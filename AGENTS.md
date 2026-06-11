# AGENTS.md — Genealogia Sodré

## Visão geral

Este repositório contém pesquisa genealógica da família Gramilo Sodré de Aiquara, Bahia. O foco principal é reconstruir a árvore genealógica a partir de **Francisco Gramilo Sodré** e **Atanagilda Odete dos Santos**, remontando ao patriarca **Tomaz Gramilo Sodré** (Amargosa, ~1891) e, se possível, ao tronco baiano de **Jerônimo Sodré Pereira** (séc. XVIII).

## Convenções

- **Idioma:** Português do Brasil em todos os arquivos
- **Datas:** Formato DD/MM/AAAA quando confirmadas; ~AAAA quando aproximadas
- **Nomes:** Manter grafia original (Sodré, não Sudré) — "Sudré" é erro cartorário conhecido
- **Localidades:** Município/UF (ex: Aiquara/BA)
- **Fontes:** Toda informação genealógica deve citar a fonte

## Fontes primárias (prioridade)

1. **FamilySearch** — Coleção 324815 (Amargosa, 1856–1915): batismos, casamentos, óbitos
2. **APEB** — Inventários do Juizado de Órfãos, comarca de Amargosa
3. **Cartórios** — Aiquara (certidões civis), Ibicuí, Amargosa

## Fontes secundárias

- Parentesco.com.br (ensaio SODRE2.pdf)
- MyHeritage (árvore pública Família Sodré)
- TJBA (processos judiciais)
- Diário Oficial do Município de Aiquara

## Estrutura de dados

Os membros da família são registrados em `data/membros_encontrados.json` com:
- `nome_completo`: Nome completo
- `nascimento`: Data/local (se conhecido)
- `falecimento`: Data/local (se conhecido)
- `pais`: Nomes dos pais (se conhecido)
- `conjuge`: Cônjuge (se conhecido)
- `fonte`: URL ou referência da informação
- `confiabilidade`: "confirmada" | "provável" | "hipotética"

## Scripts
## Scripts
- `scripts/fs_login_api.py` — Login via API REST ❌ (bloqueado pelo Incapsula WAF)
- `scripts/fs_uc_login_v3.py` — Login via UC ❌ (Incapsula detecta headless)
- `scripts/fs_search_v12_hybrid.py` — Híbrido Selenium→requests ⚠️ (funciona parcialmente; cookies expiram rápido)

## ⚠️ Pendências
- FamilySearch: login automatizado bloqueado pelo Imperva/Incapsula WAF. Usar cookie manual ou buscas manuais — ver skill `familysearch-data-collection`
- APEB: catálogo AtoM indisponível remotamente; consultar presencialmente
- MyHeritage: site com timeout; requer acesso manual
