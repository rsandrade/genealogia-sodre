#!/usr/bin/env python3
"""
FamilySearch Full-Resolution Image Downloader — via UC autenticado
Usa a sessão autenticada do UC para acessar imagens full-resolution
que exigem autenticação (401 sem sessão).

Fluxo:
1. IncapSession → bypass WAF
2. UC + login (método comprovado)
3. Navega ao ARK 3:1: link → extrai IDs DeepZoom
4. UC fetch() no contexto do navegador → baixa imagens full/resolução
5. Salva em data/images/<pessoa>/
"""
import subprocess, time, json, os, sys, random, re, argparse, logging, base64
from pathlib import Path
from datetime import datetime

# === LOGGING ===
LOG_DIR = '/home/hermes/genealogia/data'
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/fs_fullres_dl.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('fs_fullres')

DATA_DIR = '/home/hermes/genealogia/data'
IMAGE_DIR = '/home/hermes/genealogia/data/images'
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--test-mode', action='store_true', help='Only process first 2 ARK links, first 5 pages')
parser.add_argument('--max-pages', type=int, default=0, help='Max pages per film (0=all)')
parser.add_argument('--resolution', choices=['thumb', 'medium', 'full', 'original'], default='full',
                    help='Image resolution to download')
args = parser.parse_args()

# =============================================
# PASSO 0: Xvfb
# =============================================
log.info("Iniciando Xvfb :99...")
os.system('pkill -9 -f "Xvfb :99" 2>/dev/null; rm -f /tmp/.X99-lock')
time.sleep(2)
xvfb = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
os.environ['DISPLAY'] = ':99'

# =============================================
# PASSO 1: IncapSession bypass WAF
# =============================================
log.info("=" * 60)
log.info("PASSO 1: Bypass Incapsula")
log.info("=" * 60)
sys.path.insert(0, '/tmp/venv-incapsula/lib/python3.12/site-packages')
from incapsula import IncapSession

incap = IncapSession(max_retries=5,
    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    cookie_domain='.familysearch.org')

r = incap.get('https://www.familysearch.org/pt/', timeout=60)
log.info("Status FS: %d | Cookies: %d", r.status_code, len(incap.cookies))

bypass_cookies = []
for c in incap.cookies:
    bypass_cookies.append({'name': c.name, 'value': c.value,
        'domain': getattr(c, 'domain', '.familysearch.org'),
        'path': getattr(c, 'path', '/')})

if not any('incap' in c['name'] for c in bypass_cookies):
    log.error("❌ WAF bypass falhou!"); sys.exit(1)

# =============================================
# PASSO 2: UC + inject cookies
# =============================================
log.info("=" * 60)
log.info("PASSO 2: UC + login")
log.info("=" * 60)

import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

env_path = '/home/hermes/genealogia/.env'
with open(env_path) as f:
    creds = {}
    for line in f.read().strip().split('\n'):
        if '=' in line:
            k, v = line.split('=', 1)
            creds[k.strip()] = v.strip()

FS_USER = creds.get('FS_USER', '')
FS_PASS = creds.get('FS_PASS', '')

options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-gpu')

driver = uc.Chrome(options=options, version_main=149)
wait = WebDriverWait(driver, 30)

# Inject bypass cookies
driver.get('https://www.familysearch.org')
time.sleep(3)
for bc in bypass_cookies:
    try: driver.add_cookie(bc)
    except: pass
driver.get('https://www.familysearch.org/en/')
time.sleep(5)

# =============================================
# PASSO 3: Login (método comprovado)
# =============================================
log.info("=" * 60)
log.info("PASSO 3: Login")
log.info("=" * 60)

for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
    try:
        if 'sign in' in (el.text or '').lower():
            try: el.click()
            except: driver.get(el.get_attribute('href') or '')
            break
    except: continue
time.sleep(10)
if 'login' not in driver.current_url.lower() and 'signin' not in driver.current_url.lower():
    driver.get('https://ident.familysearch.org/en/identity/login/')
    time.sleep(8)

u = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
u.click(); time.sleep(0.3); u.clear()
for c in FS_USER: u.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
p = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
p.click(); time.sleep(0.3); p.clear()
for c in FS_PASS: p.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
time.sleep(1)
driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
time.sleep(20)

# VERIFICAÇÃO ROBUSTA
logged_in = False
for _ in range(5):
    body = driver.execute_script("return document.body.innerText") or ""
    html = driver.execute_script("return document.body.innerHTML") or ""
    if (any(kw in body.lower() for kw in ['sign out', 'sair']) or
        'sign out' in html.lower() or FS_USER[:5].lower() in body.lower()):
        logged_in = True; break
    time.sleep(20)

