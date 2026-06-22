import time
import sys
from playwright.sync_api import sync_playwright

def main():
    print("Iniciando Playwright...", flush=True)
    try:
        with sync_playwright() as p:
            print("Abrindo o Google Chrome...", flush=True)
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--start-maximized"]
            )
            print("Chrome aberto com sucesso!", flush=True)
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            
            url = "https://www.google.com"
            print(f"Navegando para {url}...", flush=True)
            page.goto(url)
            print("Página do Google carregada com sucesso!", flush=True)
            
            print("Mantendo o navegador aberto por 10 minutos para você testar.", flush=True)
            print("Pode fechar a janela quando quiser para encerrar o script.", flush=True)
            
            for i in range(600):
                if not browser.is_connected():
                    print("Navegador fechado pelo usuário.", flush=True)
                    break
                time.sleep(1)
                
    except Exception as e:
        print(f"Erro ocorrido: {str(e)}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
