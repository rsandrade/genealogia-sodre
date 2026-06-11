# Pesquisa Profunda FamilySearch — Família Gramilo Sodré

> **For Hermes:** Usar subagent-driven-development para executar as tarefas após aprovação do Ricardo.

**Objetivo:** Preencher as 3 maiores lacunas da árvore genealógica usando dados do FamilySearch

**Arquitetura:** Script Python (Selenium/undetected-chromedriver) faz login com token de sessão fornecido pelo usuário, executa buscas direcionadas e extrai innerText estruturado. Resultados são gravados em JSON, analisados manualmente e só depois incluídos na árvore.

**Stack:** Python 3, undetected-chromedriver, Xvfb, FamilySearch record search

---

## Lacunas a preencher

### L1. Buraco ~200 anos (Jerônimo → Tomaz)
- Jerônimo Sodré Pereira: séc. XVII, Portugal → Bahia
- Tomaz Gramilo Sodré: casamento ~1891, Amargosa/BA
- **Hipótese:** gerações intermediárias podem estar em registros paroquiais de Salvador, Cachoeira, São Félix, Amargosa
- **Buscas necessárias:** Sodré em batismos/casamentos Bahia 1700-1890; variação "Sodré Pereira"

### L2. Dados biográficos faltantes
- Tomaz Gramilo Sodré: sem nascimento, óbito, localidade
- Teodora Julia da Cruz: sem dados
- Marcelo Gramilo Sodré: nasceu em Montes Claros/MG, resto desconhecido
- Rita Rosa Sodré ("Roxa"): sem dados
- Francisco Gramilo Sodré: sem data nasc/óbito
- Atanagilda Odete dos Santos: sem data nasc/óbito
- 12 filhos: datas de nascimento OK (memória oral), faltam óbito, casamento, cônjuges

### L3. Origem do sobrenome "Gramilo Sodré"
- Quando Gramilo + Sodré se juntaram?
- "Gramilo" é sobrenome ou apelido que virou sobrenome?
- Existe registro de casamento ou batismo com "Gramilo" em Amargosa/BA antes de Tomaz?

---

## Pré-requisitos

- [ ] Token de sessão do FamilySearch (Ricardo fornece após login manual)
- [ ] Verificar se o script v11 ainda funciona com o token

---

## Tarefas

### Task 1: Preparar script de coleta v12 com token de sessão

**Objetivo:** Adaptar o `fs_search_v11.py` para aceitar token/sessão via cookie em vez de login por senha

**Arquivos:**
- Criar: `scripts/fs_search_v12_session.py`
- Referência: `fs_search_v11.py` (modelo funcional)

**Passo 1:** Criar script que aceita cookie `fssession` ou `fs-token` como argumento

```python
#!/usr/bin/env python3
"""
FamilySearch buscas v12 — Login via token de sessão (cookie).
Uso: python fs_search_v12_session.py FS_SESSION_TOKEN
"""
import subprocess, time, json, sys, os

if len(sys.argv) < 2:
    print("Uso: python fs_search_v12_session.py FS_SESSION_TOKEN")
    sys.exit(1)

FS_TOKEN = sys.argv[1]

os.environ['DISPLAY'] = ':99'
os.system('rm -f /tmp/.X99-lock')
xvfb = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'])
time.sleep(2)

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

driver = uc.Chrome(options=options, version_main=149)
wait = WebDriverWait(driver, 30)

try:
    # Navegar ao FS e injetar cookie de sessão
    driver.get('https://www.familysearch.org/en/')
    time.sleep(5)
    
    # Adicionar cookie de sessão
    driver.add_cookie({
        'name': 'fssession',
        'value': FS_TOKEN,
        'domain': '.familysearch.org',
        'path': '/',
        'secure': True
    })
    
    # Recarregar para aplicar sessão
    driver.get('https://www.familysearch.org/en/')
    time.sleep(10)
    
    # Verificar se está logado
    body = driver.execute_script("return document.body.innerText") or ""
    logged_in = 'sign out' in body.lower() or 'sair' in body.lower()
    print(f"Logado via cookie: {logged_in}")
    
    if not logged_in:
        print("Cookie não funcionou. Tentando via localStorage...")
        driver.execute_script(f"""
        localStorage.setItem('fs-token', '{FS_TOKEN}');
        """)
        driver.get('https://www.familysearch.org/en/')
        time.sleep(10)
        body = driver.execute_script("return document.body.innerText") or ""
        logged_in = 'sign out' in body.lower() or 'sair' in body.lower()
        print(f"Logado via localStorage: {logged_in}")
    
    # ... buscas (Task 2)
```

**Passo 2:** Testar com token fornecido

**Verificação:** Script imprime "Logado via cookie: True" e coleta dados de pelo menos 1 busca

---

### Task 2: Expandir buscas — 30 queries direcionadas

