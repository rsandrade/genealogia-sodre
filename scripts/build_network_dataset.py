"""
Build /home/hermes/genealogia/data/f3_network_data.js
- Copy all 158 F3 nodes
- Add ~36 colonial/historical nodes from kg-network-data
- Renumber colonial with stable id prefixes:
    net_hist_* (historical)
    net_bar_* (barao)
    net_col_* (colonial)
- Map colonial names by normalized name to existing F3 nodes (if match, reuse F3 id)
- Establish family connections:
    - jeronimo_i net_hist_jeronimo_i -> Francisca -> Jerônimo II
    - barao -> cora (spouse), barao children (jeronimo_ii, conselheiro, jose_lino, elisa_barao)
    - coronel -> meneses (spouse)
    - manuel -> maria_gramilo (spouse), eduardo (son)
    - antonio_p -> isabel_g (spouse)
- Connect Tomaz (id=1) as POSSIBLE parent of Marcelo (id=gp1) — but keep current gp1.parent pointing to virtual_1000 to avoid breaking the F3 visible tree
- Render f3_data structure: {id, data, rels}
- colonial_nodes have parents=['virtual_root'] (so they become independent fragments at gen 0)
"""
import json
import re

def parse_dash_dates(dates_str):
    """Parse dates string '1818–1882' or '1631–1711' or '~1835' or 'bat. 1881' etc.
    Returns (birth_disp, death_disp) strings."""
    if not dates_str:
        return ('', '')
    s = dates_str.strip()
    # Try range 'YYYY–YYYY'
    m = re.match(r'(\~?)(\d{4})\s*[–\-]\s*(\~?)(\d{4})', s)
    if m:
        return (m.group(1)+m.group(2), m.group(3)+m.group(4))
    # Year only '~1835'
    m = re.match(r'(\~?\d{4})', s)
    if m:
        return (m.group(1), '')
    # 'bat. 1881'
    m = re.search(r'\b(\d{4})\b', s)
    if m:
        return (m.group(1), '')
    return ('', '')

# =================== Load F3 (base) ===================
with open('/home/hermes/genealogia/data/f3_data.js') as f:
    f3_content = f.read()

f3_start = f3_content.index('= ') + 2
depth = 0
i = f3_start
while i < len(f3_content):
    if f3_content[i] == '[': depth += 1
    elif f3_content[i] == ']':
        depth -= 1
        if depth == 0: break
    i += 1
f3_nodes = json.loads(f3_content[f3_start:i+1])
print(f'Loaded {len(f3_nodes)} F3 nodes')

# Build mapping by normalized name
def norm(s):
    s = re.sub(r'\s+', ' ', s.strip().lower())
    s = re.sub(r'[áàâã]', 'a', s)
    s = re.sub(r'[éê]', 'e', s)
    s = re.sub(r'[í]', 'i', s)
    s = re.sub(r'[óôõ]', 'o', s)
    s = re.sub(r'[ú]', 'u', s)
    s = re.sub(r'[ç]', 'c', s)
    return s

f3_by_name = {}
for n in f3_nodes:
    d = n.get('data', {})
    full = d.get('nome completo', '') or f"{d.get('first name','')} {d.get('last name','')}"
    if full.strip():
        f3_by_name[norm(full)] = n['id']

def find_f3_match(label):
    """Find F3 node by name match. Return F3 id or None."""
    return f3_by_name.get(norm(label))

# =================== Load kg-network (colonial source) ===================
with open('/home/hermes/genealogia/archive/kg-network-cytoscape-backup/kg-network-data.js') as f:
    net_content = f.read()

net_start = net_content.index('const NODES_DATA = ') + len('const NODES_DATA = ')
depth = 0
i = net_start
while i < len(net_content):
    if net_content[i] == '[': depth += 1
    elif net_content[i] == ']':
        depth -= 1
        if depth == 0: break
    i += 1
net_nodes = json.loads(net_content[net_start:i+1])
print(f'Loaded {len(net_nodes)} Network nodes')

# Load edges
net_edges_start = net_content.index('const EDGES_DATA = ') + len('const EDGES_DATA = ')
depth = 0
j = net_edges_start
while j < len(net_content):
    if net_content[j] == '[': depth += 1
    elif net_content[j] == ']':
        depth -= 1
        if depth == 0: break
    j += 1
