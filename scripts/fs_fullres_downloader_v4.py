#!/usr/bin/env python3
"""
FamilySearch Full-Resolution Image Downloader v4 — FINAL
========================================================
Método comprovado: UC autenticado + CDP auto-download + botão Download
Baixa imagens full-resolution (~1.1 MB) e transcrições indexadas de cada ARK link.

Uso:
  python3 fs_fullres_downloader_v4.py [--max-images 10] [--test-mode] [--output-dir data/images/fullres]

  --max-images  Máximo de imagens (default: 10, 0 = todas)
  --test-mode   Baixar 1 imagem e parar
  --output-dir  Diretório de saída
"""
import subprocess, time, json, os, sys, random, argparse
from pathlib import Path
from datetime import datetime

GENEALOGIA_DIR = '/home/hermes/genealogia'
DATA_DIR = f'{GENEALOGIA_DIR}/data'
sys.path.insert(0, '/tmp/venv-incapsula/lib/python3.12/site-packages')

parser = argparse.ArgumentParser(description='FS Full-Resolution Image Downloader v4')
parser.add_argument('--max-images', type=int, default=10, help='Max images (0=all)')
parser.add_argument('--test-mode', action='store_true', help='Download 1 image and stop')
parser.add_argument('--output-dir', default=f'{DATA_DIR}/images/fullres', help='Output directory')
parser.add_argument('--skip-existing', action='store_true', help='Skip images already downloaded')
args = parser.parse_args()
if args.test_mode:
    args.max_images = 1
os.makedirs(args.output_dir, exist_ok=True)

LOG_FILE = f'{DATA_DIR}/fs_fullres_v4.log'
RESULTS_FILE = f'{DATA_DIR}/fs_fullres_v4_results.json'

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

# =============================================
# LOAD CREDENTIALS
# =============================================
with open(f'{GENEALOGIA_DIR}/.env') as f:
    creds = {}
    for line in f.read().strip().split('\n'):
        if '=' in line:
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip()
FS_USER = creds.get('FS_USER', '')
FS_PASS = creds.get('FS_PASS', '')
if not FS_USER or not FS_PASS:
    log("❌ Credenciais FS não encontradas em .env"); sys.exit(1)

# =============================================
# LOAD ARK LINKS
# =============================================
with open(f'{DATA_DIR}/fs_endpoint_structured.json') as f:
    data = json.load(f)

# Extract ALL 3:1: ARK links, then filter to church records (33S7, 33SQ)
import re
all_arks = set()
for key, val in data.items():
    if isinstance(val, (dict, list)):
        s = json.dumps(val, ensure_ascii=False)
        arks = re.findall(r'3:1:[A-Za-z0-9-]+', s)
        for a in arks:
            a = a.split('?')[0]
            all_arks.add(a)

# Priority: 33S7 and 33SQ = Catholic church records from Bahia
ark_links = sorted([f'https://www.familysearch.org/ark:/61903/{a}' 
                     for a in all_arks if a.startswith('3:1:33S7') or a.startswith('3:1:33SQ')])
log(f"ARK 3:1:33S*+33SQ* links (registros paroquiais BA): {len(ark_links)}")
if args.max_images > 0:
    ark_links = ark_links[:args.max_images]
    log(f"Limitado a {args.max_images} imagens")

# =============================================
# Xvfb + UC SETUP
# =============================================
os.system('pkill -9 -f "Xvfb :99" 2>/dev/null; rm -f /tmp/.X99-lock')
time.sleep(2)
xvfb = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
os.environ['DISPLAY'] = ':99'

from incapsula import IncapSession
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# =============================================
# WAF BYPASS + LOGIN
# =============================================
log("PASSO 1: WAF bypass (IncapSession)")
incap = IncapSession(max_retries=5, cookie_domain='.familysearch.org')
r = incap.get('https://www.familysearch.org/pt/', timeout=60)
log(f"IncapSession: {r.status_code}, {len(incap.cookies)} cookies")
bypass_cookies = [{'name': c.name, 'value': c.value, 'domain': getattr(c, 'domain', '.familysearch.org'), 'path': getattr(c, 'path', '/')} for c in incap.cookies]

