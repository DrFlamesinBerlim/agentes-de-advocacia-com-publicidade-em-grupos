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
        
        url = "https://pje.tjro.jus.br/1g/"
        print(f"Navegando para: {url}...")
        page.goto(url)
        
        # Wait a few seconds for the page to render fully
        print("Aguardando 5 segundos para renderização...")
        time.sleep(5)
        
        # Save screenshot
        screenshot_path = "pje_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"Captura de tela salva em: {os.path.abspath(screenshot_path)}")
        
        # Save HTML source
        html_path = "pje_page.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"Código fonte HTML salvo em: {os.path.abspath(html_path)}")
        
        # List all buttons and links for debugging
        print("\n--- Analisando elementos da página ---")
        buttons = page.locator("button, a, input[type='button'], input[type='submit']").all()
        for idx, btn in enumerate(buttons[:30]):  # Limit to first 30
            try:
                text = btn.text_content().strip() if btn.text_content() else ""
                val = btn.get_attribute("value") or ""
                id_val = btn.get_attribute("id") or ""
                role = btn.get_attribute("role") or ""
                title = btn.get_attribute("title") or ""
                
                label = text or val or title or f"Sem label (ID: {id_val})"
                print(f"Elemento {idx}: [{btn.element_handle().json_value()}] - Label: '{label}' - ID: '{id_val}' - Role: '{role}'")
            except Exception as e:
                pass
                
        print("\nFechando o navegador em 5 segundos...")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()
