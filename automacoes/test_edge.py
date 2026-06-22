import time
import sys
from playwright.sync_api import sync_playwright

def main():
    print("Iniciando Playwright...", flush=True)
    try:
        with sync_playwright() as p:
            print("Tentando abrir o Microsoft Edge via channel...", flush=True)
            browser = p.chromium.launch(
                headless=False,
                channel="msedge",
                args=["--start-maximized"]
            )
            print("Edge aberto com sucesso!", flush=True)
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            
            url = "https://pjepg.tjro.jus.br/pje"
            print(f"Navegando para {url}...", flush=True)
            page.goto(url)
            
            print("Aguardando carregamento da página...", flush=True)
            page.wait_for_selector("#kc-pje-office", timeout=15000)
            print("Botão do certificado encontrado!", flush=True)
            
            print("Clicando no botão do certificado...", flush=True)
            page.click("#kc-pje-office")
            print("Clique realizado com sucesso!", flush=True)
            
            print("Esperando 30 segundos para interação...", flush=True)
            time.sleep(30)
            
            browser.close()
            print("Navegador fechado.", flush=True)
    except Exception as e:
        print(f"Erro ocorrido: {str(e)}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
