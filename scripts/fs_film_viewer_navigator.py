#!/usr/bin/env python3
"""
FamilySearch — Navegar no Film Viewer e baixar páginas de casamento (~1890-1895)
Filmes de Amargosa: 004896387, 004896398, etc.
"""
import subprocess, time, json, os, sys, random
from pathlib import Path
from datetime import datetime

GENEALOGIA_DIR = '/home/hermes/genealogia'
DATA_DIR = f'{GENEALOGIA_DIR}/data'
IMAGES_DIR = f'{DATA_DIR}/images/film_amargosa_casamentos'
LOG_FILE = f'{DATA_DIR}/fs_film_viewer.log'
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

driver = uc.Chrome(options=options, version_main=149)
wait = WebDriverWait(driver, 30)

try:
    # Login
    log("🔐 Login...")
    driver.get('https://www.familysearch.org/en/')
    time.sleep(10)
    for el in driver.find_elements(By.TAG_NAME, 'a') + driver.find_elements(By.TAG_NAME, 'button'):
        try:
            if 'sign in' in (el.text or '').lower():
                href = el.get_attribute('href') or ''
                try: el.click()
                except: driver.get(href) if href else None
                break
        except: continue
    time.sleep(10)
    if 'login' not in driver.current_url.lower():
        driver.get('https://ident.familysearch.org/en/identity/login/')
        time.sleep(8)
    
    u = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]')))
    u.click(); u.clear()
    for c in FS_USER: u.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
    p = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
    p.click(); p.clear()
    for c in FS_PASS: p.send_keys(c); time.sleep(random.uniform(0.03, 0.08))
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    time.sleep(20)
    
    for attempt in range(4):
        body_check = driver.execute_script("return document.body.innerText") or ""
        html_check = driver.execute_script("return document.body.innerHTML") or ""
        if any(kw in body_check.lower() for kw in ['sign out', 'sair']) or 'sign out' in html_check.lower():
            break
        time.sleep(15)
    
    log("✅ Login OK")
    
    # Configurar CDP download
    driver.execute_cdp_cmd('Page.setDownloadBehavior', {
        'behavior': 'allow',
        'downloadPath': IMAGES_DIR
    })
    
    # Filmes de Amargosa com casamentos
    films = ['004896387', '004896398', '004896397', '004896394', '004896395', '004896391', '004896388', '004896243']
    
    for film in films:
        log(f"\n🎬 Filme {film}")
        url = f'https://www.familysearch.org/ark:/61903/3:1:33S7-{film}?mode=g&cat=270765'
        driver.get(url)
        time.sleep(10)
        
        # Tentar navegar no image viewer
        for img_num in range(1, 20):
            # Tentar clicar na imagem
            try:
                driver.execute_script("""
                    // Clicar na imagem atual
                    var img = document.querySelector('.image-viewer img, canvas, .open-seadragon canvas');
                    if (img) img.click();
                """)
                time.sleep(3)
                
                # Screenshot
                fname = f'{IMAGES_DIR}/film_{film}_img_{img_num}.png'
                driver.save_screenshot(fname)
                log(f"  📸 {fname}")
                
                # Próxima imagem
                driver.execute_script("""
                    var next = document.querySelector('[aria-label="Next"], .next-button, button.next');
                    if (next) next.click();
                """)
                time.sleep(2)
            except:
                pass
    
    log("\n✅ Concluído")
    
except Exception as e:
    log(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
    subprocess.run(['pkill', '-9', '-f', 'Xvfb :99'], capture_output=True)