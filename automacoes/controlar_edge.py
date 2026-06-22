import time
import sys
from playwright.sync_api import sync_playwright

def main():
    print("Conectando ao Edge na porta 9222...", flush=True)
    with sync_playwright() as p:
        try:
            # Connect to the existing browser instance
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("Conectado com sucesso ao navegador!", flush=True)
            
            # Get the first context and page
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            
            url = "https://pjepg.tjro.jus.br/pje"
            print(f"Navegando para: {url}...", flush=True)
            page.goto(url)
            
            print("Aguardando carregar o botão de login...", flush=True)
            page.wait_for_selector("#kc-pje-office", timeout=15000)
            
            print("Clicando no botão de Certificado Digital...", flush=True)
            page.click("#kc-pje-office")
            
            print("\n[SUCESSO] O robô clicou no botão! Digite seu PIN na janela do PJe Office.", flush=True)
            
        except Exception as e:
            print(f"Erro ao controlar o navegador: {str(e)}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
