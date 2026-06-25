# Visualização em Rede (kg-network.html) — Plano de Melhoria

> **Para Hermes:** Use subagent-driven-development skill para implementar este plano task-by-task.

**Objetivo:** Corrigir a visualização Cytoscape.js para ter física realista com repulsão/atração diferenciada por tipo de relação, sem sobreposição, casamento único, timeline por nascimento preservada.

**Arquitetura:** Layout híbrido — posicionamento inicial por ano de nascimento (timeline vertical) + force-directed com forças customizadas por tipo de edge (casamento=forte atração, filiação=média, irmandade=leve, não-relacionados=repulsão forte). Preservar ordem vertical por idade.

**Stack:** Cytoscape.js (CDN), layout `cose` built-in com config customizada, timeline buckets (20 anos), edge weights por relação.

---

## Tasks

### Task 1: Corrigir duplicação de edges de casamento
**Objetivo:** Garantir uma única edge `casou_com` por casal (undirected), remover duplicatas A→B e B→A.

**Arquivos:**
- Modify: `/home/hermes/genealogia/kg-network-edges.js` — regenerar edges

**Passos:**
1. Ler edges atuais, identificar pares `casou_com` duplicados
2. Regenerar `EDGES_DATA` com um único edge por casal (source/target ordenados alfabeticamente por ID)
3. Testar: `cy.edges('[type="casou_com"]').length` deve ser = número de casais únicos

### Task 2: Adicionar pesos e tipos de força aos edges
**Objetivo:** Diferenciar força de atração/repulsão por tipo de relação.

**Arquivos:**
- Modify: `/home/hermes/genealogia/kg-network-logic.js` — config de layout

**Especificação de forças:**
| Tipo | Atração (edgeElasticity) | Repulsão node-node | Comportamento |
|------|--------------------------|-------------------|---------------|
| `casou_com` | 0.05 (muito forte) | 0 (cônjuges grudados) | Mesmo Y, lado a lado |
| `pai_de`/`mae_de` | 0.2 (média) | padrão | Pais acima, filhos abaixo |
| `irmao_de` | 0.4 (leve) | padrão | Mesmo nível Y, espaçados |
| Sem edge | — | **15000-25000** | Repulsão forte entre núcleos |

**Implementação:** Usar `edgeElasticity` por seletor + `nodeRepulsion` global alta + `idealEdgeLength` por tipo.

### Task 3: Preservar timeline vertical (Y por ano nascimento) com flutuação controlada
**Objetivo:** Nós mais velhos no topo, mais novos na base; permitir pequena flutuação X para evitar sobreposição, mas manter ordem Y.

**Arquivos:**
- Modify: `/home/hermes/genealogia/kg-network-logic.js` — `runTimelineLayout()` + `runCoseLayoutRefined()`

**Abordagem:**
1. `positionByBirthYear()` — posiciona em grade Y por bucket (20 anos), X distribuído
2. `runCoseLayoutRefined()` — usa `cose` com `randomize: false`, `gravity: 0.05`, `numIter: 3000`
3. Constraint: `lockY: true` aproximado via `gravity: 0.05` + `nodeRepulsion` alta só em X

### Task 4: Anti-overlap robusto — nodeOverlap + bounding box
**Objetivo:** Zero sobreposição visual.

**Arquivos:**
- Modify: `/home/hermes/genealogia/kg-network-logic.js`

**Parâmetros:**
- `nodeOverlap: 100` (penalidade máxima)
- `idealEdgeLength: 180` (casamento), `200` (filiação), `220` (irmãos)
- `padding: 150`
- `fit: true` após layout

### Task 5: Atualizar botões de controle
**Objetivo:** UI consistente com novo layout.

**Arquivos:**
- Modify: `/home/hermes/genealogia/kg-network.html` — botões
- Modify: `/home/hermes/genealogia/kg-network-logic.js` — event listeners

**Botões:**
- 📅 **Linha do Tempo** (default, ativo)
- 🔮 **Livre** (force-directed puro)
- 🔄 **Reset zoom**
- 🎯 **Ajustar tudo**

### Task 6: Validar e commitar
**Objetivo:** Verificar funcionamento e subir.

**Comandos:**
```bash
cd /home/hermes/genealogia
# Teste sintaxe
node --check kg-network-logic.js
node --check kg-network-data.js
# Commit
git add kg-network.html kg-network-logic.js kg-network-edges.js
git commit -m "KG Network: física diferenciada por relação, casamento único, timeline preservada, zero overlap" --author="Ricardo Andrade <ricardo@feudo.org>"
git push origin main
```

---

## Verificação de Aceitação

- [ ] Abre `kg-network.html` → carrega em "Linha do Tempo"
- [ ] Nós distribuídos verticalmente por ano nascimento (1630 topo → 2020 base)
- [ ] Cônjuges lado a lado (mesmo Y, edge ∞ dourado grosso)
- [ ] Pais acima dos filhos (seta ↓ verde)
- [ ] Irmãos no mesmo nível Y aproximado
- [ ] **Zero sobreposição** de caixas (labels legíveis)
- [ ] Casamentos: **uma única edge** por casal (sem duplicata)
- [ ] Núcleos familiares separados horizontalmente (repulsão forte)
- [ ] Botão "Livre" → force-directed puro funciona
- [ ] Console: sem erros, extensões registradas
- [ ] Push feito, site atualizado