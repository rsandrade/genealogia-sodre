#!/usr/bin/env python3
"""
Extrair detalhes dos ARKs da Teodora Maria Da Cruz usando fetch() no contexto autenticado.
Método comprovado da skill: login UC + fetch() ao endpoint JSON v2.
"""
import json, time, random, subprocess, os, sys

DATA_DIR = '/home/hermes/genealogia/data'
ENV_PATH = '/home/hermes/genealogia/.env'
OUTPUT = f'{DATA_DIR}/teodora_ark_details.json'

os.system('pkill -9 -f Xvfb 2>/dev/null; rm -f /tmp/.X99-lock')
time.sleep(1)
xvfb = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
os.environ['DISPLAY'] = ':99'

with open(ENV_PATH) as f:
    creds = {}
    for line in f.read().strip().split('\n'):
        if '=' in line:
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip()

FS_USER = creds.get('FS_USER', '') or creds.get('TK_USERNAME', '')
FS_PASS = creds.get('FS_PASS', '') or creds.get('TK_PASSWORD', '')

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
print("🔐 Login...")
driver.get('https://www.familysearch.org/pt/')
time.sleep(8)

for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
    try:
        txt = (el.text or '').lower()
        href = el.get_attribute('href') or ''
        if 'entrar' in txt or 'sign in' in txt or 'ident.familysearch.org' in href:
            try: el.click()
            except:
                if href: driver.get(href)
            print(f"  → Clicou: '{el.text.strip()}'")
            break
    except: continue

time.sleep(8)
if 'ident' not in driver.current_url.lower():
    driver.get('https://ident.familysearch.org/pt/identity/login/')
    time.sleep(8)

u = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
u.click(); time.sleep(0.3); u.clear()
for c in FS_USER:
    u.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
print("  ✓ Username")

p = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
p.click(); time.sleep(0.3); p.clear()
for c in FS_PASS:
    p.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
print("  ✓ Password")

time.sleep(1)
driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
print("  → Submetido...")
time.sleep(20)

body = driver.execute_script("return document.body.innerText") or ""
logged_in = any(kw in body.lower() for kw in ['sign out', 'sair'])
if not logged_in:
    for attempt in range(3):
        time.sleep(10)
        body = driver.execute_script("return document.body.innerText") or ""
        logged_in = any(kw in body.lower() for kw in ['sign out', 'sair', FS_USER[:5].lower()])
        if logged_in: break

if not logged_in:
    print("❌ Login falhou!")
    driver.save_screenshot(f'{DATA_DIR}/teodora_login_failed.png')
    driver.quit(); xvfb.terminate(); sys.exit(1)

print("✅ Login OK!")

# Estabelecer contexto
print("\n📡 Estabelecendo contexto...")
driver.get('https://www.familysearch.org/search/record/results?q.givenName=Teodora&q.surname=Cruz&q.birthLikePlace=Amargosa&f.collectionId=3694028&count=20')
time.sleep(15)