log("PASSO 2: UC + Login")
options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-gpu')
prefs = {
    'download.default_directory': os.path.abspath(args.output_dir),
    'download.prompt_for_download': False,
    'download.directory_upgrade': True,
    'safebrowsing.enabled': True,
    'safebrowsing.disable_download_protection': True,
}
options.add_experimental_option('prefs', prefs)
driver = uc.Chrome(options=options, version_main=149)
wait = WebDriverWait(driver, 30)

# Inject WAF cookies
driver.get('https://www.familysearch.org')
time.sleep(random.uniform(3, 5))
for bc in bypass_cookies:
    try: driver.add_cookie(bc)
    except: pass
driver.get('https://www.familysearch.org/en/')
time.sleep(random.uniform(5, 8))

# Click Sign In
for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
    try:
        if 'sign in' in (el.text or '').lower():
            try: el.click()
            except: driver.get(el.get_attribute('href') or '')
            break
    except: continue
time.sleep(random.uniform(10, 15))
if 'login' not in driver.current_url.lower():
    driver.get('https://ident.familysearch.org/en/identity/login/')
    time.sleep(random.uniform(8, 12))

# Type credentials char-by-char
u = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
u.click(); time.sleep(random.uniform(0.2, 0.5)); u.clear()
for c in FS_USER: u.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
time.sleep(random.uniform(0.5, 1.0))
p = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
p.click(); time.sleep(random.uniform(0.2, 0.5)); p.clear()
for c in FS_PASS: p.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
time.sleep(random.uniform(0.5, 1.5))
driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
time.sleep(random.uniform(15, 20))

# Verify login
body = driver.execute_script('return document.body.innerText') or ''
html = driver.execute_script('return document.body.innerHTML') or ''
logged_in = any(kw in body.lower() for kw in ['sign out', 'sair']) or 'sign out' in html.lower()
log(f"Login: {'OK' if logged_in else 'FALHOU'}")
if not logged_in:
    driver.save_screenshot(f'{args.output_dir}/login_failed.png')
    driver.quit(); sys.exit(1)

# CDP: set download behavior
try:
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': os.path.abspath(args.output_dir)
    })
except: pass

# =============================================
# DOWNLOAD IMAGES + TRANSCRIPTIONS
# =============================================
log(f"PASSO 3: Download de {len(ark_links)} imagens + transcrições")

results = {
    'started': datetime.now().isoformat(),
    'total_arks': len(ark_links),
    'downloads': [],
    'transcriptions': [],
    'errors': [],
}

def dismiss_modals(driver):
    """Dismiss cookie banner + modal 'We've Updated'"""
    try:
        for btn in driver.find_elements(By.CSS_SELECTOR, 'button'):
            txt = (btn.text or '').lower()
            if 'accept' in txt or 'decline' in txt:
                btn.click(); time.sleep(random.uniform(1, 2)); break
    except: pass
    driver.execute_script("""
        const btns = document.querySelectorAll('button, [role="button"]');
        for (const btn of btns) {
            const text = (btn.textContent || '').trim().toLowerCase();
            const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
            if (text.includes('ok') || text === '×' || text.includes('close') || 
                text.includes('done') || aria.includes('close')) {
                btn.click(); break;
            }
        }
        document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', keyCode: 27}));
    """)
    time.sleep(random.uniform(1, 2))