**Objetivo:** Executar buscas específicas para as 3 lacunas

**Arquivo:** `scripts/fs_search_v12_session.py` (continuação do Task 1)

**Buscas organizadas por lacuna:**

#### L1 — Buraco ~200 anos (Jerônimo → Tomaz)
```python
('L1a_SodrePereira_Bahia_1700_1850',
 'q.surname=Sodre+Pereira&q.birthLikePlace=Bahia&q.birthLikeDate.from=1700&q.birthLikeDate.to=1850&count=40'),
('L1b_Sodre_Salvador_baptism',
 'q.surname=Sodre&q.birthLikePlace=Salvador&q.birthLikeDate.from=1700&q.birthLikeDate.to=1900&count=40'),
('L1c_Sodre_Cachoeira',
 'q.surname=Sodre&q.birthLikePlace=Cachoeira&count=40'),
('L1d_Sodre_SaoFelix',
 'q.surname=Sodre&q.birthLikePlace=Sao+Felix&count=40'),
('L1e_Gramilo_Bahia_all',
 'q.surname=Gramilo&q.birthLikePlace=Bahia&count=40'),
('L1f_Gramilo_all_Brazil',
 'q.surname=Gramilo&count=40'),
('L1g_Tomaz_Sodre_Amargosa',
 'q.givenName=Tomaz&q.surname=Sodre&q.birthLikePlace=Amargosa&count=40'),
('L1h_Thomas_Sodre_Bahia',
 'q.givenName=Thomas&q.surname=Sodre&q.birthLikePlace=Bahia&count=40'),
('L1i_SodrePereira_marry_Bahia',
 'q.surname=Sodre+Pereira&q.marriageLikePlace=Bahia&count=40'),
('L1j_Sodre_Amargosa_before1900',
 'q.surname=Sodre&q.birthLikePlace=Amargosa&q.birthLikeDate.to=1900&count=40'),
```

#### L2 — Dados biográficos faltantes
```python
('L2a_Marcelo_Gramilo_MontesClaros',
 'q.givenName=Marcelo&q.surname=Gramilo&q.birthLikePlace=Montes+Claros&count=40'),
('L2b_Marcelo_Gramilo_Bahia',
 'q.givenName=Marcelo&q.surname=Gramilo&q.birthLikePlace=Bahia&count=40'),
('L2c_Marcelo_Sodre_Bahia',
 'q.givenName=Marcelo&q.surname=Sodre&q.birthLikePlace=Bahia&count=40'),
('L2d_Teodora_Cruz_Amargosa',
 'q.givenName=Teodora&q.surname=Cruz&q.birthLikePlace=Amargosa&count=40'),
('L2e_Teodora_Julia_Bahia',
 'q.givenName=Teodora+Julia&q.birthLikePlace=Bahia&count=40'),
('L2f_Francisco_Gramilo_birth',
 'q.givenName=Francisco&q.surname=Gramilo+Sodre&f.collectionId=324815&count=40'),
('L2g_Atanagilda_Santos_Amargosa',
 'q.givenName=Atanagilda&q.surname=Santos&q.birthLikePlace=Amargosa&count=40'),
('L2h_Atanagilda_Santos_Ibicui',
 'q.givenName=Atanagilda&q.surname=Santos&q.birthLikePlace=Ibicui&count=40'),
('L2i_Rita_Rosa_Sodre',
 'q.givenName=Rita&q.surname=Sodre&q.birthLikePlace=Bahia&count=40'),
('L2j_Gervasio_Eusebio_Santos',
 'q.givenName=Gervasio&q.surname=Santos&q.birthLikePlace=Bahia&count=40'),
```

#### L3 — Origem "Gramilo Sodré"
```python
('L3a_Gramilo_Sodre_Amargosa_all',
 'q.surname=Gramilo+Sodre&q.birthLikePlace=Amargosa&count=40'),
('L3b_Gramilo_casamento_Bahia',
 'q.surname=Gramilo&q.marriageLikePlace=Bahia&count=40'),
('L3c_Gramilo_baptism_Bahia',
 'q.surname=Gramilo&q.birthLikePlace=Bahia&f.collectionId=324815&count=40'),
('L3d_Gramilo_MG_all',
 'q.surname=Gramilo&q.birthLikePlace=Minas+Gerais&count=40'),
('L3e_Tomaz_Gramilo_casamento',
 'q.givenName=Tomaz&q.surname=Gramilo&q.marriageLikePlace=Bahia&count=40'),
('L3f_Gramilo_Sodre_death_Amargosa',
 'q.surname=Gramilo+Sodre&q.deathLikePlace=Amargosa&count=40'),
('L3g_Gramilo_Sodre_Jequie',
 'q.surname=Gramilo+Sodre&q.birthLikePlace=Jequie&count=20'),
```

