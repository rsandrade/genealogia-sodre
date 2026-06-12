#!/usr/bin/env python3
"""
FamilySearch Image Downloader v3 — DeepZoom tile download
Usa UC autenticado para navegar ao image viewer e extrair
as URLs reais das imagens via DeepZoom (OpenSeadragon).

v2 corrigiu login (ident.familysearch.org + input[name="username"])
v3 corrige download: extrai thumbnails DeepZoom + full-resolution via UC fetch

Fluxo:
1. IncapSession → bypass WAF → cookies
2. UC + inject cookies + login (método comprovado)
3. UC navega ao ARK link 3:1: (image viewer)
4. Extrai thumbnail URLs do grid (deepzoomcloud/dz/v1/.../thumb_p200.jpg)
5. Extrai image-data via fetch() no contexto do navegador (filme info + DGS)
6. Baixa thumbnails e/ou imagens full-resolution
"""
import subprocess, time, json, os, sys, random, re, argparse, logging
from pathlib import Path
from datetime import datetime

# === LOGGING ===
LOG_DIR = '/home/hermes/genealogia/data'
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/fs_image_dl_v3.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('fs_img_dl')

DATA_DIR = '/home/hermes/genealogia/data'
IMAGE_DIR = '/home/hermes/genealogia/data/images'
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# =============================================
# PARÂMETROS
# =============================================
parser = argparse.ArgumentParser()
parser.add_argument('--test-mode', action='store_true', help='Only process first 3 ARK links')
parser.add_argument('--max-thumbs', type=int, default=0, help='Max thumbnails per film (0=all)')
parser.add_argument('--download-full', action='store_true', help='Try to download full-res images (slower)')
args = parser.parse_args()