net_edges = json.loads(net_content[net_edges_start:j+1])
print(f'Loaded {len(net_edges)} Network edges')

# =================== Build colonial nodes ===================
colonial_nodes = []
colonial_renames = {}  # old id -> new id (or f3 id if match)
f3_added = set()  # F3 nodes that will get new relations from colonial

colonials_to_add = []  # list of (orig_id, node_data)
for n in net_nodes:
    nd = n['data']
    cat = nd.get('category', '')
    if cat in ('historical', 'barao', 'colonial'):
        colonials_to_add.append(n)

# Add all colonials; remap IDs to net_* if not present in F3
def remap_colonial_id(old_id):
    """Return new id for a colonial node: original_id preserved if no F3 clash, but usually add prefix."""
    return f'net_{old_id}'

for n in colonials_to_add:
    nd = n['data']
    label = nd['label']
    cat = nd['category']
    dates_str = nd.get('dates', '')
    note = nd.get('note', '')
    generation = nd.get('generation', 0)

    # Try to match with existing F3 by name
    f3_id = find_f3_match(label)
    if f3_id:
        colonial_renames[nd['id']] = f3_id
        print(f'  MERGE: {nd["id"]} ({label}) -> F3 {f3_id}')
        continue

    new_id = remap_colonial_id(nd['id'])
    # In case of collision, suffix
    while any(node['id'] == new_id for node in f3_nodes + colonial_nodes):
        new_id = new_id + '_b'

    colonial_renames[nd['id']] = new_id

    # Parse name into first/last
    name_parts = label.split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    # Parse dates
    birth_str, death_str = parse_dash_dates(dates_str)

    node_data = {
        'first name': first_name,
        'last name': last_name,
        'gender': 'M',  # safer default — user will see note for clarification
        'nome completo': label,
        'confiabilidade': 'hipotética' if cat == 'colonial' or cat == 'historical' else 'provável',
        'categoria': cat,
        'generation': generation,
        'birthday': birth_str,
        'deathday': death_str,
        'dates_full': dates_str,
        'notas': note,
    }

    colonial_renames.get(nd['id'])

    colonial_nodes.append({
        'id': new_id,
        'data': node_data,
        'rels': {
            'parents': ['virtual_root'],
            'children': [],
            'spouses': []
        }
    })
    print(f'  ADD colonial: {new_id} ({label}) [{cat}] dates={dates_str}')

print(f'\n{len(colonial_nodes)} colonial nodes added')

# =================== Rebuild rels.parents for Marcelo to include Tomaz as additional parent? ===================
# Marcelo id=gp1 currently parents=['virtual_1000']
# Strategy: keep current structure (virtual_1000 root), but we want to connect to the new hierarchical tree.
# However we want to show Tomaz as possible father.
# Option: move Marcelo's parent from virtual_1000 to virtual_1001 (Tomaz group) -- but currently id=1 is in virtual_1001, so we can set gp1.parents = ['1'] (Tomaz)
# That breaks Marcelo's connection from virtual_1000: Marcelo would no longer be at the same root level as Antonio.
# Better: introduce an additional "virtual_1003_marcelo" or similar:
#  - Set virtual_1000 ALREADY -> Marcelo
#  - Tomaz (id=1) gets children = ['gp1']
#  - Marcelo (gp1) gets parents = ['virtual_1000', '1']  -- but we prefer single-parent

# Cleanest: keep gp1.parents virtual_1000 (as before), but also add Tomaz's children=['gp1'].
# That will give Tomaz->Marcelo link. The family-chart will draw BOTH parents leading to gp1.
# We accept this minor inconsistency for visual clarity.

# Find Marcelo and Tomaz
marcelo = next((n for n in f3_nodes if n['id'] == 'gp1'), None)
tomaz = next((n for n in f3_nodes if n['id'] == '1'), None)

if marcelo and tomaz:
    # Add gp1 as child of Tomaz, marking Tomaz as hypothetical parent
    tomaz['rels'].setdefault('children', [])
    if 'gp1' not in tomaz['rels']['children']:
        tomaz['rels']['children'].append('gp1')
        print(f'Linked Tomaz (id=1) -> Marcelo (gp1) as hypothetical parent')