if not logged_in:
    log.error("❌ Login falhou!"); driver.quit(); sys.exit(1)
log.info("✅ Login confirmado!")

# =============================================
# PASSO 4: Coletar ARK links
# =============================================
log.info("=" * 60)
log.info("PASSO 4: Coletar ARK links 3:1:")
log.info("=" * 60)

ark_links = []
with open(f'{DATA_DIR}/fs_endpoint_structured.json') as f:
    d = json.load(f)
for key, val in d.items():
    if not isinstance(val, dict) or 'entries' not in val: continue
    for entry in val['entries']:
        name = entry.get('name', 'unknown')
        for s in entry.get('sources', []):
            about = s.get('about', '')
            if 'ark:/' in about and '/3:1:' in about:
                ark_links.append({'ark': about, 'name': name, 'query': key})

seen = set(); unique = []
for a in ark_links:
    if a['ark'] not in seen: seen.add(a['ark']); unique.append(a)
ark_links = unique

relevant = [a for a in ark_links if any(kw in a['name'].lower() for kw in ['sodr', 'gramil', 'pereira'])]
log.info("Total ARK 3:1: %d | Relevantes: %d", len(ark_links), len(relevant))

if args.test_mode:
    relevant = relevant[:2]
    log.info("MODO TESTE: %d ARK links", len(relevant))

# =============================================
# PASSO 5: Navegar + extrair + download full-res via UC
# =============================================
log.info("=" * 60)
log.info("PASSO 5: Download imagens via UC autenticado")
log.info("=" * 60)

# Resolution mapping for URL construction
RES_MAP = {
    'thumb': 'thumb_p200.jpg',
    'medium': 'medium.jpg',
    'full': 'full.jpg',
    'original': 'original.jpg',
}
res_suffix = RES_MAP.get(args.resolution, 'full.jpg')

downloaded_count = 0
errors = 0
results = []

