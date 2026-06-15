#!/usr/bin/env python3
"""
FamilySearch — Extrair transcrições + baixar imagens paroquiais de Amargosa
Usa método de login comprovado (fs_gap_search.py) + CDP auto-download.
"""
import subprocess, time, json, os, sys, random, re
from pathlib import Path
from datetime import datetime

GENEALOGIA_DIR = '/home/hermes/genealogia'
DATA_DIR = f'{GENEALOGIA_DIR}/data'
IMAGES_DIR = f'{DATA_DIR}/images/amargosa_paroquiais'
TRANSCRIPT_DIR = f'{DATA_DIR}/transcriptions'
LOG_FILE = f'{DATA_DIR}/fs_extract_transcriptions.log'
RESULTS_FILE = f'{DATA_DIR}/fs_transcriptions_results.json'

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

# =============================================
# CREDENCIAIS
# =============================================
with open(f'{GENEALOGIA_DIR}/.env') as f:
    creds = {}
    for line in f.read().strip().split('\n'):
        if '=' in line:
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip()
FS_USER = creds.get('FS_USER', '') or creds.get('TK_USERNAME', '')
FS_PASS = creds.get('FS_PASS', '') or creds.get('TK_PASSWORD', '')
if not FS_USER or not FS_PASS:
    log("❌ Credenciais não encontradas"); sys.exit(1)

# =============================================
# SETUP — método comprovado (fs_gap_search.py)
# =============================================
subprocess.run(['pkill', '-9', '-f', 'Xvfb :99'], capture_output=True)
time.sleep(1)
subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
os.environ['DISPLAY'] = ':99'
time.sleep(2)

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
    """Login método comprovado — fs_gap_search.py"""
    log("🔐 Fazendo login...")
    driver.get('https://www.familysearch.org/en/')
    time.sleep(10)

    # Clicar em "Sign In"
    for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
        try:
            if 'sign in' in (el.text or '').lower():
                href = el.get_attribute('href') or ''
                try: el.click()
                except: driver.get(href) if href else None
                log(f"  → Clicou em: '{el.text.strip()}'")
                break
        except: continue

    time.sleep(10)
    if 'login' not in driver.current_url.lower() and 'signin' not in driver.current_url.lower() and 'ident' not in driver.current_url.lower():
        log("  → Navegando direto para login...")
        driver.get('https://ident.familysearch.org/en/identity/login/')
        time.sleep(8)

    # Digitar username e password
    u = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
    u.click(); time.sleep(0.3); u.clear()
    for c in FS_USER: u.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
    log("  ✓ Username digitado")

    p = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
    p.click(); time.sleep(0.3); p.clear()
    for c in FS_PASS: p.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
    log("  ✓ Password digitado")

    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    log("  → Submetido, aguardando...")
    time.sleep(20)

    # Verificar login
    body_check = driver.execute_script("return document.body.innerText") or ""
    html_check = driver.execute_script("return document.body.innerHTML") or ""
    logged_in = any(kw in body_check.lower() for kw in ['sign out', 'sair'])
    if not logged_in:
        logged_in = 'sign out' in html_check.lower() or FS_USER[:5].lower() in body_check.lower()
    
    if not logged_in:
        # Tentar novamente — esperar mais
        for attempt in range(3):
            log(f"  ⏳ Verificando login... tentativa {attempt+1}")
            time.sleep(10)
            body_check = driver.execute_script("return document.body.innerText") or ""
            html_check = driver.execute_script("return document.body.innerHTML") or ""
            logged_in = any(kw in body_check.lower() for kw in ['sign out', 'sair'])
            if not logged_in:
                logged_in = 'sign out' in html_check.lower() or FS_USER[:5].lower() in body_check.lower()
            if logged_in:
                break
    
    if not logged_in:
        driver.save_screenshot(f'{DATA_DIR}/fs_login_failed.png')
        log(f"❌ Login falhou! Saindo...")
        return False
    
    log("✅ Login bem-sucedido!")
    return True

