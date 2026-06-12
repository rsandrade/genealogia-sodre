#!/usr/bin/env python3
"""
FamilySearch Image Viewer Diagnostic — entender como o FS carrega imagens.
Navega a um ARK link 3:1:, clica em "View Original Document", e captura
todos os recursos carregados (Performance API + DOM inspection).

Objetivo: descobrir a URL real da imagem escaneada do microfilme.
"""
import subprocess, time, json, os, sys, random

# Xvfb
os.system('pkill -9 -f "Xvfb :99" 2>/dev/null; rm -f /tmp/.X99-lock')
time.sleep(2)
xvfb = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1920x1080x24'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
os.environ['DISPLAY'] = ':99'

# IncapSession
sys.path.insert(0, '/tmp/venv-incapsula/lib/python3.12/site-packages')
from incapsula import IncapSession
incap = IncapSession(max_retries=5, cookie_domain='.familysearch.org')
r = incap.get('https://www.familysearch.org/pt/', timeout=60)
print(f"IncapSession: {r.status_code}, {len(incap.cookies)} cookies")

bypass_cookies = []
for c in incap.cookies:
    bypass_cookies.append({'name': c.name, 'value': c.value,
        'domain': getattr(c, 'domain', '.familysearch.org'),
        'path': getattr(c, 'path', '/')})

# UC
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

# Login (método comprovado)
for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
    try:
        if 'sign in' in (el.text or '').lower():
            try: el.click()
            except: driver.get(el.get_attribute('href') or '')
            break
    except: continue
time.sleep(10)
if 'login' not in driver.current_url.lower():
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

body = driver.execute_script("return document.body.innerText") or ""
html = driver.execute_script("return document.body.innerHTML") or ""
logged_in = (
    any(kw in body.lower() for kw in ['sign out', 'sair']) or
    'sign out' in html.lower() or
    FS_USER[:5].lower() in body.lower() or
    'hermes879' in html.lower()
)
if not logged_in:
    for _ in range(3):
        time.sleep(20)
        body = driver.execute_script("return document.body.innerText") or ""
        html = driver.execute_script("return document.body.innerHTML") or ""
        if (any(kw in body.lower() for kw in ['sign out', 'sair']) or
            'sign out' in html.lower() or
            FS_USER[:5].lower() in body.lower() or
            'hermes879' in html.lower()):
            logged_in = True; break
print(f"Login: {'OK' if logged_in else 'FALHOU'}")
if not logged_in:
    driver.save_screenshot('/home/hermes/genealogia/data/fs_diag_login.png')
    driver.quit(); sys.exit(1)

driver.save_screenshot('/home/hermes/genealogia/data/fs_diag_01_logged_in.png')

# ===== NAVEGAR AO ARK LINK 3:1: (image reference) =====
TEST_ARK = 'https://www.familysearch.org/ark:/61903/3:1:33SQ-G5LY-DB9'
print(f"\nNavegando ao ARK 3:1: {TEST_ARK}")
driver.get(TEST_ARK)
time.sleep(12)
driver.save_screenshot('/home/hermes/genealogia/data/fs_diag_02_ark_page.png')

# Capture everything about the page
page_info = driver.execute_script("""
    const result = {
        url: window.location.href,
        title: document.title,
        bodyPreview: document.body.innerText.substring(0, 2000),
        images: [],
        canvases: [],
        iframes: [],
        links: [],
        scripts: []
    };
    
    // All images
    document.querySelectorAll('img').forEach(img => {
        result.images.push({
            src: img.src,
            width: img.naturalWidth,
            height: img.naturalHeight,
            alt: img.alt || '',
            className: img.className || ''
        });
    });
    
    // Canvases
    document.querySelectorAll('canvas').forEach(c => {
        result.canvases.push({
            width: c.width,
            height: c.height,
            className: c.className || '',
            id: c.id || ''
        });
    });
    
    // Iframes
    document.querySelectorAll('iframe').forEach(f => {
        result.iframes.push(f.src || f.getAttribute('data-src') || '');
    });
    
    // Links
    document.querySelectorAll('a').forEach(a => {
        if (a.href && a.href.startsWith('http')) {
            result.links.push({
                href: a.href,
                text: (a.textContent || '').trim().substring(0, 50)
            });
        }
    });
    
    // Scripts with src
    document.querySelectorAll('script[src]').forEach(s => {
        if (s.src && (s.src.includes('image') || s.src.includes('viewer') || s.src.includes('dgs')))
            result.scripts.push(s.src);
    });
    
    return result;
""")

