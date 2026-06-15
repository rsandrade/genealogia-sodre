#!/usr/bin/env python3
"""
Buscar casamento de Tomaz × Teodora nos filmes de Amargosa (período 1886-1900).
Usa login UC + fetch() ao endpoint JSON v2 (método comprovado).
Também navega o Film Viewer para buscar nos índices das páginas.
"""
import json, time, random, subprocess, os, sys
from pathlib import Path

DATA_DIR = '/home/hermes/genealogia/data'
ENV_PATH = '/home/hermes/genealogia/.env'
OUTPUT = f'{DATA_DIR}/fs_marriage_search_results.json'

# Xvfb
os.system('pkill -9 -f Xvfb 2>/dev/null; rm -f /tmp/.X99-lock')
time.sleep(1)
xvfb = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
os.environ['DISPLAY'] = ':99'

# Credenciais
with open(ENV_PATH) as f:
    creds = {}
    for line in f.read().strip().split('\n'):
        if '=' in line:
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip()

FS_USER = creds.get('FS_USER', '') or creds.get('TK_USERNAME', '')
FS_PASS = creds.get('FS_PASS', '') or creds.get('TK_PASSWORD', '')

if not FS_USER or not FS_PASS:
    print("❌ Credenciais não encontradas no .env")
    sys.exit(1)

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('--lang=pt-BR,pt')

driver = uc.Chrome(options=options, version_main=149)
wait = WebDriverWait(driver, 30)

# === LOGIN ===
print("🔐 Login no FamilySearch...")
driver.get('https://www.familysearch.org/pt/')
time.sleep(8)

# Clicar em Entrar
for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
    try:
        txt = (el.text or '').lower()
        href = el.get_attribute('href') or ''
        if 'entrar' in txt or 'sign in' in txt or 'login' in href or 'ident.familysearch.org' in href:
            try: el.click()
            except: 
                if href: driver.get(href)
            print(f"  → Clicou: '{el.text.strip()}'")
            break
    except: continue

time.sleep(8)

# Se não foi para login, navegar direto
if 'ident' not in driver.current_url.lower():
    driver.get('https://ident.familysearch.org/pt/identity/login/')
    time.sleep(8)

# Preencher login
u = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
u.click(); time.sleep(0.3); u.clear()
for c in FS_USER:
    u.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
print("  ✓ Username digitado")

p = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
p.click(); time.sleep(0.3); p.clear()
for c in FS_PASS:
    p.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
print("  ✓ Password digitado")

time.sleep(1)
driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
print("  → Submetido, aguardando...")
time.sleep(20)

# Verificar login
body = driver.execute_script("return document.body.innerText") or ""
logged_in = any(kw in body.lower() for kw in ['sign out', 'sair', 'sair da conta'])
if not logged_in:
    for attempt in range(3):
        time.sleep(10)
        body = driver.execute_script("return document.body.innerText") or ""
        logged_in = any(kw in body.lower() for kw in ['sign out', 'sair', FS_USER[:5].lower()])
        if logged_in: break
        print(f"  ⏳ Tentativa {attempt+1}/3...")

if not logged_in:
    print("❌ Login falhou!")
    driver.save_screenshot(f'{DATA_DIR}/login_failed.png')
    driver.quit()
    xvfb.terminate()
    sys.exit(1)

print("✅ Login OK!")

# === BUSCAR NO ENDPOINT JSON v2 ===
# Coleção 3694028 (Bahia Civil Registration) — buscar casamentos Sodré/Cruz em Amargosa ~1890
BASE = "https://www.familysearch.org/service/search/hr/v2/personas?m.defaultFacets=on&m.facetNestCollectionInCategory=on&m.queryRequireDefault=on&count=40"