#### Reforço — mais Sodré na região
```python
('R1_VazSodre_Amargosa_deep',
 'q.surname=Vaz+Sodre&q.birthLikePlace=Amargosa&count=40'),
('R2_Sodre_coleta324815',
 'q.surname=Sodre&f.collectionId=324815&count=40'),
('R3_Esmeraldo_Sodre_deep',
 'q.givenName=Esmeraldo&q.surname=Sodre&f.collectionId=324815&count=40'),
('R4_Luiz_VazSodre_deep',
 'q.givenName=Luiz&q.surname=Vaz+Sodre&count=40'),
('R5_Francisco_Ludgero_deep',
 'q.givenName=Francisco+Ludgero&q.surname=Sodre&count=40'),
('R6_Sodre_Ibitupa',
 'q.surname=Sodre&q.birthLikePlace=Ibitupa&count=20'),
```

**Verificação:** JSON de saída com pelo menos 30 entradas de busca

---

### Task 3: Analisar resultados e categorizar

**Objetivo:** Processar o JSON bruto em dados estruturados por lacuna

**Arquivo:**
- Criar: `scripts/fs_analyze_results.py`
- Ler: `data/fs_v12_all_data.json`

**Passo 1:** Parsear innerText de cada busca, extrair:
- Nome completo
- Tipo de evento (nascimento/batismo/casamento/óbito)
- Data
- Localidade
- Pais
- Cônjuge
- Filhos
- Fonte/coleção
- ARK (identificador permanente)

**Passo 2:** Categorizar por relevância:
- **A — Direto:** Pessoa já na árvore, dados novos
- **B — Conexão provável:** Parentes prováveis (mesmo ramo, localidade, período)
- **C — Contexto:** Outros Sodré/Gramilo na região (útil para mapear o ramo)
- **D — Irrelevante:** Sem conexão com a família

**Passo 3:** Gerar relatório: `data/fs_v12_analise.md`

**Verificação:** Relatório com pelo menos 10 pessoas categorizadas A ou B

---

### Task 4: Busca por árvore genealógica (FamilySearch Tree)

**Objetivo:** Consultar a Árvore Genealógica do FamilySearch (não só registros) para encontrar conexões genealógicas já feitas por outros pesquisadores

**Arquivo:** `scripts/fs_search_v12_session.py` (seção adicional)

**Buscas na árvore:**
```
https://www.familysearch.org/search/record/results?q.surname=Gramilo+Sodre&f.collectionId=2
https://www.familysearch.org/tree/find?q.surname=Gramilo+Sodre
```

**Verificação:** Ver se existem perfis de árvore para Tomaz, Marcelo, Francisco

---

### Task 5: Compilar relatório de descobertas

**Objetivo:** Relatório final consolidado para aprovação do Ricardo antes de incluir na árvore HTML

**Arquivo:** `docs/fs_v12_relatorio_descobertas.md`

**Conteúdo:**
- Resumo por lacuna (L1, L2, L3)
- Novas pessoas descobertas
- Novos dados para pessoas existentes
- Conexões genealógicas propostas
- Fontes com ARK
- Recomendações do que incluir na árvore

**Verificação:** Ricardo aprova as inclusões

---

## Decisões necessárias do usuário

1. **Token de sessão FS:** Como obter?
   - Opção A: Ricardo faz login no browser, copia cookie `fssession` via DevTools
   - Opção B: Ricardo faz login no browser, copia o valor de `fs-token` do localStorage
   - Opção C: Ricardo fornece credenciais atualizadas (senha pode ter mudado)

2. **Prioridade:** Qual lacuna atacar primeiro?
   - L1 (buraco 200 anos) — mais difícil, provavelmente sem resultado direto
   - L2 (dados biográficos) — mais provável de encontrar resultados
   - L3 (origem Gramilo) — intermediário

3. **Inclusão na árvore:** Só incluir dados confirmados por registro primário, ou incluir "provável" com badge?

---

## Riscos

| Risco | Probabilidade | Mitigação |
|-------|---------------|-----------|
| Token de sessão expira rápido | Alta | Executar buscas em 1 sessão, sem pausas longas |
| FS bloqueia scraping | Média | undetected-chromedriver + delays randomizados |
| Registros L1 (1700-1850) não digitalizados | Alta | Focar no que existe; documentar ausência |
| Cookie injection não funciona | Média | Fallback para login com credenciais atualizadas |
| Muitos resultados irrelevantes | Média | Filtrar por localidade + período + palavras-chave |

---

## Cronograma estimado

| Task | Tempo | Dependência |
|------|-------|-------------|
| Task 1 | 15 min | Token FS |
| Task 2 | 20 min | Task 1 |
| Task 3 | 15 min | Task 2 |
| Task 4 | 10 min | Task 1 |
| Task 5 | 15 min | Task 3 + Task 4 |

**Total:** ~75 min após receber o token