print(f"\nURL: {page_info['url'][:100]}")
print(f"Título: {page_info['title']}")
print(f"Imagens: {len(page_info['images'])}")
for img in page_info['images'][:10]:
    print(f"  {img['src'][:80]} | {img['width']}x{img['height']} | cls={img['className'][:30]}")
print(f"Canvases: {len(page_info['canvases'])}")
for c in page_info['canvases']:
    print(f"  {c['width']}x{c['height']} | cls={c['className'][:40]} | id={c['id']}")
print(f"Iframes: {page_info['iframes'][:5]}")
print(f"Links relevantes:")
for l in page_info['links']:
    if any(kw in l['href'].lower() for kw in ['image', 'dgs', 'iiif', 'film', 'viewer', 'download']):
        print(f"  {l['href'][:100]} | {l['text']}")

# ===== PERFORMANCE API — todos os recursos carregados =====
resources = driver.execute_script("""
    const entries = performance.getEntriesByType('resource');
    return entries
        .filter(e => e.initiatorType !== 'xmlhttprequest' || e.name.includes('dgs') || e.name.includes('image') || e.name.includes('iiif'))
        .map(e => ({
            name: e.name,
            type: e.initiatorType,
            duration: Math.round(e.duration),
            size: e.transferSize || 0
        }))
        .sort((a, b) => b.size - a.size)
        .slice(0, 30);
""")

print(f"\nRecursos carregados (top 30 por tamanho):")
for r in resources:
    print(f"  {r['type']:15} | {r['size']:>8} bytes | {r['name'][:100]}")

# ===== Procurar botão "View Original Document" / "View Document" =====
view_info = driver.execute_script("""
    const buttons = Array.from(document.querySelectorAll('a, button'));
    const viewBtns = buttons.filter(b => {
        const text = (b.textContent || '').toLowerCase();
        const title = (b.title || b.getAttribute('aria-label') || '').toLowerCase();
        return text.includes('view') || text.includes('original') || text.includes('document')
            || title.includes('view') || title.includes('original') || title.includes('document');
    }).map(b => ({
        tag: b.tagName,
        text: (b.textContent || '').trim().substring(0, 60),
        href: b.href || b.getAttribute('data-href') || '',
        title: b.title || b.getAttribute('aria-label') || '',
        className: b.className || ''
    }));
    
    // Also look for download buttons
    const dlBtns = buttons.filter(b => {
        const text = (b.textContent || '').toLowerCase();
        const title = (b.title || b.getAttribute('aria-label') || '').toLowerCase();
        const cls = (b.className || '').toLowerCase();
        return text.includes('download') || title.includes('download') || cls.includes('download');
    }).map(b => ({
        tag: b.tagName,
        text: (b.textContent || '').trim().substring(0, 60),
        href: b.href || '',
        title: b.title || ''
    }));
    
    return { viewButtons: viewBtns, downloadButtons: dlBtns };
""")

print(f"\nBotões 'View/Original/Document':")
for b in view_info.get('viewButtons', []):
    print(f"  <{b['tag']}> '{b['text']}' | href={b['href'][:60]} | title={b['title'][:40]}")
print(f"\nBotões 'Download':")
for b in view_info.get('downloadButtons', []):
    print(f"  <{b['tag']}> '{b['text']}' | href={b['href'][:60]} | title={b['title'][:40]}")

# ===== Se houver "View Document", clicar e investigar o viewer =====
# Try to find and click a "View Original Document" link
view_clicked = driver.execute_script("""
    const links = document.querySelectorAll('a');
    for (const a of links) {
        const text = (a.textContent || '').toLowerCase();
        const title = (a.title || a.getAttribute('aria-label') || '').toLowerCase();
        if (text.includes('original document') || text.includes('view document') || 
            title.includes('original document') || title.includes('view document')) {
            return { clicked: true, href: a.href || '', text: a.textContent.trim() };
        }
    }
    // Also check for image-viewer links or camera icons
    for (const a of links) {
        const href = (a.href || '').toLowerCase();
        if (href.includes('/images/') || href.includes('image-viewer')) {
            return { clicked: true, href: a.href, text: a.textContent.trim() };
        }
    }
    return { clicked: false, href: '', text: '' };
""")

