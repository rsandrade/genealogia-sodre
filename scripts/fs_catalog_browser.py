#!/usr/bin/env python3
"""
FamilySearch Catalog Browser — Login UC + acesso ao catálogo de Amargosa
Busca os microfilmes de casamento (~1890-1900) e baixa as imagens.
Usa UC com digitação humana (método comprovado v11/v3).
"""
import subprocess, time, json, os, sys, random
from datetime import datetime
from pathlib import Path

GENEALOGIA_DIR = '/home/hermes/genealogia'
DATA_DIR = f'{GENEALOGIA_DIR}/data'
IMAGES_DIR = f'{DATA_DIR}/images/amargosa_casamentos'
OUTPUT_FILE = f'{DATA_DIR}/fs_catalog_amargosa.json'
os.makedirs(IMAGES_DIR, exist_ok=True)

# =============================================
# SETUP
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
from selenium.webdriver.common.keys import Keys

options = uc.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 30)

def slow_type(element, text, delay_range=(0.03, 0.08)):
    """Digita caractere a caractere com delay random (método comprovado)"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(*delay_range))

try:
    # =============================================
    # LOGIN
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
        print("❌ Credenciais não encontradas"); sys.exit(1)
    
    print(f"🔐 Fazendo login como {FS_USER[:5]}...")
    driver.get('https://ident.familysearch.org/en/identity/login/')
    time.sleep(5)
    
    # Digitar username
    try:
        username_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]')))
        slow_type(username_field, FS_USER)
        time.sleep(0.5)
    except Exception as e:
        print(f"Tentando seletor alternativo para username: {e}")
        username_field = driver.find_element(By.CSS_SELECTOR, 'input[type="text"]')
        slow_type(username_field, FS_USER)
        time.sleep(0.5)
    
    # Digitar password
    password_field = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    slow_type(password_field, FS_PASS)
    time.sleep(0.5)
    
    # Submeter
    submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_btn.click()
    time.sleep(8)
    
    # Verificar login
    body = driver.execute_script("return document.body.innerText") or ""
    html = driver.execute_script("return document.body.innerHTML") or ""
    logged_in = any(kw in body.lower() for kw in ['sign out', 'sair'])
    if not logged_in:
        logged_in = 'sign out' in html.lower() or FS_USER[:5].lower() in body.lower()
    
    if not logged_in:
        print("❌ Login falhou!")
        print(f"Body (200 chars): {body[:200]}")
        driver.save_screenshot(f'{DATA_DIR}/fs_login_failed.png')
        sys.exit(1)
    
    print("✅ Login bem-sucedido!")
    
    # =============================================
    # ACESSAR CATÁLOGO 324815 (Amargosa paroquiais 1856-1915)
    # =============================================
    print("\n📋 Acessando catálogo 324815 (Amargosa paroquiais 1856-1915)...")
    driver.get('https://www.familysearch.org/search/catalog/324815')
    time.sleep(10)
    
    body_cat1 = driver.execute_script("return document.body.innerText") or ""
    html_cat1 = driver.execute_script("return document.body.innerHTML") or ""
    
    with open(f'{DATA_DIR}/fs_catalog_324815.html', 'w') as f:
        f.write(html_cat1)
    print(f"💾 Catálogo 324815 salvo ({len(html_cat1)} chars)")
    
    # Verificar se há links de filmes/DGS
    dgs_links = driver.execute_script("""
        var links = document.querySelectorAll('a[href*="film"], a[href*="DGS"], a[href*="images"], a[href*="ark"]');
        var result = [];
        for (var i = 0; i < links.length; i++) {
            result.push({text: links[i].innerText.trim(), href: links[i].href});
        }
        return result;
    """)
    print(f"🔗 Links encontrados: {len(dgs_links)}")
    for link in dgs_links[:20]:
        print(f"  {link.get('text', '')[:60]} → {link.get('href', '')[:80]}")
    
    # =============================================
    # ACESSAR CATÁLOGO 1482750 (Amargosa registros 1856-1956)
    # =============================================
    print("\n📋 Acessando catálogo 1482750 (Amargosa registros 1856-1956)...")
    driver.get('https://www.familysearch.org/search/catalog/1482750')
    time.sleep(10)
    
    body_cat2 = driver.execute_script("return document.body.innerText") or ""
    html_cat2 = driver.execute_script("return document.body.innerHTML") or ""
    
    with open(f'{DATA_DIR}/fs_catalog_1482750.html', 'w') as f:
        f.write(html_cat2)
    print(f"💾 Catálogo 1482750 salvo ({len(html_cat2)} chars)")
    
    dgs_links2 = driver.execute_script("""
        var links = document.querySelectorAll('a[href*="film"], a[href*="DGS"], a[href*="images"], a[href*="ark"]');
        var result = [];
        for (var i = 0; i < links.length; i++) {
            result.push({text: links[i].innerText.trim(), href: links[i].href});
        }
        return result;
    """)
    print(f"🔗 Links encontrados: {len(dgs_links2)}")
    for link in dgs_links2[:20]:
        print(f"  {link.get('text', '')[:60]} → {link.get('href', '')[:80]}")
    
    # =============================================
    # BUSCAR ARK LINKS NOS DADOS EXISTENTES
    # =============================================
    print("\n📋 Buscando ARK links nos dados existentes...")
    all_arks = set()
    for fname in ['fs_endpoint_structured.json', 'fs_gap_search_results.json', 'fs_v17_data.json']:
        fpath = f'{DATA_DIR}/{fname}'
        if os.path.exists(fpath):
            with open(fpath) as f:
                content = f.read()
            import re
            arks = re.findall(r'3:1:[A-Za-z0-9-]+', content)
            for a in arks:
                a = a.split('?')[0]
                all_arks.add(a)
            arks2 = re.findall(r'ark:/61903/3:1:[A-Za-z0-9:-]+', content)
            for a in arks2:
                all_arks.add(a)
    
    print(f"  Total ARK links únicos: {len(all_arks)}")
    for ark in sorted(all_arks)[:30]:
        print(f"  {ark}")
    
    # Salvar tudo
    results = {
        'catalog_324815_body': body_cat1[:3000],
        'catalog_1482750_body': body_cat2[:3000],
        'dgs_links_324815': dgs_links[:50],
        'dgs_links_1482750': dgs_links2[:50],
        'ark_links_from_data': list(all_arks)[:100],
    }
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Resultados salvos em {OUTPUT_FILE}")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        driver.save_screenshot(f'{DATA_DIR}/fs_catalog_final.png')
    except:
        pass
    driver.quit()
    subprocess.run(['pkill', '-9', '-f', 'Xvfb :99'], capture_output=True)
    print("Encerrado.")