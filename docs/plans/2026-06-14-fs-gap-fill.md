# Plano: Preencher Gaps Genealógicos via FamilySearch + Fontes Complementares

> **Para Hermes:** Executar via delegate_task em paralelo.

**Objetivo:** Preencher lacunas na árvore Gramilo Sodré buscando dados no FamilySearch e fontes complementares.

**Metodologia:** Seguir a skill `familysearch-data-collection` — analisar dados existentes PRIMEIRO, depois rodar script UC se necessário.

---

## Fase 1: Extrair dados JÁ EXISTENTES (sem novo script FS)

Os dados `fs_endpoint_structured.json` e `fs_v17_data.json` têm 6.956 resultados para "Sodré Amargosa" mas só extraímos 80 entradas. Extrair:

1. Todas as pessoas Sodré em Amargosa com datas/nascimento/casamento/óbito
2. Especificamente: Tomaz/Tomé Sodré, Gervásio Eusébio, Teodoria/Teodora, Horácio Vaz Sodré
3. Casamentos Sodré em Amargosa 1890-1930
4. Qualquer Esmeraldo Vaz Sodré com mais detalhes

## Fase 2: Buscas complementares (web, antes de FS UC)

1. "Esmeraldo Vaz Sodré" Bahia genealogia
2. "Firmino Vaz Sodré" Amargosa
3. "Manoel Caetano Sodré" Amargosa
4. "Tomaz Gramilo Sodré" casamento
5. "Gervásio Eusébio dos Santos" Amargosa

## Fase 3: Novas buscas FS (UC script)

Queries faltantes (não cobertas pelos dados existentes):
1. Esmeraldo Vaz Sodré (nascimento, casamento)
2. Manoel Caetano Sodré (nascimento, casamento)
3. Florinda de Andrade (casamento com Esmeraldo)
4. Antonio Victor Sodré (pai de Eufrásio)
5. Sodré casamento Amargosa 1890-1920 (batch)
6. Sodré Jequié (cidade próxima)
7. Sodré Ipiaú / Jitaúna (cidades próximas)

## Fase 4: Buscar transcrições e imagens

Para cada pessoa encontrada, verificar se há ARK links com imagens e transcrições disponíveis.