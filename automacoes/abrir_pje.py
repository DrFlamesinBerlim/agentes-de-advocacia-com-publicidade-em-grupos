import time
import os
from playwright.sync_api import sync_playwright

def main():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    print(f"Verificando Chrome em: {chrome_path}")
    
    with sync_playwright() as p:
        launch_args = {
            "headless": False,
            "args": ["--start-maximized"]
        }
        if os.path.exists(chrome_path):
            launch_args["executable_path"] = chrome_path
            
        print("Iniciando navegador...")
        browser = p.chromium.launch(**launch_args)
        
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        
        # Go directly to the actual PJe 1G login page
        url = "https://pjepg.tjro.jus.br/pje"
        print(f"Navegando diretamente para o PJe: {url}...")
        page.goto(url)
        
        print("Aguardando 10 segundos para carregamento completo e capturando tela...")
        time.sleep(10)
        
        # Take a screenshot to inspect the login page
        screenshot_path = "pje_login_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"Captura de tela salva em: {os.path.abspath(screenshot_path)}")
        
        # Save HTML source
        html_path = "pje_login_page.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"Código fonte HTML de login salvo em: {os.path.abspath(html_path)}")
        
        print("O navegador ficará aberto por 3 minutos para você interagir ou fechar.")
        for i in range(180):
            if not browser.is_connected():
                print("Navegador foi fechado pelo usuário.")
                break
            time.sleep(1)
            
        browser.close()

if __name__ == "__main__":
    main()