try:
    # =============================================
    # LOGIN
    # =============================================
    if not do_login():
        sys.exit(1)
    
    # Navegar a uma página de search para estabelecer contexto
    driver.get('https://www.familysearch.org/search/record/results?q.surname=Sodre&q.birthLikePlace=Amargosa&f.collectionId=3694028&count=20')
    time.sleep(5)
    
    # =============================================
    # EXTRAIR TRANSCRIÇÕES VIA FETCH (endpoint JSON v2)
    # =============================================
    # Carregar ARKs dos dados existentes
    sodre_arks_transcription = set()  # 3:1:3Q9M — registro civil com transcrição
    sodre_arks_paroquial = set()       # 3:1:33S7/33SQ — paroquial (imagem apenas)
    
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.endswith('.json') and fname.startswith('fs_'):
            fpath = f'{DATA_DIR}/{fname}'
            try:
                with open(fpath) as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for label, d in data.items():
                        entries = d.get('entries', [])
                        if isinstance(entries, list):
                            for e in entries:
                                names = str(e.get('names', e.get('name', ''))).lower()
                                facts = str(e.get('facts', '')).lower()
                                sources = str(e.get('sources', ''))
                                if ('sodr' in names or 'gramil' in names or 'vaz' in names) and \
                                   any(p in facts or p in names for p in ['amargosa', 'pocoes', 'guarani', 'ibicui', 'ibitup', 'jequi', 'conquista', 'tapera']):
                                    for m in re.finditer(r'3:1:3Q9M-[A-Za-z0-9-]+', sources):
                                        sodre_arks_transcription.add(m.group())
                                    for m in re.finditer(r'3:1:33S[7Q]-[A-Za-z0-9-]+', sources):
                                        sodre_arks_paroquial.add(m.group())
            except:
                pass
    
    sodre_arks_transcription = sorted(sodre_arks_transcription)
    sodre_arks_paroquial = sorted(sodre_arks_paroquial)
    
    log(f"📋 ARKs com transcrição (3:1:3Q9M): {len(sodre_arks_transcription)}")
    log(f"🖼️ ARKs paroquiais (33S7/33SQ): {len(sodre_arks_paroquial)}")
    
    all_transcriptions = {}
    
    # =============================================
    # EXTRAIR TRANSCRIÇÕES INDEXADAS
    # =============================================
    for i, ark_id in enumerate(sodre_arks_transcription):
        url = f'https://www.familysearch.org/ark:/61903/{ark_id}'
        log(f"\n[{i+1}/{len(sodre_arks_transcription)}] Extraindo transcrição: {ark_id}")
        
        try:
            # Usar fetch via execute_async_script (método comprovado)
            result = driver.execute_async_script("""
                var url = arguments[0];
                var callback = arguments[arguments.length - 1];
                
                fetch(url, {credentials: 'include', headers: {'Accept': 'text/html'}})
                .then(r => r.text())
                .then(html => {
                    // Parse HTML para extrair dados
                    var parser = new DOMParser();
                    var doc = parser.parseFromString(html, 'text/html');
                    var text = doc.body ? doc.body.innerText : '';
                    
                    // Extrair campos
                    var fields = {};
                    doc.querySelectorAll('[data-label], .field-label, .label, dt, th').forEach(function(el) {
                        var label = el.innerText.trim();
                        var value = '';
                        var next = el.nextElementSibling;
                        if (next) value = next.innerText.trim();
                        if (label && value) fields[label] = value;
                    });
                    
                    callback({
                        url: url,
                        title: doc.title,
                        body_length: text.length,
                        body_preview: text.substring(0, 3000),
                        fields: fields,
                        ok: true
                    });
                })
                .catch(e => callback({error: e.message, ok: false}));
            """, url)
            
            if result and result.get('ok'):
                all_transcriptions[ark_id] = result
                log(f"    ✅ {result.get('body_length', 0)} chars, {len(result.get('fields', {}))} campos")
            else:
                log(f"    ⚠️ Fetch falhou, tentando navegação direta...")
                driver.get(url)
                time.sleep(8)
                body = driver.execute_script("return document.body.innerText") or ""
                all_transcriptions[ark_id] = {
                    'url': url,
                    'body_preview': body[:3000],
                    'method': 'navigation'
                }
                log(f"    📄 {len(body)} chars via navegação")
            
        except Exception as e:
            log(f"    ❌ Erro: {str(e)[:80]}")
            all_transcriptions[ark_id] = {'url': url, 'error': str(e)[:200]}
        
        # Salvar incrementalmente a cada 5
        if (i + 1) % 5 == 0 or i == len(sodre_arks_transcription) - 1:
            with open(RESULTS_FILE, 'w') as f:
                json.dump(all_transcriptions, f, indent=2, ensure_ascii=False)
            log(f"  💾 Salvo {len(all_transcriptions)} transcrições")
        
        time.sleep(random.uniform(2, 4))
    
    # =============================================
    # BAIXAR IMAGENS PAROQUIAIS
    # =============================================
    log(f"\n🖼️ Baixando {len(sodre_arks_paroquial)} imagens paroquiais...")
    
    # Configurar CDP para auto-download
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': IMAGES_DIR
    })
    
    for i, ark_id in enumerate(sodre_arks_paroquial):
        url = f'https://www.familysearch.org/ark:/61903/{ark_id}'
        log(f"\n  [{i+1}/{len(sodre_arks_paroquial)}] Imagem: {ark_id}")
        
        try:
            driver.get(url)
            time.sleep(10)
            
            # Screenshot
            driver.save_screenshot(f'{IMAGES_DIR}/{ark_id.replace(":", "_")}.png')
            
            # Extrair texto da página
            body_text = driver.execute_script("return document.body.innerText") or ""
            all_transcriptions[f'paroquial_{ark_id}'] = {
                'url': url,
                'body_preview': body_text[:3000],
                'method': 'screenshot'
            }
            
            log(f"    📸 Screenshot + texto ({len(body_text)} chars)")
            
        except Exception as e:
            log(f"    ❌ Erro: {str(e)[:80]}")
            all_transcriptions[f'paroquial_{ark_id}'] = {'url': url, 'error': str(e)[:200]}
        
        # Salvar incrementalmente
        if (i + 1) % 3 == 0 or i == len(sodre_arks_paroquial) - 1:
            with open(RESULTS_FILE, 'w') as f:
                json.dump(all_transcriptions, f, indent=2, ensure_ascii=False)
            log(f"  💾 Salvo progresso ({len(all_transcriptions)} total)")
        
        time.sleep(random.uniform(3, 5))
    
    # =============================================
    # SALVAR RESULTADOS FINAIS
    # =============================================
    with open(RESULTS_FILE, 'w') as f:
        json.dump(all_transcriptions, f, indent=2, ensure_ascii=False)
    
    log(f"\n✅ RESULTADOS FINAIS:")
    log(f"   Transcrições indexadas: {sum(1 for k in all_transcriptions if not k.startswith('paroquial_'))}")
    log(f"   Imagens paroquiais: {sum(1 for k in all_transcriptions if k.startswith('paroquial_'))}")
    log(f"   Arquivo: {RESULTS_FILE}")

except Exception as e:
    log(f"❌ Erro fatal: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        driver.save_screenshot(f'{DATA_DIR}/fs_extract_final.png')
    except: pass
    driver.quit()
    subprocess.run(['pkill', '-9', '-f', 'Xvfb :99'], capture_output=True)
    log("Encerrado.")