#!/usr/bin/env python3
"""
Busca profunda em Poções/BA e Guarani/BA — Sodré, Vaz Sodré, Gramilo, Tomaz, Marcelo
Período: 1860-1930 (cobrindo nascimento de Tomaz ~1860, casamento ~1891, nascimento de Marcelo ~1885)
Coleção: 3694028 (Bahia, Registro Civil 1877-2021)
Também busca em 2558782 (Bahia, registros da Igreja) para registros paroquiais de Poções/Amargosa
"""
import subprocess, time, json, sys, os, random

DATA_DIR = '/home/hermes/genealogia/data'
os.makedirs(DATA_DIR, exist_ok=True)
OUTPUT = f'{DATA_DIR}/fs_pocoes_profundo.json'

# Xvfb
os.system('pkill -9 -f "Xvfb :99" 2>/dev/null; pkill -9 -f chromedriver 2>/dev/null; rm -f /tmp/.X99-lock')
time.sleep(2)
xvfb = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
os.environ['DISPLAY'] = ':99'

# Credenciais
with open('/home/hermes/genealogia/.env') as f:
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
options.add_argument('--lang=en-US,en')
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36')

driver = uc.Chrome(options=options, version_main=149)
wait = WebDriverWait(driver, 30)

def do_login():
    print("Login...")
    driver.get('https://www.familysearch.org/en/')
    time.sleep(10)

    for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
        try:
            if 'sign in' in (el.text or '').lower():
                href = el.get_attribute('href') or ''
                try: el.click()
                except: driver.get(href) if href else None
                print(f"  → Clicou em: '{el.text.strip()}'")
                break
        except: continue

    time.sleep(10)
    if 'login' not in driver.current_url.lower() and 'signin' not in driver.current_url.lower() and 'ident' not in driver.current_url.lower():
        print("  → Navegando direto para login...")
        driver.get('https://ident.familysearch.org/en/identity/login/')
        time.sleep(8)

    u = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
    u.click(); time.sleep(0.3); u.clear()
    for c in FS_USER: u.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
    print("  ✓ Username digitado")

    p = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
    p.click(); time.sleep(0.3); p.clear()
    for c in FS_PASS: p.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
    print("  ✓ Password digitado")

    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    print("  → Submetido, aguardando...")
    time.sleep(20)

    body_check = driver.execute_script("return document.body.innerText") or ""
    logged_in = any(kw in body_check.lower() for kw in ['sign out', 'sair', FS_USER[:5].lower()])

    if not logged_in:
        for attempt in range(4):
            time.sleep(15)
            body_check = driver.execute_script("return document.body.innerText") or ""
            logged_in = any(kw in body_check.lower() for kw in ['sign out', 'sair', FS_USER[:5].lower()])
            if logged_in: break
            print(f"  ⏳ Tentativa {attempt+1}/4...")

    print(f"  Logado: {logged_in}")
    return logged_in

def fetch_endpoint(url, label):
    """Fetch JSON from FS endpoint and return structured summary."""
    print(f"\n--- {label} ---")
    result = driver.execute_async_script("""
    var url = arguments[0];
    var callback = arguments[1];
    fetch(url, {
        credentials: 'include',
        headers: {'Accept': 'application/json', 'X-FS-Accept-Language': 'en'}
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
            if (data.links && data.links.next) summary.nextUrl = data.links.next.href;
            (data.entries || []).forEach(function(entry) {
                var person = {};
                person.id = entry.id || '';
                person.confidence = entry.confidence || 0;
                if (entry.content && entry.content.gedcomx) {
                    var gx = entry.content.gedcomx;
                    if (gx.persons && gx.persons.length > 0) {
                        var p = gx.persons[0];
                        person.name = '';
                        if (p.names && p.names.length > 0 && p.names[0].nameForms && p.names[0].nameForms.length > 0) {
                            person.name = p.names[0].nameForms[0].fullText || '';
                        }
                        person.gender = (p.gender && p.gender.type) ? p.gender.type.replace('http://gedcomx.org/', '') : '';
                        person.facts = [];
                        if (p.facts) {
                            p.facts.forEach(function(fact) {
                                var f = {
                                    type: (fact.type || '').replace('http://gedcomx.org/', ''),
                                    date: '',
                                    place: ''
                                };
                                if (fact.date) f.date = fact.date.original || (fact.date.formal || '');
                                if (fact.place) f.place = fact.place.original || (fact.place.normalized && fact.place.normalized[0] ? fact.place.normalized[0].value : '');
                                person.facts.push(f);
                            });
                        }
                    }
                    person.relationships = [];
                    if (gx.relationships) {
                        gx.relationships.forEach(function(rel) {
                            person.relationships.push({
                                type: (rel.type || '').replace('http://gedcomx.org/', ''),
                                person1: rel.person1 ? (rel.person1.resourceId || '') : '',
                                person2: rel.person2 ? (rel.person2.resourceId || '') : ''
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
    """, url)

    if result.get('error'):
        print(f"  ❌ {result['error']}")
        return None

    summary = result.get('summary', {})
    total = summary.get('totalResults', '?')
    entries = summary.get('entryCount', 0)
    print(f"  Total: {total} | Entradas: {entries}")
    for e in summary.get('entries', [])[:8]:
        name = e.get('name', '?')
        facts_str = ' | '.join([f"{f['type']}:{f['date']}@{f['place']}" for f in e.get('facts', [])[:3]])
        rels = ' | '.join([f"{r['type']}({r['person1']}↔{r['person2']})" for r in e.get('relationships', [])[:2]])
        srcs = ' | '.join([s.get('about', '')[-20:] for s in e.get('sources', [])[:1]])
        print(f"    {name}: {facts_str}")
        if rels: print(f"      rels: {rels}")
        if srcs: print(f"      src: {srcs}")
    return summary