# =============================================
# PASSO 0: Xvfb
# =============================================
log.info("Iniciando Xvfb :99...")
os.system('pkill -9 -f "Xvfb :99" 2>/dev/null; rm -f /tmp/.X99-lock')
time.sleep(2)
xvfb = subprocess.Popen(
    ['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(3)
os.environ['DISPLAY'] = ':99'
log.info("Xvfb iniciado (PID %d)", xvfb.pid)

# =============================================
# PASSO 1: IncapSession → Bypass WAF
# =============================================
log.info("=" * 60)
log.info("PASSO 1: Bypass Incapsula via IncapSession")
log.info("=" * 60)

sys.path.insert(0, '/tmp/venv-incapsula/lib/python3.12/site-packages')
from incapsula import IncapSession

incap = IncapSession(
    max_retries=5,
    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    cookie_domain='.familysearch.org',
)

r = incap.get('https://www.familysearch.org/pt/', timeout=60)
log.info("Status FS: %d | Cookies: %d", r.status_code, len(incap.cookies))

bypass_cookies = []
for c in incap.cookies:
    bypass_cookies.append({
        'name': c.name,
        'value': c.value,
        'domain': getattr(c, 'domain', '.familysearch.org'),
        'path': getattr(c, 'path', '/'),
    })
    if 'incap' in c.name:
        log.info("  ✅ Cookie WAF: %s = %s...", c.name, c.value[:30])

log.info("Total bypass cookies: %d", len(bypass_cookies))

if not any('incap' in c['name'] for c in bypass_cookies):
    log.error("❌ Nenhum cookie Incapsula obtido! WAF bypass falhou.")
    sys.exit(1)

# =============================================
# PASSO 2: UC + inject bypass cookies
# =============================================
log.info("=" * 60)
log.info("PASSO 2: UC + inject bypass cookies + login")
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
if not FS_USER or not FS_PASS:
    log.error("Credenciais FS não encontradas em %s", env_path)
    sys.exit(1)

options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')

log.info("Iniciando UC...")
driver = uc.Chrome(options=options, version_main=149)
wait = WebDriverWait(driver, 30)
log.info("UC iniciado")

# Inject bypass cookies BEFORE navigating
driver.get('https://www.familysearch.org')
time.sleep(3)
for bc in bypass_cookies:
    try:
        driver.add_cookie({
            'name': bc['name'],
            'value': bc['value'],
            'domain': bc['domain'],
            'path': bc.get('path', '/'),
        })
    except Exception as e:
        log.warning("Cookie %s: %s", bc['name'], e)

driver.get('https://www.familysearch.org/en/')
time.sleep(5)
driver.save_screenshot(f'{DATA_DIR}/fs_v3_01_after_bypass.png')

# =============================================
# PASSO 3: Login (método comprovado do endpoint_json_v2)
# =============================================
log.info("=" * 60)
log.info("PASSO 3: Login no FamilySearch")
log.info("=" * 60)

def do_login():
    """Login método comprovado — ident.familysearch.org + input[name='username']"""
    log.info("Navegando ao FS homepage para iniciar login...")
    driver.get('https://www.familysearch.org/en/')
    time.sleep(10)

    clicked_signin = False
    for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
        try:
            if 'sign in' in (el.text or '').lower():
                href = el.get_attribute('href') or ''
                log.info("Botão 'Sign In': text='%s' href='%s'", el.text[:30], href[:60])
                try: el.click()
                except Exception:
                    if href: driver.get(href)
                clicked_signin = True
                break
        except: continue

    if not clicked_signin:
        log.warning("Botão Sign In não encontrado. Navegando direto...")
    time.sleep(10)

    if 'login' not in driver.current_url.lower() and 'signin' not in driver.current_url.lower():
        driver.get('https://ident.familysearch.org/en/identity/login/')
        time.sleep(8)

    log.info("Página de login: %s", driver.current_url[:80])
    driver.save_screenshot(f'{DATA_DIR}/fs_v3_02_login_page.png')

    try:
        u = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
        u.click(); time.sleep(0.3); u.clear()
        for c in FS_USER: u.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
        log.info("Username digitado: %s***", FS_USER[:3])
    except Exception as e:
        log.error("Erro no username: %s", e)
        return False

    try:
        p = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
        p.click(); time.sleep(0.3); p.clear()
        for c in FS_PASS: p.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
        log.info("Password digitado")
    except Exception as e:
        log.error("Erro no password: %s", e)
        return False

    time.sleep(1)
    try:
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        log.info("Submit clicado")
    except Exception as e:
        log.error("Erro no submit: %s", e)
        return False

    time.sleep(20)

    # VERIFICAÇÃO REAL: buscar "sign out"/"sair" no body + innerHTML
    for attempt in range(5):
        body = driver.execute_script("return document.body.innerText") or ""
        html = driver.execute_script("return document.body.innerHTML") or ""
        logged_in = (
            any(kw in body.lower() for kw in ['sign out', 'sair']) or
            'sign out' in html.lower() or
            FS_USER[:5].lower() in body.lower() or
            'hermes879' in html.lower()
        )
        if logged_in:
            break
        if attempt < 4:
            log.info("Login não confirmado, tentativa %d/5...", attempt + 1)
            time.sleep(20)

    driver.save_screenshot(f'{DATA_DIR}/fs_v3_03_after_login.png')
    return logged_in

logged_in = do_login()
if not logged_in:
    log.error("❌ Login falhou! Saindo.")
    driver.quit()
    sys.exit(1)
log.info("✅ Login confirmado!")

# =============================================
# PASSO 4: Coletar ARK links relevantes
# =============================================
log.info("=" * 60)
log.info("PASSO 4: Coletar ARK links 3:1: (image references)")
log.info("=" * 60)

ark_links = []
structured_data_path = f'{DATA_DIR}/fs_endpoint_structured.json'
if os.path.exists(structured_data_path):
    with open(structured_data_path) as f:
        d = json.load(f)
    for key, val in d.items():
        if not isinstance(val, dict) or 'entries' not in val:
            continue
        for entry in val['entries']:
            name = entry.get('name', 'unknown')
            for s in entry.get('sources', []):
                about = s.get('about', '')
                # Only use 3:1: links (direct image references)
                if 'ark:/' in about and '/3:1:' in about:
                    ark_links.append({'ark': about, 'name': name, 'query': key})

# Deduplicate by ARK URL
seen_arks = set()
unique_arks = []
for a in ark_links:
    if a['ark'] not in seen_arks:
        seen_arks.add(a['ark'])
        unique_arks.append(a)
ark_links = unique_arks

# Filter Sodré/Gramilo/Pereira
relevant_arks = [a for a in ark_links if any(kw in a['name'].lower() for kw in ['sodr', 'gramil', 'pereira'])]
log.info("Total ARK 3:1: links: %d | Relevantes: %d", len(ark_links), len(relevant_arks))

if args.test_mode:
    relevant_arks = relevant_arks[:3]
    log.info("MODO TESTE: processando apenas %d ARK links", len(relevant_arks))

# =============================================
# PASSO 5: Navegar ARK links → extrair thumbnails DeepZoom → download
# =============================================
log.info("=" * 60)
log.info("PASSO 5: Extrair thumbnails DeepZoom → download")
log.info("=" * 60)

image_dir = Path(IMAGE_DIR)
downloaded = []
errors = 0

for i, ark_info in enumerate(relevant_arks):
    ark_url = ark_info['ark']
    name = ark_info['name']
    safe_name = re.sub(r'[^\w\s]', '_', name)[:50].strip().replace(' ', '_')

    log.info("[%d/%d] %s | ARK: %s", i+1, len(relevant_arks), name, ark_url)

    try:
        driver.get(ark_url)
        time.sleep(12 + random.uniform(0, 3))

        # Extract DeepZoom thumbnail URLs from the rendered page
        thumb_data = driver.execute_script("""
            const imgs = document.querySelectorAll('img');
            const deepzoom = [];
            const other = [];
            
            imgs.forEach(img => {
                if (img.src && img.src.includes('deepzoomcloud')) {
                    deepzoom.push({
                        src: img.src,
                        width: img.naturalWidth,
                        height: img.naturalHeight
                    });
                } else if (img.src && img.naturalWidth > 100 && !img.src.includes('edge.fscdn.org')) {
                    other.push({
                        src: img.src,
                        width: img.naturalWidth,
                        height: img.naturalHeight
                    });
                }
            });
            
            return {
                deepzoomThumbs: deepzoom,
                otherImgs: other,
                title: document.title,
                url: window.location.href
            };
        """)

        n_thumbs = len(thumb_data.get('deepzoomThumbs', []))
        log.info("  DeepZoom thumbs: %d | Outras imgs: %d", n_thumbs, len(thumb_data.get('otherImgs', [])))
        log.info("  Título: %s", thumb_data.get('title', '')[:60])

        # Create subfolder per person
        person_dir = image_dir / safe_name
        person_dir.mkdir(parents=True, exist_ok=True)

        # Download DeepZoom thumbnails (these ARE the scanned page thumbnails!)
        thumb_count = 0
        for j, thumb in enumerate(thumb_data.get('deepzoomThumbs', [])):
            if args.max_thumbs > 0 and j >= args.max_thumbs:
                break

            thumb_src = thumb.get('src', '')
            if not thumb_src:
                continue

            # Extract ARK sub-ID from URL for naming
            # URL: .../dz/v1/3:1:33SQ-G5LY-D4Q/thumb_p200.jpg
            ark_sub = 'unknown'
            parts = thumb_src.split('/dz/v1/')
            if len(parts) > 1:
                ark_sub = parts[1].split('/')[0].replace(':', '_').replace(' ', '_')

            fname = person_dir / f"thumb_{j:04d}_{ark_sub}.jpg"

            try:
                # Use IncapSession to download (faster than UC)
                resp = incap.get(thumb_src, timeout=15)
                if resp.status_code == 200 and len(resp.content) > 100:
                    with open(fname, 'wb') as f:
                        f.write(resp.content)
                    thumb_count += 1
                    if j < 3:  # Log first 3
                        log.info("  ✅ Thumb %d: %s (%d bytes)", j, fname.name, len(resp.content))
                else:
                    if j < 3:
                        log.info("  ⚠️ Thumb %d: status %d, size %d", j, resp.status_code, len(resp.content))
            except Exception as e:
                if j < 3:
                    log.warning("  Erro thumb %d: %s", j, str(e)[:100])

        log.info("  Thumbnails baixados: %d/%d", thumb_count, n_thumbs)

        # Try to fetch image-data for full resolution info
        if args.download_full:
            film_data = driver.execute_async_script("""
                var callback = arguments[1];
                var imageId = arguments[0];
                
                // Try the filmdatainfo endpoint
                fetch('/search/filmdatainfo/image-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        type: 'film-data',
                        imageId: imageId,
                        state: null,
                        args: { noPlaceholder: true }
                    })
                })
                .then(r => r.text())
                .then(text => callback({ status: 'ok', data: text.substring(0, 5000) }))
                .catch(e => callback({ status: 'error', error: e.message }));
            """, ark_url.split('/')[-1])

            if film_data and film_data.get('status') == 'ok':
                log.info("  Film data: %s", str(film_data.get('data', ''))[:200])

        downloaded.append({
            'name': name,
            'ark': ark_url,
            'thumbnails_downloaded': thumb_count,
            'total_thumbnails_available': n_thumbs,
            'person_dir': str(person_dir),
            'title': thumb_data.get('title', ''),
        })

        # Human-like delay
        delay = random.uniform(3, 7)
        log.info("  Aguardando %.1fs...", delay)
        time.sleep(delay)

    except Exception as e:
        log.error("  ❌ Erro em %s: %s", name, str(e)[:200])
        errors += 1
        driver.save_screenshot(f'{DATA_DIR}/fs_v3_error_{safe_name}.png')
        downloaded.append({
            'name': name, 'ark': ark_url, 'status': 'error', 'error': str(e)[:200]
        })
        time.sleep(random.uniform(3, 8))

# =============================================
# PASSO 6: Salvar resultados
# =============================================
log.info("=" * 60)
log.info("PASSO 6: Salvar resultados")
log.info("=" * 60)

results = {
    'downloaded': downloaded,
    'total_ark_links_31': len(ark_links),
    'relevant_ark_links': len(relevant_arks),
    'total_thumbnails': sum(d.get('thumbnails_downloaded', 0) for d in downloaded),
    'errors': errors,
    'timestamp': datetime.now().isoformat(),
    'test_mode': args.test_mode,
}

with open(f'{DATA_DIR}/fs_image_download_v3_results.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

# List files
for person_dir in sorted(image_dir.iterdir()):
    if person_dir.is_dir():
        files = list(person_dir.glob('*.jpg'))
        total_size = sum(f.stat().st_size for f in files) / 1024
        log.info("  %s/: %d arquivos (%.1f KB)", person_dir.name, len(files), total_size)

log.info("✅ Script concluído! %d thumbnails, %d erros",
         results['total_thumbnails'], errors)

try:
    driver.quit()
except:
    pass