def extract_transcription(driver):
    """Extract indexed transcription data from the FS record page.
    The Image Index panel on the ARK page shows indexed fields."""
    return driver.execute_script("""
        const text = document.body.innerText;
        
        // Look for the Image Index section which has indexed data
        const fields = ['Name', 'Sex', 'Event Type', 'Event Date', 'Event Place',
                       'Birth Date', 'Birthplace', 'Father', 'Mother', 'Spouse',
                       'Padrinho', 'Madrinha', 'Christening Date', 'Death Date',
                       'Marriage Date', 'Residence Place', 'Age', 'Occupation',
                       'Certificate Number'];
        
        const data = {};
        for (const field of fields) {
            const idx = text.indexOf(field + '\\n');
            if (idx === -1) continue;
            // Get the value after the field label (next non-empty line)
            const after = text.substring(idx + field.length + 1, idx + field.length + 150);
            const value = after.split('\\n').filter(l => l.trim() && l.trim() !== 'More' && l.trim() !== 'ATTACH')[0];
            if (value && value.trim()) {
                data[field] = value.trim();
            }
        }
        
        // Extract ARK ID from URL
        const arkMatch = window.location.href.match(/3:1:[A-Za-z0-9-]+/);
        data._ark = arkMatch ? arkMatch[0] : window.location.href.substring(0, 80);
        
        // Extract film info
        const filmMatch = text.match(/Film #?\\s*(\\d+)/);
        data._film = filmMatch ? filmMatch[1] : '';
        
        // Extract image number
        const imageMatch = text.match(/Image (\\d+ of \\d+)/i);
        data._image = imageMatch ? imageMatch[1] : '';
        
        // Get title
        data._title = document.title.substring(0, 100);
        
        // Check for "Restricted" or "no access" messages
        data._restricted = text.toLowerCase().includes('restricted') || 
                          text.toLowerCase().includes('no access') ||
                          text.toLowerCase().includes('contract');
        
        return data;
    """)

def wait_for_download(output_dir, existing_files, timeout=60):
    """Wait for a new file to appear in the download directory"""
    start = time.time()
    while time.time() - start < timeout:
        current = set(Path(output_dir).glob('*'))
        new = current - existing_files
        # Filter for actual image files (>50KB, not screenshots)
        new_images = [f for f in new if f.stat().st_size > 50000 and f.suffix in ('.jpg', '.jpeg', '.avif', '.png')]
        if new_images:
            # Wait for file size to stabilize
            newest = max(new_images, key=lambda f: f.stat().st_mtime)
            prev_size = 0
            for _ in range(5):
                size = newest.stat().st_size
                if size == prev_size and size > 1000:
                    return newest
                prev_size = size
                time.sleep(1)
            return newest
        time.sleep(2)
    return None

