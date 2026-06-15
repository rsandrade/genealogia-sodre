#!/usr/bin/env python3
"""
Navegar no Film Viewer do FamilySearch para procurar o casamento de Tomaz Gramilo Sodré
no filme 004896398 (Amargosa, casamentos ~1850-1956).
"""
import json, time, random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def login_fs(driver):
    """Login no FamilySearch via Selenium UC"""
    from pathlib import Path
    env_path = Path("/home/hermes/.hermes/.env")
    fs_user = "hermesmassarelos"
    fs_pass = ""
    for line in env_path.read_text().splitlines():
        if line.startswith("FS_PASS="):
            fs_pass = line.split("=", 1)[1].strip()
            break
    
    driver.get("https://www.familysearch.org/pt/")
    time.sleep(2)
    
    # Clicar em Entrar
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/auth/familysearch/login') or contains(text(), 'Entrar') or contains(text(), 'Sign In')]"))
        )
        btn.click()
        time.sleep(2)
    except:
        pass
    
    # Preencher login
    email = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    for c in fs_user:
        email.send_keys(c)
        time.sleep(random.uniform(0.05, 0.15))
    
    pwd = driver.find_element(By.NAME, "password")
    for c in fs_pass:
        pwd.send_keys(c)
        time.sleep(random.uniform(0.05, 0.15))
    
    pwd.send_keys(Keys.ENTER)
    time.sleep(5)
    print("✅ Login realizado")
    return True

def search_film(driver, film_number):
    """Navegar direto para o filme"""
    url = f"https://www.familysearch.org/search/film/{film_number}"
    driver.get(url)
    time.sleep(5)
    print(f"🎬 Filme {film_number} aberto")

def navigate_images(driver, start_img=1, max_imgs=50, search_terms=None):
    """Navegar nas imagens do filme procurando termos"""
    if search_terms is None:
        search_terms = ["tomaz", "tomé", "teodora", "gramilo", "sodré", "vaz", "cruz", "julia"]
    
    found = []
    
    for img_num in range(start_img, start_img + max_imgs):
        print(f"\n📄 Verificando imagem {img_num}...")
        
        # URL direta da imagem no filme
        img_url = f"https://www.familysearch.org/ark:/61903/3:1:33S7-95LB-4PL?i={img_num}&cat=1030382"
        driver.get(img_url)
        time.sleep(3)
        
        # Capturar texto da página
        page_text = driver.page_source.lower()
        
        # Procurar termos
        matches = []
        for term in search_terms:
            if term.lower() in page_text:
                matches.append(term)
        
        if matches:
            print(f"  ✅ ENCONTRADO: {matches}")
            found.append({
                "image": img_num,
                "matches": matches,
                "url": driver.current_url,
                "preview": page_text[:2000]
            })
            
            # Salvar screenshot
            screenshot_path = f"/home/hermes/genealogia/data/images/film_search/film_004896398_img_{img_num}.png"
            Path(screenshot_path).parent.mkdir(parents=True, exist_ok=True)
            driver.save_screenshot(screenshot_path)
            print(f"  📸 Screenshot salvo: {screenshot_path}")
        
        time.sleep(1)
    
    return found

def main():
    print("🔍 Buscando casamento Tomaz × Teodora no filme 004896398...")
    
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/usr/bin/chromium-browser"
    
    driver = uc.Chrome(options=options, browser_executable_path="/usr/bin/chromium-browser")
    
    try:
        login_fs(driver)
        search_film(driver, "004896398")
        
        # O filme 004896398 tem 402 imagens segundo o índice
        # O casamento de Tomaz ~1891 deve estar no início
        found = navigate_images(driver, start_img=1, max_imgs=100)
        
        # Salvar resultados
        results_path = "/home/hermes/genealogia/data/film_004896398_tomaz_search.json"
        with open(results_path, "w") as f:
            json.dump(found, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Resultados salvos em: {results_path}")
        
        if found:
            print(f"\n🎉 ENCONTRADOS {len(found)} imagens com termos relevantes!")
            for f in found:
                print(f"  Imagem {f['image']}: {f['matches']}")
        else:
            print("\n❌ Nenhum termo encontrado nas primeiras 100 imagens")
            print("   O casamento pode estar mais à frente ou em outro filme")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