QUERIES = [
    # Casamentos Tomaz/Teodora
    ("Tomaz_Sodre_casamento_BA", "q.givenName=Tomaz&q.surname=Sodre&q.marriageLikePlace=Amargosa&f.collectionId=3694028"),
    ("Teodora_Cruz_casamento_BA", "q.givenName=Teodora&q.surname=Cruz&q.marriageLikePlace=Amargosa&f.collectionId=3694028"),
    ("Tomaz_Teodora_BA_civil", "q.givenName=Tomaz&q.surname=Sodre&q.spouseGivenName=Teodora&f.collectionId=3694028"),
    # Buscas amplos — casamentos Sodré em Amargosa
    ("Sodre_casamento_Amargosa_1890", "q.surname=Sodre&q.marriageLikePlace=Amargosa&q.marriageLikeDate.from=1880&q.marriageLikeDate.to=1900&f.collectionId=3694028"),
    ("Sodre_casamento_Amargosa_todos", "q.surname=Sodre&q.marriageLikePlace=Amargosa&f.collectionId=3694028"),
    # Da Cruz em Amargosa
    ("Cruz_casamento_Amargosa_1890", "q.surname=Cruz&q.marriageLikePlace=Amargosa&q.marriageLikeDate.from=1880&q.marriageLikeDate.to=1900&f.collectionId=3694028"),
    # Vaz Sodré casamentos
    ("Vaz_Sodre_casamento_BA", "q.surname=Vaz+Sodre&q.marriageLikePlace=Amargosa&f.collectionId=3694028"),
    # Nascimentos — Tomaz/Sodré
    ("Tomaz_Sodre_nascimento_BA", "q.givenName=Tomaz&q.surname=Sodre&q.birthLikePlace=Amargosa&f.collectionId=3694028"),
    ("Marcelo_Sodre_nascimento_BA", "q.givenName=Marcelo&q.surname=Sodre&q.birthLikePlace=Amargosa&f.collectionId=3694028"),
    # Óbitos — Tomaz/Sodré
    ("Tomaz_Sodre_obito_BA", "q.givenName=Tomaz&q.surname=Sodre&q.deathLikePlace=Amargosa&f.collectionId=3694028"),
    # Sem coleção — amplo
    ("Tomaz_Teodora_Amargosa_amplo", "q.givenName=Tomaz&q.surname=Sodre&q.spouseGivenName=Teodora&q.marriageLikePlace=Amargosa"),
    # Variações de nome
    ("Thomaz_Sodre_BA", "q.givenName=Thomaz&q.surname=Sodre&q.birthLikePlace=Amargosa&f.collectionId=3694028"),
    ("Tome_Sodre_BA", "q.givenName=Tomé&q.surname=Sodre&q.birthLikePlace=Amargosa&f.collectionId=3694028"),
    # Gramilo em BA
    ("Gramilo_BA_civil", "q.surname=Gramilo&f.collectionId=3694028"),
]

all_results = {}

# Navegar a uma página de search para estabelecer contexto
print("\n📡 Estabelecendo contexto de search...")
driver.get('https://www.familysearch.org/search/record/results?q.surname=Sodre&q.birthLikePlace=Amargosa&f.collectionId=3694028&count=20')
time.sleep(15)

FETCH_JS = """
var url = arguments[0];
var callback = arguments[1];
fetch(url, {
    credentials: 'include',
    headers: {'Accept': 'application/json', 'X-FS-Accept-Language': 'pt-BR'}
})
.then(function(r) {
    if (!r.ok) return {error: 'HTTP ' + r.status, status: r.status};
    return r.json().then(function(data) {
        var summary = {
            totalResults: data.results || 0,
            index: data.index || 0,
            entryCount: (data.entries || []).length,
            entries: []
        };
        if (data.links && data.links.next) summary.links_next = data.links.next.href;
        (data.entries || []).forEach(function(entry) {
            var person = {};
            person.confidence = entry.confidence || 0;
            person.id = entry.id || '';
            if (entry.content && entry.content.gedcomx) {
                var gx = entry.content.gedcomx;
                if (gx.persons && gx.persons.length > 0) {
                    var p = gx.persons[0];
                    person.name = '';
                    if (p.names && p.names.length > 0) {
                        var n = p.names[0];
                        if (n.nameForms && n.nameForms.length > 0) {
                            person.name = n.nameForms[0].fullText || '';
                        }
                    }
                    person.gender = (p.gender && p.gender.type) ? p.gender.type.replace('http://gedcomx.org/', '') : '';
                    person.facts = [];
                    if (p.facts) {
                        p.facts.forEach(function(fact) {
                            var f = {
                                type: (fact.type || '').replace('http://gedcomx.org/', ''),
                                date: fact.date ? (fact.date.original || (fact.date.formal || '')) : '',
                                place: fact.place ? (fact.place.original || (fact.place.normalized && fact.place.normalized[0] ? fact.place.normalized[0].value : '')) : ''
                            };
                            person.facts.push(f);
                        });
                    }
                }
                person.relationships = [];
                if (gx.relationships) {
                    gx.relationships.forEach(function(rel) {
                        person.relationships.push({
                            type: (rel.type || '').replace('http://gedcomx.org/', ''),
                            person1: rel.person1 ? (rel.person1.resourceId || rel.person1.resource || '') : '',
                            person2: rel.person2 ? (rel.person2.resourceId || rel.person2.resource || '') : ''
                        });
                    });
                }
                person.sources = [];
                if (gx.sourceDescriptions) {
                    gx.sourceDescriptions.forEach(function(src) {
                        person.sources.push({
                            id: src.id || '',
                            title: src.titles && src.titles[0] ? src.titles[0].value : '',
                            about: src.about || ''
                        });
                    });
                }
            }
            summary.entries.push(person);
        });
        callback({ok: true, summary: summary});
    }).catch(function(e) { callback({error: 'JSON parse: ' + e.message}); });
})
.catch(function(e) { callback({error: e.message}); });
"""