if view_clicked.get('clicked'):
    print(f"\nClicando em View Document: {view_clicked['text'][:40]} → {view_clicked['href'][:60]}")
    driver.get(view_clicked['href'])
    time.sleep(15)
    driver.save_screenshot('/home/hermes/genealogia/data/fs_diag_03_viewer.png')
    
    # Now analyze the image viewer page
    viewer_resources = driver.execute_script("""
        const entries = performance.getEntriesByType('resource');
        const relevant = entries.filter(e => 
            e.name.includes('dgs') || e.name.includes('iiif') || 
            e.name.includes('image') || e.name.includes('thumbnail') ||
            (e.transferSize > 10000 && (e.initiatorType === 'img' || e.name.includes('jpg') || e.name.includes('png'))
            )
        ).map(e => ({
            name: e.name,
            type: e.initiatorType,
            size: e.transferSize || 0,
            duration: Math.round(e.duration)
        })).sort((a, b) => b.size - a.size);
        
        const canvases = document.querySelectorAll('canvas');
        const bigImgs = Array.from(document.querySelectorAll('img')).filter(i => i.naturalWidth > 300);
        
        return {
            url: window.location.href,
            resources: relevant.slice(0, 30),
            canvasCount: canvases.length,
            canvasInfo: Array.from(canvases).map(c => ({ w: c.width, h: c.height, cls: c.className })),
            bigImgInfo: bigImgs.map(i => ({ src: i.src, w: i.naturalWidth, h: i.naturalHeight }))
        };
    """)
    
    print(f"\nViewer URL: {viewer_resources.get('url', '')[:100]}")
    print(f"Viewer Canvases: {len(viewer_resources.get('canvasInfo', []))}")
    for ci in viewer_resources.get('canvasInfo', []):
        print(f"  {ci['w']}x{ci['h']} cls={ci.get('cls', '')[:30]}")
    print(f"Viewer Big Imgs: {len(viewer_resources.get('bigImgInfo', []))}")
    for bi in viewer_resources.get('bigImgInfo', []):
        print(f"  {bi['w']}x{bi['h']} → {bi['src'][:100]}")
    print(f"Viewer Resources (top 20 por tamanho):")
    for r in viewer_resources.get('resources', [])[:20]:
        print(f"  {r['type']:15} | {r['size']:>8} bytes | {r['name'][:120]}")
else:
    print("\n⚠️ Nenhum botão 'View Document' encontrado")
    # Try navigating to the 1:2: link and looking there
    TEST_ARK_12 = 'https://www.familysearch.org/ark:/61903/1:2:4BB1-DMPS'
    print(f"\nTentando ARK 1:2: {TEST_ARK_12}")
    driver.get(TEST_ARK_12)
    time.sleep(12)
    driver.save_screenshot('/home/hermes/genealogia/data/fs_diag_03_ark12.png')
    
    # Check for view button here
    view_btn_12 = driver.execute_script("""
        const links = document.querySelectorAll('a');
        for (const a of links) {
            const text = (a.textContent || '').toLowerCase();
            const title = (a.title || '').toLowerCase();
            const href = (a.href || '').toLowerCase();
            if (text.includes('original document') || title.includes('original document') ||
                href.includes('/images/') || href.includes('image-viewer')) {
                return { found: true, href: a.href, text: a.textContent.trim().substring(0, 60) };
            }
        }
        return { found: false };
    """)
    print(f"View button no ARK 1:2: {view_btn_12}")

# Save all diagnostics
with open('/home/hermes/genealogia/data/fs_viewer_diagnostics.json', 'w') as f:
    json.dump({
        'page_info': page_info,
        'resources': resources,
        'view_buttons': view_info,
        'viewer_resources': viewer_resources if view_clicked.get('clicked') else None,
    }, f, ensure_ascii=False, indent=2, default=str)

print("\n✅ Diagnóstico completo. Dados salvos em fs_viewer_diagnostics.json")
driver.save_screenshot('/home/hermes/genealogia/data/fs_diag_04_final.png')

try: driver.quit()
except: pass