# ============================================
# QUERIES — Poções/Guarani/Amargosa profundo
# ============================================
BASE = "https://www.familysearch.org/service/search/hr/v2/personas?m.defaultFacets=on&m.facetNestCollectionInCategory=on&m.queryRequireDefault=on&count=40"
COL_BA = "f.collectionId=3694028"  # Bahia Registro Civil
COL_IGREJA = "f.collectionId=2558782"  # Bahia Igreja

QUERIES = [
    # === POCÕES (município-mãe de Ibicuí até 1952) ===
    # Casamentos Sodré em Poções 1877-1930
    ("Pocoes_Sodre_casamento", f"q.surname=Sodre&q.marriageLikePlace=Pocoes&{COL_BA}&q.marriageLikeDate.from=1877&q.marriageLikeDate.to=1930"),
    # Nascimentos Sodré em Poções
    ("Pocoes_Sodre_nascimento", f"q.surname=Sodre&q.birthLikePlace=Pocoes&{COL_BA}&q.birthLikeDate.from=1860&q.birthLikeDate.to=1930"),
    # Óbitos Sodré em Poções
    ("Pocoes_Sodre_obito", f"q.surname=Sodre&q.deathLikePlace=Pocoes&{COL_BA}&q.deathLikeDate.from=1877&q.deathLikeDate.to=1930"),
    
    # === GUARANI (nome histórico de Ibicuí até 1942) ===
    # Tudo de Sodré em Guarani
    ("Guarani_Sodre_tudo", f"q.surname=Sodre&q.birthLikePlace=Guarani&{COL_BA}"),
    ("Guarani_Sodre_casamento", f"q.surname=Sodre&q.marriageLikePlace=Guarani&{COL_BA}"),
    # Vaz Sodré em Guarani
    ("Guarani_VazSodre_tudo", f"q.surname=Vaz+Sodre&q.birthLikePlace=Guarani&{COL_BA}"),
    
    # === TOMAZ / MARCELO em Poções e Guarani ===
    ("Pocoes_Tomaz_Sodre", f"q.givenName=Tomaz&q.surname=Sodre&q.birthLikePlace=Pocoes&{COL_BA}"),
    ("Pocoes_Marcelo_Sodre", f"q.givenName=Marcelo&q.surname=Sodre&q.birthLikePlace=Pocoes&{COL_BA}"),
    ("Guarani_Tomaz_Sodre", f"q.givenName=Tomaz&q.surname=Sodre&q.birthLikePlace=Guarani&{COL_BA}"),
    ("Guarani_Marcelo_Sodre", f"q.givenName=Marcelo&q.surname=Sodre&q.birthLikePlace=Guarani&{COL_BA}"),
    
    # === VAZ SODRÉ em Poções (conexão Amargosa-Guarani) ===
    ("Pocoes_VazSodre_casamento", f"q.surname=Vaz+Sodre&q.marriageLikePlace=Pocoes&{COL_BA}&q.marriageLikeDate.from=1877&q.marriageLikeDate.to=1930"),
    ("Pocoes_VazSodre_nascimento", f"q.surname=Vaz+Sodre&q.birthLikePlace=Pocoes&{COL_BA}&q.birthLikeDate.from=1860&q.birthLikeDate.to=1930"),
    
    # === GRAMILO em toda BA (nome raro, qualquer lugar) ===
    ("BA_Gramilo_tudo", f"q.surname=Gramilo&{COL_BA}"),
    ("BA_Gramilo_igreja", f"q.surname=Gramilo&{COL_IGREJA}"),
    
    # === REGISTROS DA IGREJA — Sodré em Poções/Amargosa ===
    ("Igreja_Sodre_Pocoes", f"q.surname=Sodre&q.birthLikePlace=Pocoes&{COL_IGREJA}"),
    ("Igreja_Sodre_Amargosa_cas", f"q.surname=Sodre&q.marriageLikePlace=Amargosa&{COL_IGREJA}&q.marriageLikeDate.from=1870&q.marriageLikeDate.to=1910"),
    
    # === TOMAZ com variações em toda BA ===
    ("BA_Tomaz_Sodre_civil", f"q.givenName=Tomaz&q.surname=Sodre&{COL_BA}&q.birthLikeDate.from=1850&q.birthLikeDate.to=1900"),
    ("BA_Tome_Sodre_civil", f"q.givenName=Thomaz&q.surname=Sodre&{COL_BA}&q.birthLikeDate.from=1850&q.birthLikeDate.to=1900"),
    
    # === RITA (Rosa) Sodré — possível Vaz Sodré ===
    ("Pocoes_Rita_Sodre", f"q.givenName=Rita&q.surname=Sodre&q.birthLikePlace=Pocoes&{COL_BA}"),
    ("Amargosa_Rita_Sodre", f"q.givenName=Rita&q.surname=Sodre&q.birthLikePlace=Amargosa&{COL_BA}&q.birthLikeDate.from=1860&q.birthLikeDate.to=1910"),
    
    # === IBIUÍ e POÇÕES — busca por localidade nos registros de igreja ===
    ("Igreja_Pocoes_Sodre_cas", f"q.surname=Sodre&{COL_IGREJA}&q.marriageLikePlace=Pocoes"),
    ("Igreja_Guarani_Sodre", f"q.surname=Sodre&{COL_IGREJA}&q.birthLikePlace=Guarani"),
]

