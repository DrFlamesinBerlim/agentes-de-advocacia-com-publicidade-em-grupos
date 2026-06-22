import time
import os
from playwright.sync_api import sync_playwright

def main():
    # Prioritizing Microsoft Edge as the default browser
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    browser_path = None
    if os.path.exists(edge_path):
        print(f"Usando Microsoft Edge em: {edge_path}")
        browser_path = edge_path
    elif os.path.exists(chrome_path):
        print(f"Usando Google Chrome em: {chrome_path}")
        browser_path = chrome_path
    else:
        print("Usando Chromium padrão do Playwright...")
        
    with sync_playwright() as p:
        launch_args = {
            "headless": False,
            "args": ["--start-maximized"]
        }
        if browser_path:
            launch_args["executable_path"] = browser_path
            
        browser = p.chromium.launch(**launch_args)
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        
        url = "https://pjepg.tjro.jus.br/pje"
        print(f"Navegando para: {url}...")
        page.goto(url)
        
        print("Aguardando o botão de Certificado Digital carregar...")
        # Wait for the certificate button
        page.wait_for_selector("#kc-pje-office", timeout=15000)
        
        print("Clicando no botão 'CERTIFICADO DIGITAL'...")
        page.click("#kc-pje-office")
        
        print("\n*** AÇÃO NECESSÁRIA ***")
        print("A janela do PJe Office deve ter aparecido na sua tela.")
        print("Insira seu token USB e digite seu PIN/Senha para fazer o login.")
        print("Aguardando você realizar o login no PJe...")
        
        # Poll for URL change to detect successful login
        login_success = False
        for _ in range(120):  # Wait up to 2 minutes
            if not browser.is_connected():
                print("O navegador foi fechado.")
                break
            
            current_url = page.url
            # If the URL is no longer the login URL or contains login subpaths, we logged in
            if "/pje" not in current_url or "/seam" in current_url or "/painel" in current_url or ("login" not in current_url.lower() and current_url != url):
                print(f"\n[OK] Login detectado! Nova URL: {current_url}")
                login_success = True
                break
                
            time.sleep(1)
            
        if login_success:
            print("Login concluído com sucesso via automação!")
        else:
            print("Tempo limite de login esgotado ou navegador fechado.")
            
        # Keep browser open for user to continue working
        print("Mantendo o navegador aberto por mais 5 minutos para você trabalhar...")
        for _ in range(300):
            if not browser.is_connected():
                break
            time.sleep(1)
            
        browser.close()

if __name__ == "__main__":
    main()