# Save updated Tomaz
f3_nodes_updated = []
for n in f3_nodes:
    if n['id'] == '1':
        f3_nodes_updated.append(tomaz)
    else:
        f3_nodes_updated.append(n)

# =================== Add colonial-to-colonial relations based on kg-network edges ===================
# Build colonial rels from EDGES_DATA where both endpoints are colonial (or remap)
# Build by-id dict
colonial_by_new_id = {n['id']: n for n in colonial_nodes}

# Collect edges where source/target are colonial/historical/barao
colonial_ids_orig = set()
for n in colonials_to_add:
    colonial_ids_orig.add(n['data']['id'])

colonial_rels_added = 0

for e in net_edges:
    ed = e['data']
    src_orig = ed['source']
    tgt_orig = ed['target']
    rel_type = ed['type']

    if src_orig in colonial_ids_orig or tgt_orig in colonial_ids_orig:
        src_new = colonial_renames.get(src_orig)
        tgt_new = colonial_renames.get(tgt_orig)
        if not src_new or not tgt_new:
            continue

        if src_orig in colonial_ids_orig:
            src_node = colonial_by_new_id.get(src_new)
        else:
            # Could be F3 (e.g. some edge connecting jeronimo_auto to net_)
            # Probably not relevant for now
            continue

        if tgt_orig in colonial_ids_orig:
            tgt_node = colonial_by_new_id.get(tgt_new)
        else:
            continue

        if not src_node or not tgt_node:
            continue

        if rel_type in ('pai_de', 'mae_de'):
            src_node['rels'].setdefault('children', [])
            if tgt_new not in src_node['rels']['children']:
                src_node['rels']['children'].append(tgt_new)
                # Update tgt's parents: replace virtual_root with src_new
                if 'virtual_root' in tgt_node['rels'].get('parents', []):
                    tgt_node['rels']['parents'] = [src_new]
                colonial_rels_added += 1
        elif rel_type == 'casou_com':
            src_node['rels'].setdefault('spouses', [])
            tgt_node['rels'].setdefault('spouses', [])
            if tgt_new not in src_node['rels']['spouses']:
                src_node['rels']['spouses'].append(tgt_new)
                if src_new not in tgt_node['rels']['spouses']:
                    tgt_node['rels']['spouses'].append(src_new)
                colonial_rels_added += 1

print(f'Added {colonial_rels_added} colonial-to-colonial relations')

# =================== Merge final dataset ===================
final_nodes = f3_nodes_updated + colonial_nodes

# Ensure virtual_root remains (from F3) and has all colonial nodes as children IN ADDITION
virtual_root = next((n for n in final_nodes if n['id'] == 'virtual_root'), None)
if virtual_root:
    current_children = set(virtual_root.get('rels', {}).get('children', []))
    for n in colonial_nodes:
        if n['id'] not in current_children:
            virtual_root['rels'].setdefault('children', [])
            if n['id'] not in virtual_root['rels']['children']:
                virtual_root['rels']['children'].append(n['id'])

# =================== Sanity check ===================
print(f'\n=== Final dataset ===')
print(f'Total nodes: {len(final_nodes)}')
# Count by category
from collections import Counter
cats = Counter()
for n in final_nodes:
    d = n.get('data', {})
    cat = d.get('categoria', d.get('confiabilidade', '?'))
    cats[cat] += 1
for k, v in cats.most_common():
    print(f'  {k}: {v}')

# Count roots (parents = ['virtual_root'])
rooted = []
for n in final_nodes:
    if 'virtual_root' in n.get('rels', {}).get('parents', []):
        rooted.append(n['id'])
print(f'\nFragments (children of virtual_root): {len(rooted)}')

# =================== Write file ===================
output_path = '/home/hermes/genealogia/data/f3_network_data.js'
with open(output_path, 'w') as f:
    f.write('// Auto-merged dataset: 158 F3 + ~36 colonial nodes from kg-network (Cytoscape Rede)\n')
    f.write('// Generated by build_network_dataset.py — do not edit by hand\n')
    f.write('const F3_NETWORK_DATA = ')
    json.dump(final_nodes, f, ensure_ascii=False, indent=2)
    f.write(';\n')

print(f'\nWritten to {output_path}')
print(f'Size: {len(json.dumps(final_nodes, ensure_ascii=False))} bytes')