print(f"{'=' * 60}")
print(f"Busca Poções/Guarani Profundo — {len(QUERIES)} queries")
print(f"{'=' * 60}")

all_results = {}
saved_count = 0

try:
    logged_in = do_login()
    if not logged_in:
        print("❌ Login falhou — abortando")
        sys.exit(1)

    print(f"\n✓ Login OK — navegando ao search para estabelecer contexto...")
    driver.get('https://www.familysearch.org/search/record/results?q.surname=Sodre&q.birthLikePlace=Amargosa&count=20')
    time.sleep(15)

    for i, (label, params) in enumerate(QUERIES):
        url = f'{BASE}&{params}'
        summary = fetch_endpoint(url, label)
        if summary:
            all_results[label] = summary
        else:
            all_results[label] = {'error': 'fetch_failed', 'label': label}
        
        # Salvamento incremental a cada 5 queries
        saved_count += 1
        if saved_count % 5 == 0 or saved_count == len(QUERIES):
            with open(OUTPUT, 'w') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"  💾 Salvo {saved_count}/{len(QUERIES)} queries no disco")
        
        time.sleep(random.uniform(3, 6))

    # Salvar resultado final
    with open(OUTPUT, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Resultado final salvo em: {OUTPUT}")

    # Resumo
    print(f"\n{'=' * 60}")
    print(f"RESUMO FINAL")
    print(f"{'=' * 60}")
    relevant_found = 0
    for label, data in all_results.items():
        if data and 'error' not in data:
            total = data.get('totalResults', '?')
            entries = data.get('entryCount', 0)
            names = [e.get('name', '?') for e in data.get('entries', [])[:3]]
            marker = "★" if (isinstance(total, int) and total > 0) or entries > 0 else "○"
            if isinstance(total, int) and total > 0:
                relevant_found += 1
            print(f"  {marker} {label}: {total} resultados, {entries} entradas → {', '.join(names)}")
        else:
            print(f"  ❌ {label}: ERRO")
    print(f"\nQueries com resultados: {relevant_found}/{len(QUERIES)}")

except Exception as e:
    print(f"\n✗ Erro: {e}")
    import traceback; traceback.print_exc()
    try: driver.save_screenshot(f'{DATA_DIR}/fs_pocoes_error.png')
    except: pass
    # Salvar o que tiver
    with open(OUTPUT, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"💾 Parcial salvo em: {OUTPUT}")

finally:
    try: driver.quit()
    except: pass
    xvfb.terminate()
    print("\nEncerrado.")
