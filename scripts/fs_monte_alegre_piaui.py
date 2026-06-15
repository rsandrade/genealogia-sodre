#!/usr/bin/env python3
"""
FamilySearch — Busca Monte Alegre do Piauí + Piauí amplo
Sodré e Gramilo no contexto do Piauí e norte da Bahia.
"""
import subprocess, time, json, sys, os, random

DATA_DIR = '/home/hermes/genealogia/data'
os.makedirs(DATA_DIR, exist_ok=True)

os.system('pkill -9 -f Xvfb 2>/dev/null; pkill -9 -f chromedriver 2>/dev/null; rm -f /tmp/.X99-lock')
time.sleep(2)
xvfb = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
os.environ['DISPLAY'] = ':99'

with open('/home/hermes/genealogia/.env') as f:
    creds = {}
    for line in f.read().strip().split('\n'):
        if '=' in line:
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip()

FS_USER = creds.get('FS_USER', '')
FS_PASS = creds.get('FS_PASS', '')

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
    logged_in = any(kw in body_check.lower() for kw in ['sign out', 'sair'])
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
    print(f"\n--- {label} ---")
    result = driver.execute_async_script("""
    var url = arguments[0]; var callback = arguments[1];
    fetch(url, { credentials: 'include', headers: { 'Accept': 'application/json', 'X-FS-Accept-Language': 'en' } })
    .then(function(r) {
        if (!r.ok) return {error: 'HTTP ' + r.status};
        return r.json().then(function(data) {
            var summary = { totalResults: data.results || 0, entryCount: (data.entries || []).length, entries: [] };
            (data.entries || []).forEach(function(entry) {
                var person = {}; person.id = entry.id || '';
                if (entry.content && entry.content.gedcomx) {
                    var gx = entry.content.gedcomx;
                    if (gx.persons && gx.persons.length > 0) {
                        var p = gx.persons[0]; person.name = '';
                        if (p.names && p.names.length > 0 && p.names[0].nameForms && p.names[0].nameForms.length > 0) person.name = p.names[0].nameForms[0].fullText || '';
                        person.gender = (p.gender && p.gender.type) ? p.gender.type.replace('http://gedcomx.org/', '') : '';
                        person.facts = [];
                        if (p.facts) p.facts.forEach(function(fact) { var f = { type: (fact.type||'').replace('http://gedcomx.org/',''), date: '', place: '' }; if (fact.date) f.date = fact.date.original || (fact.date.formal||''); if (fact.place) f.place = fact.place.original || (fact.place.normalized && fact.place.normalized[0] ? fact.place.normalized[0].value : ''); person.facts.push(f); });
                    }
                    person.relationships = [];
                    if (gx.relationships) gx.relationships.forEach(function(rel) { person.relationships.push({ type: (rel.type||'').replace('http://gedcomx.org/',''), person1: rel.person1 ? (rel.person1.resourceId||rel.person1.resource||'') : '', person2: rel.person2 ? (rel.person2.resourceId||rel.person2.resource||'') : '' }); });
                    person.sources = [];
                    if (gx.sourceDescriptions) gx.sourceDescriptions.forEach(function(src) { person.sources.push({ id: src.id || '', title: src.titles && src.titles[0] ? src.titles[0].value : '', about: src.about || '' }); });
                }
                summary.entries.push(person);
            });
            callback({ok: true, summary: summary});
        }).catch(function(e) { callback({error: 'JSON: ' + e.message}); });
    }).catch(function(e) { callback({error: e.message}); });
    """, url)

    if result.get('error'): print(f"  ❌ {result['error']}"); return None
    summary = result.get('summary', {})
    print(f"  ✅ Total: {summary.get('totalResults', '?')}, Entradas: {summary.get('entryCount', 0)}")
    for e in summary.get('entries', [])[:5]:
        print(f"    → {e.get('name','?')}")
        for f in e.get('facts', [])[:3]: print(f"      {f['type']}: {f.get('date','')} {f.get('place','')}")
    return summary

BASE = 'https://www.familysearch.org/service/search/hr/v2/personas?m.defaultFacets=on&m.facetNestCollectionInCategory=on&m.queryRequireDefault=on'