# === FETCH aos ARKs via endpoint JSON v2 ===
# Usar q.pid para buscar as pessoas específicas
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
            entryCount: (data.entries || []).length,
            entries: []
        };
        (data.entries || []).forEach(function(entry) {
            var person = {};
            person.confidence = entry.confidence || 0;
            person.id = entry.id || '';
            if (entry.content && entry.content.gedcomx) {
                var gx = entry.content.gedcomx;
                if (gx.persons && gx.persons.length > 0) {
                    // Extrair TODOS os persons (não só o primeiro)
                    person.allPersons = gx.persons.map(function(p) {
                        var pp = {};
                        pp.name = '';
                        if (p.names && p.names.length > 0) {
                            pp.name = p.names[0].nameForms[0].fullText || '';
                        }
                        pp.gender = (p.gender && p.gender.type) ? p.gender.type.replace('http://gedcomx.org/', '') : '';
                        pp.facts = (p.facts || []).map(function(f) {
                            return {
                                type: (f.type || '').replace('http://gedcomx.org/', ''),
                                date: f.date ? (f.date.original || (f.date.formal || '')) : '',
                                place: f.place ? (f.place.original || (f.place.normalized && f.place.normalized[0] ? f.place.normalized[0].value : '')) : ''
                            };
                        });
                        return pp;
                    });
                    // Primeira pessoa = principal
                    if (gx.persons[0] && gx.persons[0].names && gx.persons[0].names[0]) {
                        person.name = gx.persons[0].names[0].nameForms[0].fullText || '';
                    }
                }
                person.relationships = (gx.relationships || []).map(function(rel) {
                    return {
                        type: (rel.type || '').replace('http://gedcomx.org/', ''),
                        person1: rel.person1 ? (rel.person1.resourceId || rel.person1.resource || '') : '',
                        person2: rel.person2 ? (rel.person2.resourceId || rel.person2.resource || '') : ''
                    };
                });
                person.sources = (gx.sourceDescriptions || []).map(function(src) {
                    return {
                        id: src.id || '',
                        title: src.titles && src.titles[0] ? src.titles[0].value : '',
                        about: src.about || ''
                    };
                });
            }
            summary.entries.push(person);
        });
        callback({ok: true, summary: summary});
    }).catch(function(e) { callback({error: 'JSON parse: ' + e.message}); });
})
.catch(function(e) { callback({error: e.message}); });
"""

# Buscas direcionadas para Teodora
QUERIES = [
    # Teodora Maria Da Cruz — buscar detalhes com local
    ("Teodora_Cruz_Amargosa_detalhado", "q.givenName=Teodora&q.surname=Cruz&q.birthLikePlace=Amargosa&f.collectionId=3694028&count=40"),
    # Teodora nascida 1891 BA
    ("Teodora_1891_BA", "q.givenName=Teodora&q.surname=Cruz&q.birthLikeDate.from=1890&q.birthLikeDate.to=1892&f.collectionId=3694028&count=40"),
    # Teodora Julia da Cruz
    ("Teodora_Julia_Cruz_BA", "q.givenName=Teodora+Julia&q.surname=Cruz&f.collectionId=3694028&count=40"),
    # Buscar pelo person ID 6V4R-MFX8 (Teodora com data)
    ("Teodora_6V4R_PID", "q.pid=6V4R-MFX8&f.collectionId=3694028&count=10"),
    # Buscar pelo casal (p_297622363930 × p_297622363931)
    ("Teodora_couple_PID2", "q.pid=p_297622363931&f.collectionId=3694028&count=10"),
]

all_results = {}

for i, (label, params) in enumerate(QUERIES):
    url = f"https://www.familysearch.org/service/search/hr/v2/personas?m.defaultFacets=on&m.facetNestCollectionInCategory=on&m.queryRequireDefault=on&count=40&{params}"
    print(f"\n[{i+1}/{len(QUERIES)}] {label}...")
    
    try:
        result = driver.execute_async_script(FETCH_JS, url)
        if result and result.get('ok'):
            summary = result.get('summary', {})
            total = summary.get('totalResults', '?')
            entries = summary.get('entryCount', 0)
            print(f"  Total: {total} | Entradas: {entries}")
            
            for e in summary.get('entries', [])[:10]:
                name = e.get('name', '?')
                all_persons = e.get('allPersons', [])
                facts_list = []
                
                # Mostrar dados da pessoa principal
                if all_persons:
                    main = all_persons[0]
                    facts_str = ', '.join([f"{f['type']}:{f['date']}@{f['place']}" for f in main.get('facts', [])[:4]])
                    facts_list.append(f"  {main['name']} | {facts_str}")
                    
                    # Mostrar pessoas relacionadas no mesmo registro
                    for p in all_persons[1:]:
                        pf = ', '.join([f"{f['type']}:{f['date']}@{f['place']}" for f in p.get('facts', [])[:3]])
                        facts_list.append(f"    ↔ {p['name']} ({p.get('gender','?')}) | {pf}")
                
                rels = e.get('relationships', [])
                rel_str = '; '.join([f"{r['type']}: {r.get('person1','')}-{r.get('person2','')}" for r in rels[:3]])
                
                print(f"  - {name}")
                for line in facts_list:
                    print(line)
                if rel_str:
                    print(f"    Rel: {rel_str}")
            
            all_results[label] = summary
        else:
            error = result.get('error', 'unknown') if result else 'script failed'
            print(f"  ❌ {error}")
            all_results[label] = {'error': error}
    except Exception as ex:
        print(f"  ❌ Exception: {ex}")
        all_results[label] = {'error': str(ex)}
    
    with open(OUTPUT, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    time.sleep(random.uniform(2, 4))

# Agora navegar ao ARK da Teodora para ver a transcrição completa
print("\n\n📄 Navegando ao ARK da Teodora...")
driver.get('https://www.familysearch.org/ark:/61903/3:1:3Q9M-CSKB-YYR8')
time.sleep(15)

page_text = driver.execute_script("return document.body.innerText") or ""
print(f"  Texto extraído: {len(page_text)} chars")

# Procurar dados-chave
for keyword in ['Teodora', 'Cruz', 'Amargosa', 'Tomaz', 'Sodré', '1891', 'nascimento', 'casamento', 'filia', 'pai', 'mãe', 'conjuge', 'conjug']:
    lower = page_text.lower()
    if keyword.lower() in lower:
        idx = lower.find(keyword.lower())
        context = page_text[max(0, idx-80):idx+200]
        print(f"\n  ✅ '{keyword}': ...{context}...")

driver.save_screenshot(f'{DATA_DIR}/teodora_ark_screenshot.png')

# Salvar texto completo
with open(f'{DATA_DIR}/teodora_ark_text.txt', 'w') as f:
    f.write(page_text)

# Navegar ao segundo ARK
print("\n📄 Segundo ARK...")
driver.get('https://www.familysearch.org/ark:/61903/3:1:3Q9M-CS2Q-R7BS-P')
time.sleep(15)

page_text2 = driver.execute_script("return document.body.innerText") or ""
print(f"  Texto extraído: {len(page_text2)} chars")

for keyword in ['Teodora', 'Cruz', 'Amargosa', '1891', 'filia', 'pai', 'mãe', 'conjuge']:
    lower = page_text2.lower()
    if keyword.lower() in lower:
        idx = lower.find(keyword.lower())
        context = page_text2[max(0, idx-80):idx+200]
        print(f"  ✅ '{keyword}': ...{context}...")

driver.save_screenshot(f'{DATA_DIR}/teodora_ark2_screenshot.png')

with open(f'{DATA_DIR}/teodora_ark2_text.txt', 'w') as f:
    f.write(page_text2)

print("\n" + "=" * 60)
print("RESULTADOS SALVOS")
print("=" * 60)
print(f"  {OUTPUT}")
print(f"  {DATA_DIR}/teodora_ark_text.txt")
print(f"  {DATA_DIR}/teodora_ark2_text.txt")
print(f"  {DATA_DIR}/teodora_ark_screenshot.png")
print(f"  {DATA_DIR}/teodora_ark2_screenshot.png")

driver.quit()
xvfb.terminate()
print("\nEncerrado.")