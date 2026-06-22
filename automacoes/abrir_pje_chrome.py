import time
import sys
import os
from playwright.sync_api import sync_playwright

def main():
    print("Iniciando Playwright...", flush=True)
    try:
        with sync_playwright() as p:
            # Let's try to launch Chrome via channel "chrome" or fall back to default chromium
            print("Abrindo o Google Chrome...", flush=True)
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--start-maximized"]
            )
            print("Chrome aberto com sucesso!", flush=True)
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            
            url = "https://pjepg.tjro.jus.br/pje"
            print(f"Navegando para {url}...", flush=True)
            page.goto(url)
            
            print("Aguardando o botão de login carregar...", flush=True)
            page.wait_for_selector("#kc-pje-office", timeout=20000)
            print("Botão encontrado. Clicando...", flush=True)
            page.click("#kc-pje-office")
            print("Clique realizado! A janela do PJe Office deve estar na sua tela.", flush=True)
            
            print("Mantendo o navegador aberto por 1 hora para você trabalhar tranquilamente.", flush=True)
            print("Você pode fechar a janela do navegador quando terminar para encerrar o script.", flush=True)
            
            # Keep browser open for 1 hour (3600 seconds)
            for i in range(3600):
                if not browser.is_connected():
                    print("Navegador foi fechado pelo usuário. Finalizando script.", flush=True)
                    break
                time.sleep(1)
                
    except Exception as e:
        print(f"Erro ocorrido: {str(e)}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