QUERIES = [
    # === MONTE ALEGRE DO PIAUÍ ===
    ('PI_Sodre_MonteAlegre', 'q.surname=Sodre&q.birthLikePlace=Monte+Alegre+Piaui&count=40'),
    ('PI_Sodre_MonteAlegre_PI', 'q.surname=Sodre&q.birthLikePlace=Monte+Alegre+do+Piaui&count=40'),
    ('PI_Tomaz_Sodre_MonteAlegre', 'q.givenName=Tomaz&q.surname=Sodre&q.birthLikePlace=Monte+Alegre&count=40'),
    ('PI_Marcelo_Sodre_MonteAlegre', 'q.givenName=Marcelo&q.surname=Sodre&q.birthLikePlace=Monte+Alegre&count=40'),
    ('PI_Gramilo_MonteAlegre', 'q.surname=Gramilo&q.birthLikePlace=Monte+Alegre&count=40'),
    ('PI_Gramilo_Piaui', 'q.surname=Gramilo&q.birthLikePlace=Piaui&count=40'),

    # === SODRÉ EM PIAUÍ — nomes relevantes ===
    ('PI_Tomaz_Sodre_Piaui', 'q.givenName=Tomaz&q.surname=Sodre&q.birthLikePlace=Piaui&count=40'),
    ('PI_Tome_Sodre_Piaui', 'q.givenName=Tome&q.surname=Sodre&q.birthLikePlace=Piaui&count=40'),
    ('PI_Marcelo_Sodre_Piaui', 'q.givenName=Marcelo&q.surname=Sodre&q.birthLikePlace=Piaui&count=40'),
    ('PI_Thomaz_Sodre_Piaui', 'q.givenName=Thomaz&q.surname=Sodre&q.birthLikePlace=Piaui&count=40'),

    # === SODRÉ EM PIAUÍ — amplo (casamento/óbito) ===
    ('PI_Sodre_casamento_Piaui', 'q.surname=Sodre&q.marriageLikePlace=Piaui&count=40'),
    ('PI_Sodre_obito_Piaui', 'q.surname=Sodre&q.deathLikePlace=Piaui&count=40'),

    # === MONTE ALEGRE — outros estados ===
    ('MG_Sodre_MonteAlegre', 'q.surname=Sodre&q.birthLikePlace=Monte+Alegre+Minas&count=40'),
    ('BA_Sodre_MonteAlegre', 'q.surname=Sodre&q.birthLikePlace=Monte+Alegre+Bahia&count=40'),

    # === CRUZAMENTO PI↔BA (migração norte→sul) ===
    ('PI_Sodre_nasc_PI_morte_BA', 'q.surname=Sodre&q.birthLikePlace=Piaui&q.deathLikePlace=Bahia&count=40'),
    ('PI_Sodre_nasc_PI_morte_RJ', 'q.surname=Sodre&q.birthLikePlace=Piaui&q.deathLikePlace=Rio+de+Janeiro&count=40'),

    # === GRAMILO em todo Brasil (nome + sobrenome) ===
    ('BR_Gramilo_Gramilho', 'q.surname=Gramilho&count=40'),

    # === Variações de Gramilo ===
    ('BR_Gramilho_Bahia', 'q.surname=Gramilho&q.birthLikePlace=Bahia&count=40'),
    ('BR_Gramilho_Piaui', 'q.surname=Gramilho&q.birthLikePlace=Piaui&count=40'),
    ('BR_Gramilho_MG', 'q.surname=Gramilho&q.birthLikePlace=Minas+Gerai&count=40'),
]

print(f"{'=' * 60}")
print(f"FamilySearch — Monte Alegre do PI + Piauí + Gramilho")
print(f"{len(QUERIES)} queries")
print(f"{'=' * 60}")

all_results = {}
try:
    logged_in = do_login()
    if not logged_in:
        print("❌ Login falhou"); sys.exit(1)
    print(f"\n✓ Login OK")
    driver.get('https://www.familysearch.org/search/record/results?q.surname=Sodre&q.birthLikePlace=Piaui&count=20')
    time.sleep(15)

    for i, (label, params) in enumerate(QUERIES):
        url = f'{BASE}&{params}'
        summary = fetch_endpoint(url, label)
        if summary: all_results[label] = summary
        else: all_results[label] = {'error': 'fetch_failed', 'label': label}
        time.sleep(random.uniform(3, 6))

    output_path = f'{DATA_DIR}/fs_monte_alegre_piaui.json'
    with open(output_path, 'w') as f: json.dump(all_results, f, indent=2, ensure_ascii=False)
    existing_path = f'{DATA_DIR}/fs_endpoint_structured.json'
    existing = {}
    try:
        with open(existing_path) as f: existing = json.load(f)
    except: pass
    for k, v in all_results.items():
        if k not in existing: existing[k] = v
    with open(existing_path, 'w') as f: json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"RESULTADOS — MONTE ALEGRE PI + PIAUÍ")
    print(f"{'=' * 60}")
    for label, data in all_results.items():
        if data and isinstance(data, dict) and 'error' not in data:
            total = data.get('totalResults', '?')
            entries = data.get('entryCount', 0)
            names = [e.get('name', '?') for e in data.get('entries', [])[:3]]
            print(f"  {label}: {total} resultados, {entries} entradas → {', '.join(names)}")
        else:
            print(f"  {label}: ERRO ou sem dados")

    # DESTAQUES
    print(f"\n--- DESTAQUES (Sodré/Gramilo + PI/BA/RJ) ---")
    for label, data in all_results.items():
        if data and isinstance(data, dict) and 'error' not in data:
            for e in data.get('entries', []):
                name = e.get('name', '').lower()
                if 'sodr' in name or 'gramilo' in name or 'gramilh' in name:
                    facts = e.get('facts', [])
                    places = ' '.join(f.get('place','') for f in facts if f.get('place'))
                    if any(kw in places.lower() for kw in ['piaui', 'piauí', 'bahia', 'rj', 'rio', 'jequi', 'amargosa', 'monte alegre']):
                        fact_str = '; '.join(f"{f['type']}:{f.get('date','')} {f.get('place','')}" for f in facts[:4])
                        print(f"  ★ [{label}] {e.get('name','?')} → {fact_str}")

except Exception as e:
    print(f"\n✗ Erro: {e}")
    import traceback; traceback.print_exc()
    try: driver.save_screenshot(f'{DATA_DIR}/fs_piaui_error.png')
    except: pass
finally:
    try: driver.quit()
    except: pass
    xvfb.terminate()
    print("\nEncerrado.")