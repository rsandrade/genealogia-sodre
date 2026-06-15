#!/usr/bin/env python3
"""
FamilySearch — Extrair transcrições via navegação direta aos ARK links
Método: UC login → navegar a cada ARK → extrair innerText
Os ARKs 3:1:3Q9M (civil) já têm transcrição indexada no FS.
Os ARKs 3:1:33S7/33SQ (paroquiais) são imagens sem transcrição.
"""
import subprocess, time, json, os, sys, random, re
from pathlib import Path
from datetime import datetime

GENEALOGIA_DIR = '/home/hermes/genealogia'
DATA_DIR = f'{GENEALOGIA_DIR}/data'
IMAGES_DIR = f'{DATA_DIR}/images/amargosa_paroquiais'
LOG_FILE = f'{DATA_DIR}/fs_extract_transcriptions.log'
RESULTS_FILE = f'{DATA_DIR}/fs_transcriptions_results.json'
os.makedirs(IMAGES_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

# Credenciais
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

# Setup
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
        driver.get('https://ident.familysearch.org/en/identity/login/')
        time.sleep(8)

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

    for attempt in range(4):
        body_check = driver.execute_script("return document.body.innerText") or ""
        html_check = driver.execute_script("return document.body.innerHTML") or ""
        logged_in = any(kw in body_check.lower() for kw in ['sign out', 'sair'])
        if not logged_in:
            logged_in = 'sign out' in html_check.lower() or FS_USER[:5].lower() in body_check.lower()
        if logged_in:
            log("✅ Login bem-sucedido!")
            return True
        log(f"  ⏳ Verificando login... tentativa {attempt+1}")
        time.sleep(15)

    driver.save_screenshot(f'{DATA_DIR}/fs_login_failed.png')
    log("❌ Login falhou!")
    return False

try:
    if not do_login():
        sys.exit(1)

    # =============================================
    # CARREGAR ARKs DOS DADOS EXISTENTES
    # =============================================
    sodre_arks_transcription = set()
    sodre_arks_paroquial = set()

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
            except: pass

    # Remover duplicatas da execução anterior
    existing_results = {}
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE) as f:
                existing_results = json.load(f)
            log(f"📋 Carregados {len(existing_results)} resultados anteriores")
        except: pass

    all_transcriptions = existing_results
    sodre_arks_transcription = sorted(sodre_arks_transcription)
    sodre_arks_paroquial = sorted(sodre_arks_paroquial)

    log(f"📋 ARKs com transcrição: {len(sodre_arks_transcription)}")
    log(f"🖼️ ARKs paroquiais: {len(sodre_arks_paroquial)}")

    # =============================================
    # EXTRAIR TRANSCRIÇÕES VIA NAVEGAÇÃO DIRETA
    # =============================================
    all_arks = [(ark, 'civil') for ark in sodre_arks_transcription] + \
               [(ark, 'paroquial') for ark in sodre_arks_paroquial]

    for i, (ark_id, ark_type) in enumerate(all_arks):
        if ark_id in all_transcriptions or f'paroquial_{ark_id}' in all_transcriptions:
            log(f"[{i+1}/{len(all_arks)}] ⏭️ {ark_id} já extraído")
            continue

        url = f'https://www.familysearch.org/ark:/61903/{ark_id}'
        log(f"\n[{i+1}/{len(all_arks)}] {ark_type}: {ark_id}")

        try:
            driver.get(url)
            time.sleep(10)

            # Extrair innerText da página
            body_text = driver.execute_script("return document.body.innerText") or ""
            
            # Screenshot
            driver.save_screenshot(f'{IMAGES_DIR}/{ark_id.replace(":", "_")}.png')

            key = ark_id if ark_type == 'civil' else f'paroquial_{ark_id}'
            all_transcriptions[key] = {
                'url': url,
                'type': ark_type,
                'body_preview': body_text[:5000],
                'body_length': len(body_text),
                'method': 'navigation'
            }

            # Checar se tem dados relevantes
            has_data = len(body_text) > 500 and any(kw in body_text.lower() for kw in ['sodr', 'gramil', 'vaz', 'birth', 'death', 'marriage', 'nascimento', 'óbito', 'casamento'])
            log(f"    {'✅' if has_data else '⚠️'} {len(body_text)} chars {'(dados relevantes)' if has_data else '(poucos dados)'}")

        except Exception as e:
            log(f"    ❌ Erro: {str(e)[:80]}")
            key = ark_id if ark_type == 'civil' else f'paroquial_{ark_id}'
            all_transcriptions[key] = {'url': url, 'type': ark_type, 'error': str(e)[:200]}

        # Salvar incrementalmente a cada 3
        if (i + 1) % 3 == 0 or i == len(all_arks) - 1:
            with open(RESULTS_FILE, 'w') as f:
                json.dump(all_transcriptions, f, indent=2, ensure_ascii=False)
            log(f"  💾 Salvo {len(all_transcriptions)} entradas")

        time.sleep(random.uniform(3, 6))

    # =============================================
    # RESULTADOS FINAIS
    # =============================================
    with open(RESULTS_FILE, 'w') as f:
        json.dump(all_transcriptions, f, indent=2, ensure_ascii=False)

    civil_count = sum(1 for k in all_transcriptions if not k.startswith('paroquial_'))
    paroq_count = sum(1 for k in all_transcriptions if k.startswith('paroquial_'))
    
    log(f"\n✅ RESULTADOS FINAIS:")
    log(f"   Transcrições civis: {civil_count}")
    log(f"   Imagens paroquiais: {paroq_count}")
    log(f"   Arquivo: {RESULTS_FILE}")

except Exception as e:
    log(f"❌ Erro fatal: {e}")
    import traceback
    traceback.print_exc()
finally:
    try: driver.save_screenshot(f'{DATA_DIR}/fs_extract_final.png')
    except: pass
    driver.quit()
    subprocess.run(['pkill', '-9', '-f', 'Xvfb :99'], capture_output=True)
    log("Encerrado.")