for i, (label, params) in enumerate(QUERIES):
    url = f'{BASE}&{params}'
    print(f"\n[{i+1}/{len(QUERIES)}] {label}...")
    
    try:
        result = driver.execute_async_script(FETCH_JS, url)
        
        if result and result.get('ok'):
            summary = result.get('summary', {})
            total = summary.get('totalResults', '?')
            entries = summary.get('entryCount', 0)
            print(f"  Total: {total} | Entradas: {entries}")
            
            for e in summary.get('entries', [])[:5]:
                name = e.get('name', '?')
                facts_str = ', '.join([f"{f['type']}:{f['date']}@{f['place']}" for f in e.get('facts', [])[:3]])
                print(f"    - {name} | {facts_str}")
            
            all_results[label] = summary
        else:
            error = result.get('error', 'unknown') if result else 'script failed'
            print(f"  ❌ {error}")
            all_results[label] = {'error': error}
    except Exception as ex:
        print(f"  ❌ Exception: {ex}")
        all_results[label] = {'error': str(ex)}
    
    # Salvar incrementalmente
    with open(OUTPUT, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    time.sleep(random.uniform(2, 4))

# === NAVEGAR FILMES — buscar índices dos filmes com casamentos ~1890 ===
# Filmes relevantes: 004896387, 004896388, 004896391 (período 1886-1900)
print("\n\n🎬 Navegando filmes para buscar casamentos...")

FILM_ARKS = {
    '004896387': ['33S7-95LB-3VD', '33S7-95LB-3VF', '33SQ-G5LB-3GW'],
    '004896388': ['33S7-95LB-3B7'],
    '004896391': ['33SQ-G5LB-QBX'],
}

SEARCH_TERMS = ['tomaz', 'tomé', 'thomaz', 'teodora', 'gramilo', 'sodré', 'sodre', 'vaz', 'cruz', 'julia']

film_findings = {}

for film_num, arks in FILM_ARKS.items():
    print(f"\n📺 Filme {film_num} ({len(arks)} ARKs)...")
    
    for ark_suffix in arks:
        ark_url = f"https://www.familysearch.org/ark:/61903/3:1:{ark_suffix}"
        print(f"  ARK: {ark_suffix}...")
        
        try:
            driver.get(ark_url)
            time.sleep(10)
            
            # Extrair texto da página
            page_text = driver.execute_script("return document.body.innerText") or ""
            
            # Buscar termos
            page_lower = page_text.lower()
            found_terms = [t for t in SEARCH_TERMS if t in page_lower]
            
            if found_terms:
                print(f"  ✅ ENCONTRADO: {found_terms}")
                film_findings[ark_suffix] = {
                    'film': film_num,
                    'terms': found_terms,
                    'preview': page_text[:3000]
                }
                driver.save_screenshot(f'{DATA_DIR}/film_{film_num}_{ark_suffix.replace("-", "_")}.png')
            else:
                # Verificar se tem índice com nomes
                names_in_index = []
                for line in page_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith(('SKIP', 'Family', 'Search', 'Memories', 'Get', 'Activities', 'Image', 'Film', 'SOURCE', 'ATTACH', 'Column', 'More', 'Information')):
                        if any(c.isalpha() for c in line) and len(line) > 5 and len(line) < 100:
                            names_in_index.append(line)
                
                print(f"  Termos não encontrados. {len(names_in_index)} linhas no índice.")
                film_findings[ark_suffix] = {
                    'film': film_num,
                    'terms': [],
                    'names_count': len(names_in_index),
                    'preview': page_text[:2000]
                }
        except Exception as ex:
            print(f"  ❌ Erro: {ex}")
            film_findings[ark_suffix] = {'film': film_num, 'error': str(ex)}
        
        time.sleep(3)

# Salvar resultados dos filmes
film_output = f'{DATA_DIR}/fs_film_marriage_search.json'
with open(film_output, 'w') as f:
    json.dump(film_findings, f, indent=2, ensure_ascii=False)
print(f"\n💾 Resultados dos filmes salvos em: {film_output}")

# Resumo final
print("\n" + "=" * 60)
print("RESUMO DA BUSCA")
print("=" * 60)
print("\n📡 Endpoint JSON v2:")
for label, data in all_results.items():
    if data and 'error' not in data:
        total = data.get('totalResults', '?')
        entries = data.get('entryCount', 0)
        names = [e.get('name', '?') for e in data.get('entries', [])[:3]]
        print(f"  {label}: {total} resultados, {entries} entradas")
    else:
        print(f"  {label}: ERRO - {data.get('error', '?')}")

print("\n🎬 Navegação de filmes:")
for ark, data in film_findings.items():
    terms = data.get('terms', [])
    if terms:
        print(f"  ✅ {ark} (filme {data.get('film')}): {terms}")
    else:
        print(f"  ❌ {ark} (filme {data.get('film')}): termos não encontrados")

driver.quit()
xvfb.terminate()
print("\nEncerrado.")