for i, ark_info in enumerate(relevant):
    ark_url = ark_info['ark']
    name = ark_info['name']
    safe_name = re.sub(r'[^\w\s]', '_', name)[:50].strip().replace(' ', '_')

    log.info("[%d/%d] %s | ARK: %s", i+1, len(relevant), name, ark_url[:60])

    try:
        driver.get(ark_url)
        time.sleep(12 + random.uniform(0, 3))

        # Extract DeepZoom image IDs from the page
        img_ids = driver.execute_script("""
            const imgs = document.querySelectorAll('img');
            const ids = [];
            imgs.forEach(img => {
                if (img.src && img.src.includes('deepzoomcloud')) {
                    // Extract: .../dz/v1/3:1:33SQ-G5LY-D4Q/thumb_p200.jpg
                    const parts = img.src.split('/dz/v1/');
                    if (parts.length > 1) {
                        const arkPart = parts[1].split('/')[0];
                        ids.push(arkPart);
                    }
                }
            });
            // Deduplicate
            return [...new Set(ids)];
        """)

        n_ids = len(img_ids)
        log.info("  DeepZoom IDs: %d", n_ids)

        if args.test_mode:
            img_ids = img_ids[:5]
            log.info("  MODO TESTE: processando %d imagens", len(img_ids))

        person_dir = Path(IMAGE_DIR) / safe_name
        person_dir.mkdir(parents=True, exist_ok=True)

        page_count = 0
        for j, img_id in enumerate(img_ids):
            if args.max_pages > 0 and j >= args.max_pages:
                break

            # Construct full-res URL
            base_url = f'https://sg30p0.familysearch.org/service/records/storage/deepzoomcloud/dz/v1/{img_id}'

            if args.resolution == 'thumb':
                # Thumbnails don't need auth — use IncapSession (faster)
                url = f'{base_url}/thumb_p200.jpg'
                try:
                    resp = incap.get(url, timeout=15)
                    if resp.status_code == 200 and len(resp.content) > 100:
                        fname = person_dir / f"thumb_{j:04d}_{img_id.replace(':','_')}.jpg"
                        with open(fname, 'wb') as f: f.write(resp.content)
                        page_count += 1
                        if j < 3: log.info("  ✅ Thumb %d: %s (%d B)", j, fname.name, len(resp.content))
                    else:
                        if j < 3: log.info("  ⚠️ Thumb %d: status=%d size=%d", j, resp.status_code, len(resp.content))
                except Exception as e:
                    if j < 3: log.warning("  Erro thumb %d: %s", j, str(e)[:80])
            else:
                # Full-res needs auth — use UC fetch()
                safe_id = img_id.replace(':', '_').replace(' ', '_')
                fname = person_dir / f"{args.resolution}_{j:04d}_{safe_id}.jpg"

                # Use fetch() inside the authenticated browser session
                download_result = driver.execute_async_script("""
                    var callback = arguments[2];
                    var baseUrl = arguments[0];
                    var resSuffix = arguments[1];
                    
                    var url = baseUrl + '/' + resSuffix;
                    
                    fetch(url, {
                        method: 'GET',
                        credentials: 'include',
                        headers: { 'Accept': 'image/jpeg' }
                    })
                    .then(response => {
                        if (!response.ok) {
                            callback({status: 'error', code: response.status, msg: 'HTTP ' + response.status});
                            return null;
                        }
                        return response.blob();
                    })
                    .then(blob => {
                        if (!blob) return;
                        // Convert blob to base64 for transfer
                        var reader = new FileReader();
                        reader.onloadend = function() {
                            callback({
                                status: 'ok',
                                size: blob.size,
                                type: blob.type,
                                data: reader.result  // data:image/jpeg;base64,...
                            });
                        };
                        reader.readAsDataURL(blob);
                    })
                    .catch(e => callback({status: 'error', msg: e.message}));
                """, base_url, res_suffix)

                if download_result and download_result.get('status') == 'ok':
                    data_url = download_result.get('data', '')
                    if data_url and 'base64,' in data_url:
                        b64_data = data_url.split('base64,')[1]
                        img_bytes = base64.b64decode(b64_data)
                        with open(fname, 'wb') as f: f.write(img_bytes)
                        page_count += 1
                        downloaded_count += 1
                        if j < 3:
                            log.info("  ✅ %s %d: %s (%d B, type=%s)",
                                     args.resolution, j, fname.name, len(img_bytes),
                                     download_result.get('type', ''))
                    else:
                        if j < 3: log.info("  ⚠️ %s %d: sem dados base64", args.resolution, j)
                else:
                    err_info = download_result or {}
                    if j < 3:
                        log.info("  ⚠️ %s %d: %s (code=%s)",
                                 args.resolution, j,
                                 err_info.get('msg', 'unknown'),
                                 err_info.get('code', '?'))
                    # Fallback: try thumbnail
                    if args.resolution != 'thumb':
                        thumb_url = f'{base_url}/thumb_p200.jpg'
                        try:
                            resp = incap.get(thumb_url, timeout=10)
                            if resp.status_code == 200 and len(resp.content) > 100:
                                thumb_fname = person_dir / f"thumb_{j:04d}_{safe_id}.jpg"
                                with open(thumb_fname, 'wb') as f: f.write(resp.content)
                                page_count += 1
                                if j < 3: log.info("  ↳ Fallback thumb: %s (%d B)", thumb_fname.name, len(resp.content))
                        except: pass

            # Human-like delay
            time.sleep(random.uniform(2, 5))

        results.append({
            'name': name,
            'ark': ark_url,
            'pages_downloaded': page_count,
            'total_pages_available': n_ids,
            'person_dir': str(person_dir),
        })
        log.info("  Páginas baixadas: %d/%d", page_count, n_ids)
        time.sleep(random.uniform(3, 7))

    except Exception as e:
        log.error("  ❌ Erro: %s", str(e)[:200])
        errors += 1
        results.append({'name': name, 'ark': ark_url, 'status': 'error', 'error': str(e)[:200]})
        time.sleep(random.uniform(3, 8))

# =============================================
# PASSO 6: Resultados
# =============================================
log.info("=" * 60)
log.info("PASSO 6: Resultados")
log.info("=" * 60)

summary = {
    'resolution': args.resolution,
    'downloaded': downloaded_count,
    'results': results,
    'errors': errors,
    'timestamp': datetime.now().isoformat(),
    'test_mode': args.test_mode,
}

with open(f'{DATA_DIR}/fs_fullres_results.json', 'w') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

# List files
total_files = 0
total_size = 0
for person_dir in sorted(Path(IMAGE_DIR).iterdir()):
    if person_dir.is_dir():
        files = list(person_dir.glob('*.jpg'))
        sz = sum(f.stat().st_size for f in files)
        total_files += len(files)
        total_size += sz
        log.info("  %s/: %d arquivos (%.1f KB)", person_dir.name, len(files), sz/1024)

log.info("✅ TOTAL: %d arquivos (%.1f KB) | %d erros", total_files, total_size/1024, errors)

try: driver.quit()
except: pass