for i, ark in enumerate(ark_links):
    # Normalize ARK link (remove query params)
    ark_base = ark.split('?')[0]
    ark_id = ark_base.split('3:1:')[1] if '3:1:' in ark_base else f'unknown_{i}'
    
    # Check if already downloaded
    existing_jpg = Path(args.output_dir) / f'{ark_id}.jpg'
    if args.skip_existing and existing_jpg.exists() and existing_jpg.stat().st_size > 50000:
        log(f"  [{i+1}/{len(ark_links)}] ⏭️ {ark_id} já existe ({existing_jpg.stat().st_size:,} bytes)")
        results['downloads'].append({'ark': ark_base, 'ark_id': ark_id, 'filename': existing_jpg.name, 'size': existing_jpg.stat().st_size, 'skipped': True})
        continue
    
    log(f"\n  [{i+1}/{len(ark_links)}] ARK: 3:1:{ark_id}")
    
    try:
        driver.get(ark_base)
        time.sleep(random.uniform(12, 18))
        
        dismiss_modals(driver)
        
        # STEP A: Extract transcription BEFORE clicking download
        transcription = extract_transcription(driver)
        has_data = any(k for k in transcription.keys() if not k.startswith('_') and transcription.get(k))
        
        if has_data:
            fields = [k for k in transcription.keys() if not k.startswith('_') and transcription.get(k)]
            log(f"    📝 Transcrição: {fields}")
            log(f"       Name={transcription.get('Name','?')}, Date={transcription.get('Event Date','?')}, Place={transcription.get('Event Place','?')}")
            transcription['_url'] = ark_base
            transcription['_timestamp'] = datetime.now().isoformat()
            results['transcriptions'].append(transcription)
        else:
            log(f"    ⚠️ Sem transcrição indexada (film={transcription.get('_film','?')}, image={transcription.get('_image','?')})")
            transcription['_url'] = ark_base
            transcription['_timestamp'] = datetime.now().isoformat()
            results['transcriptions'].append(transcription)
        
        # Check if restricted
        if transcription.get('_restricted'):
            log(f"    🔒 Imagem com acesso restrito — pulando download")
            results['errors'].append({'ark': ark_base, 'ark_id': ark_id, 'error': 'restricted_access'})
            continue
        
        # STEP B: Download image
        existing = set(Path(args.output_dir).glob('*'))
        
        clicked = driver.execute_script("""
            var btns = document.querySelectorAll('button');
            for (var btn of btns) {
                var aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                if (aria === 'download') { 
                    if (btn.disabled || btn.classList.contains('disabled')) return 'disabled';
                    btn.click(); return true; 
                }
            }
            return false;
        """)
        
        if clicked == 'disabled':
            log(f"    🔒 Botão Download desabilitado (restrição de contrato)")
            driver.save_screenshot(f'{args.output_dir}/restricted_{ark_id}.png')
            results['errors'].append({'ark': ark_base, 'ark_id': ark_id, 'error': 'download_disabled_contract'})
            continue
        elif not clicked:
            log(f"    ❌ Botão Download não encontrado")
            driver.save_screenshot(f'{args.output_dir}/no_download_{ark_id}.png')
            results['errors'].append({'ark': ark_base, 'ark_id': ark_id, 'error': 'download_button_not_found'})
            continue
        
        # Wait for download
        time.sleep(random.uniform(2, 5))
        new_file = wait_for_download(args.output_dir, existing, timeout=60)
        
        if new_file:
            size = new_file.stat().st_size
            log(f"    ✅ {new_file.name}: {size:,} bytes ({size/1024:.0f} KB)")
            # Rename to ARK ID for consistency
            target = Path(args.output_dir) / f'{ark_id}.jpg'
            if new_file != target and not target.exists():
                new_file.rename(target)
                log(f"    📝 Renomeado: {new_file.name} → {target.name}")
            results['downloads'].append({
                'ark': ark_base, 'ark_id': ark_id, 'filename': target.name,
                'size': size, 'timestamp': datetime.now().isoformat()
            })
        else:
            log(f"    ❌ Download não detectado após 60s")
            driver.save_screenshot(f'{args.output_dir}/timeout_{ark_id}.png')
            results['errors'].append({'ark': ark_base, 'ark_id': ark_id, 'error': 'download_timeout'})
        
        # Human-like delay
        if i < len(ark_links) - 1:
            delay = random.uniform(20, 40)
            log(f"    ⏳ Aguardando {delay:.0f}s...")
            time.sleep(delay)
    
    except Exception as e:
        log(f"    ❌ Erro: {e}")
        results['errors'].append({'ark': ark_base, 'ark_id': ark_id, 'error': str(e)})
        time.sleep(random.uniform(10, 20))

# =============================================
# SAVE TRANSCRIPTIONS SEPARATELY
# =============================================
transcription_file = f'{DATA_DIR}/fs_transcriptions.json'
with open(transcription_file, 'w') as f:
    json.dump(results['transcriptions'], f, ensure_ascii=False, indent=2)
log(f"\n📝 Transcrições salvas em: {transcription_file}")

# Save results
results['finished'] = datetime.now().isoformat()
results['success_count'] = len(results['downloads'])
results['error_count'] = len(results['errors'])
results['transcription_count'] = len(results['transcriptions'])

with open(RESULTS_FILE, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

log(f"\n✅ Concluído: {results['success_count']} downloads, {results['transcription_count']} transcrições, {results['error_count']} erros")
log(f"Resultados: {RESULTS_FILE}")

try: driver.quit()
except: pass
os.system('pkill -9 -f "Xvfb :99" 2>/dev/null')