#!/usr/bin/env python3
"""
Gera F3_DATA para family-chart a partir de membros_encontrados.json.

Estratégia:
1. Ler membros_encontrados.json
2. Resolver referências de pais/cônjuges por nome → ID
3. Criar nós placeholder para pessoas referenciadas mas não presentes
4. Adicionar uma "raiz virtual" que conecta todos os fragmentos de árvore
   na mesma geração, garantindo alinhamento horizontal correto.
5. Gerar o array JS com nome completo para melhor exibição
"""
import json
import re
import sys

DATA_FILE = "data/membros_encontrados.json"
OUTPUT_FILE = "data/f3_data.js"

def main():
    with open(DATA_FILE) as f:
        membros = json.load(f)

    # Map nome_completo → membro
    name_to_membro = {}
    id_to_membro = {}
    for m in membros:
        nome = m.get("nome_completo", "")
        mid = m.get("id", "")
        if nome:
            name_to_membro[nome] = m
        if mid:
            id_to_membro[mid] = m

    # Auto-increment for placeholders
    auto_id = 1

    # Placeholder tracker: nome → id_already_created
    placeholder_cache = {}

    def get_or_create_placeholder(nome):
        nonlocal auto_id
        if nome in placeholder_cache:
            return placeholder_cache[nome]
        # Check if already exists as a real member
        if nome in name_to_membro:
            return name_to_membro[nome].get("id", "")
        pid = f"auto_{auto_id}"
        auto_id += 1
        placeholder_cache[nome] = pid
        return pid

    # Build F3 data entries
    f3_entries = {}
    # First pass: create entries for all real members
    for m in membros:
        mid = m.get("id")
        if not mid:
            continue
        nome = m.get("nome_completo", "")
        # Determine gender
        # Use existing gender if available, otherwise infer from name patterns
        gender = m.get("genero", "")
        if not gender:
            # Common male/female name patterns in Portuguese
            female_endings = ["a", "e", "idade", "triz"]
            if nome and nome[-1] == "a" and not nome.endswith(("Sodré", "Sodré", "Andrade")):
                gender = "F"
            else:
                gender = "M"
        
        # Build data fields
        data = {
            "first name": nome.split()[0] if nome else "",
            "last name": " ".join(nome.split()[1:]) if len(nome.split()) > 1 else "",
            "gender": gender,
            "nome completo": nome,
        }
        
        # Add birthday
        nascimento = m.get("nascimento", "")
        if nascimento:
            # Extract year if possible
            year_match = re.search(r'(\d{4})', nascimento)
            if year_match:
                data["birthday"] = year_match.group(1)
        
        # Add confiabilidade
        conf = m.get("confiabilidade", "")
        if conf:
            data["confiabilidade"] = conf
        
        # Add notas  
        notas = m.get("notas", "")
        if notas:
            data["notas"] = notas

        entry = {
            "id": mid,
            "data": data,
            "rels": {}
        }
        f3_entries[mid] = entry

    # Second pass: resolve relationships
    for m in membros:
        mid = m.get("id")
        if not mid:
            continue
        entry = f3_entries[mid]
        
        # Pais (by name)
        pais_names = m.get("pais", [])
        if pais_names:
            parent_ids = []
            for pnome in pais_names:
                if pnome and pnome in name_to_membro:
                    pid = name_to_membro[pnome].get("id")
                    if pid:
                        parent_ids.append(pid)
                elif pnome:
                    # Create placeholder
                    pid = get_or_create_placeholder(pnome)
                    parent_ids.append(pid)
            if parent_ids:
                entry["rels"]["parents"] = parent_ids

        # Cônjuge (by name)
        conjuge_names = m.get("conjuge", [])
        if isinstance(conjuge_names, str):
            conjuge_names = [conjuge_names]
        if conjuge_names:
            spouse_ids = []
            for cnome in conjuge_names:
                if cnome and cnome in name_to_membro:
                    cid = name_to_membro[cnome].get("id")
                    if cid:
                        spouse_ids.append(cid)
                elif cnome:
                    cid = get_or_create_placeholder(cnome)
                    spouse_ids.append(cid)
            if spouse_ids:
                entry["rels"]["spouses"] = spouse_ids

    # Third pass: add children relationships (derived from parents)
    children_map = {}  # parent_id → [child_id]
    for mid, entry in f3_entries.items():
        parents = entry["rels"].get("parents", [])
        for pid in parents:
            if pid not in children_map:
                children_map[pid] = []
            if mid not in children_map[pid]:
                children_map[pid].append(mid)

    for pid, children in children_map.items():
        if pid in f3_entries:
            existing = f3_entries[pid]["rels"].get("children", [])
            merged = list(dict.fromkeys(existing + children))
            f3_entries[pid]["rels"]["children"] = merged

    # Fourth pass: create placeholder entries
    for nome, pid in placeholder_cache.items():
        if pid not in f3_entries:
            # Infer gender
            gender = "F" if nome and nome[-1] == "a" and not nome.endswith(("Sodré", "Andrade")) else "M"
            entry = {
                "id": pid,
                "data": {
                    "first name": nome.split()[0] if nome else "",
                    "last name": " ".join(nome.split()[1:]) if len(nome.split()) > 1 else "",
                    "gender": gender,
                    "nome completo": nome,
                    "confiabilidade": "hipotética",
                },
                "rels": {}
            }
            # Add children if any
            if pid in children_map:
                entry["rels"]["children"] = children_map[pid]
            f3_entries[pid] = entry

    # Fifth pass: add spouse cross-references
    # If A has spouse B, then B should have spouse A
    for mid, entry in f3_entries.items():
        spouses = entry["rels"].get("spouses", [])
        for sid in spouses:
            if sid in f3_entries:
                target_spouses = f3_entries[sid]["rels"].get("spouses", [])
                if mid not in target_spouses:
                    target_spouses.append(mid)
                    f3_entries[sid]["rels"]["spouses"] = target_spouses

    # === COMPUTE GENERATIONS ===
    # BFS from roots (no parents) to assign generation levels
    # Use the geracao field from membros if available, otherwise compute
    
    # First, use geracao from membros_encontrados.json
    geracao_map = {}
    for m in membros:
        mid = m.get("id")
        gen = m.get("geracao", 0)
        if mid and gen:
            geracao_map[mid] = gen

    # Compute generations for nodes not yet assigned
    # Build adjacency
    dmap = f3_entries
    
    def find_roots():
        """Find nodes with no parents in the dataset"""
        roots = []
        for mid, entry in dmap.items():
            parents = entry["rels"].get("parents", [])
            has_parent_in_data = any(p in dmap for p in parents)
            if not has_parent_in_data:
                roots.append(mid)
        return roots

    # Use BFS to compute relative generations
    # Start from roots assigned geracao=1 (or their known geracao)
    visited = set()
    computed_gen = {}
    queue = []
    
    roots = find_roots()
    
    # Assign initial generations to roots
    # Use known geracao if available, otherwise 1
    for rid in roots:
        if rid in geracao_map and geracao_map[rid] > 0:
            computed_gen[rid] = geracao_map[rid]
        else:
            computed_gen[rid] = 1
        queue.append(rid)
    
    # BFS
    while queue:
        nid = queue.pop(0)
        if nid in visited:
            continue
        visited.add(nid)
        
        gen = computed_gen.get(nid, 1)
        entry = dmap.get(nid)
        if not entry:
            continue
        
        # Spouses are same generation
        for sid in entry["rels"].get("spouses", []):
            if sid not in computed_gen or computed_gen[sid] > gen:
                computed_gen[sid] = gen
                if sid not in visited:
                    queue.append(sid)
        
        # Children = gen + 1
        for cid in entry["rels"].get("children", []):
            if cid not in computed_gen or computed_gen[cid] < gen + 1:
                computed_gen[cid] = gen + 1
                if cid not in visited:
                    queue.append(cid)
        
        # Parents = gen - 1 (shouldn't happen much since we started from roots)
        for pid in entry["rels"].get("parents", []):
            if pid in dmap:
                if pid not in computed_gen or computed_gen[pid] > gen - 1:
                    computed_gen[pid] = gen - 1
                    if pid not in visited:
                        queue.append(pid)

    # Handle any unassigned nodes
    for mid in dmap:
        if mid not in computed_gen:
            computed_gen[mid] = 0

    # === CREATE VIRTUAL ROOT ===
    # Find the minimum generation across all nodes
    min_gen = min(computed_gen.values()) if computed_gen else 1
    
    # Adjust all generations so min = 1
    for mid in computed_gen:
        computed_gen[mid] = computed_gen[mid] - min_gen + 1
    
    # Group roots by generation
    gen_groups = {}
    for mid, gen in computed_gen.items():
        if mid not in gen_groups.get(gen, []):
            gen_groups.setdefault(gen, []).append(mid)
    
    # Create virtual root nodes at generation 0 that connect the fragment roots
    # This ensures disconnected fragments are aligned at the same horizontal level
    virtual_id_counter = [1000]
    
    def make_virtual_id():
        vid = f"virtual_{virtual_id_counter[0]}"
        virtual_id_counter[0] += 1
        return vid

    # Find the root generation (earliest generation that has multiple fragments)
    # We need to find which generation each group of roots belongs to
    # and connect them through virtual parents at gen-1
    
    # Get all root nodes (no parents in data)
    root_nodes = find_roots()
    
    # Group roots by their generation
    root_by_gen = {}
    for rid in root_nodes:
        gen = computed_gen.get(rid, 1)
        root_by_gen.setdefault(gen, []).append(rid)
    
    # Create virtual parent nodes to connect roots at the same generation
    # This makes family-chart display them as siblings (same horizontal level)
    # We only connect roots that are at the same generation level
    
    virtual_entries = []
    
    # For each group of roots at the same generation, create a virtual parent
    # if there are 2+ roots at that level
    for gen in sorted(root_by_gen.keys()):
        roots_at_gen = root_by_gen[gen]
        if len(roots_at_gen) >= 2:
            # Create a virtual parent at gen-1
            vparent_id = make_virtual_id()
            vparent_entry = {
                "id": vparent_id,
                "data": {
                    "first name": "",
                    "last name": "",
                    "gender": "M",
                    "nome completo": "",
                    "confiabilidade": "virtual",
                },
                "rels": {
                    "children": roots_at_gen[:]
                }
            }
            virtual_entries.append(vparent_entry)
            f3_entries[vparent_id] = vparent_entry
            
            # Update children's parent refs
            for rid in roots_at_gen:
                if "parents" not in f3_entries[rid]["rels"]:
                    f3_entries[rid]["rels"]["parents"] = []
                if vparent_id not in f3_entries[rid]["rels"]["parents"]:
                    f3_entries[rid]["rels"]["parents"].append(vparent_id)
            
            # Connect this virtual parent upward if there are multiple virtual parents
            # Chain virtual parents together
    
    # If we have multiple virtual parents, chain them with a super-root
    if len(virtual_entries) > 1:
        # Create super-root
        super_id = "virtual_root"
        super_entry = {
            "id": super_id,
            "data": {
                "first name": "",
                "last name": "",
                "gender": "M",
                "nome completo": "",
                "confiabilidade": "virtual",
            },
            "rels": {
                "children": [ve["id"] for ve in virtual_entries]
            }
        }
        f3_entries[super_id] = super_entry
        
        for ve in virtual_entries:
            if "parents" not in ve["rels"]:
                ve["rels"]["parents"] = []
            ve["rels"]["parents"].append(super_id)
        
        main_id = super_id
    elif len(virtual_entries) == 1:
        main_id = virtual_entries[0]["id"]
    else:
        # Single connected component — find the deepest root
        # Prefer Marcelo as main
        if "gp1" in f3_entries:
            main_id = "gp1"
        else:
            main_id = root_nodes[0] if root_nodes else "1"

    # Generate JS output
    entries_list = list(f3_entries.values())
    
    # Sort: virtual entries last, real entries sorted by generation then name
    def sort_key(e):
        gen = computed_gen.get(e["id"], 99)
        is_virtual = 1 if e["data"].get("confiabilidade") == "virtual" else 0
        nome = e["data"].get("nome completo", "")
        return (is_virtual, gen, nome)
    
    entries_list.sort(key=sort_key)
    
    # Generate JS code
    js_lines = []
    js_lines.append("// Auto-generated from data/membros_encontrados.json")
    js_lines.append(f"// Total: {len(entries_list)} entries, mainId: {main_id}")
    js_lines.append("const F3_DATA = [")
    
    for i, entry in enumerate(entries_list):
        js_entry = json.dumps(entry, ensure_ascii=False, indent=4)
        comma = "," if i < len(entries_list) - 1 else ""
        js_lines.append(js_entry + comma)
    
    js_lines.append("];")
    js_lines.append(f"\nconst F3_MAIN_ID = '{main_id}';")
    
    output = "\n".join(js_lines)
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    
    print(f"Generated {OUTPUT_FILE}: {len(entries_list)} entries")
    print(f"Main ID: {main_id}")
    print(f"Virtual entries: {len(virtual_entries)}")
    
    # Stats
    real_count = sum(1 for e in entries_list if e["data"].get("confiabilidade") != "virtual")
    virtual_count = sum(1 for e in entries_list if e["data"].get("confiabilidade") == "virtual")
    placeholder_count = sum(1 for e in entries_list if e["id"].startswith("auto_"))
    print(f"Real members: {real_count}")
    print(f"Placeholders (parents/spouses not in dataset): {placeholder_count}")
    print(f"Virtual connector nodes: {virtual_count}")
    
    # Generation stats
    gen_stats = {}
    for mid, gen in computed_gen.items():
        gen_stats.setdefault(gen, 0)
        gen_stats[gen] += 1
    print(f"\nGenerations:")
    for g in sorted(gen_stats.keys()):
        print(f"  Gen {g}: {gen_stats[g]} nodes")

if __name__ == "__main__":
    main()
