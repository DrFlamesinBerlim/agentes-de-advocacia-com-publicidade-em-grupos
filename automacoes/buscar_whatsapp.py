import time
import sys
import os
import json
from playwright.sync_api import sync_playwright

def find_whatsapp_page(browser):
    """Procura por uma aba aberta com o WhatsApp Web."""
    for context in browser.contexts:
        for page in context.pages:
            try:
                url = page.url()
                if "web.whatsapp.com" in url:
                    return page
            except Exception:
                continue
    return None

def main():
    print("MABIOS v3 — Buscador de Grupos WhatsApp 'AA'", flush=True)
    print("Conectando ao navegador na porta 9222...", flush=True)
    
    with sync_playwright() as p:
        try:
            # Conecta ao navegador aberto com depuração remota
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("Conectado com sucesso ao navegador!", flush=True)
            
            # Encontra ou cria a página do WhatsApp Web
            page = find_whatsapp_page(browser)
            if page:
                print(f"Aba do WhatsApp Web encontrada: '{page.title()}'", flush=True)
                # Traz a página para frente
                page.bring_to_front()
            else:
                print("Aba do WhatsApp Web não encontrada. Criando nova aba...", flush=True)
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.new_page()
                page.goto("https://web.whatsapp.com")
            
            print("Aguardando carregamento do WhatsApp Web (pode requerer login/sincronização)...", flush=True)
            # Espera carregar a interface principal buscando o seletor do painel lateral ou da barra de busca
            # Os seletores comuns para a interface carregada são:
            # - #side
            # - div[contenteditable="true"]
            # - [data-tab="3"]
            
            try:
                page.wait_for_selector("#side", timeout=30000)
                print("WhatsApp Web carregado com sucesso!", flush=True)
            except Exception:
                print("Painel principal não detectado em 30s. Verifique se o QR Code precisa ser escaneado.", flush=True)
                # Salva um print para ajudar o usuário se necessário
                os.makedirs("documentos", exist_ok=True)
                page.screenshot(path="documentos/whatsapp_status.png")
                print("Salvo screenshot em documentos/whatsapp_status.png", flush=True)
                return
            
            print("Localizando caixa de pesquisa...", flush=True)
            search_selectors = [
                "div[contenteditable='true'][data-tab='3']",
                "div[contenteditable='true']",
                "[role='textbox']",
                "div.lexical-rich-text-input"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    el = page.locator(selector).first
                    if el.is_visible():
                        search_box = el
                        print(f"Caixa de pesquisa encontrada com o seletor: '{selector}'", flush=True)
                        break
                except Exception:
                    continue
            
            if not search_box:
                print("Não foi possível localizar a caixa de pesquisa do WhatsApp Web.", flush=True)
                return
            
            # Clica e limpa a pesquisa anterior
            search_box.click()
            # Apaga o texto atual digitando Backspace repetidamente
            search_box.press("Control+A")
            search_box.press("Backspace")
            
            print("Digitando termo de busca 'AA'...", flush=True)
            search_box.fill("AA")
            time.sleep(3)  # Aguarda a filtragem dos chats
            
            print("Varrendo os resultados da busca...", flush=True)
            # Seletor para os títulos das conversas na lista lateral
            # Geralmente são spans com atributo title ou dir="auto" dentro de elementos da lista
            titles = []
            
            # Abordagem 1: Pegar todos os spans com dir="auto" que tenham classe de título ou title no pai
            # No WhatsApp Web, cada chat item tem span[title] ou spans contendo o nome do contato.
            # Vamos buscar elementos de texto contendo "AA" (case-insensitive) na barra lateral (#side)
            elements = page.locator("#side span[title]").all()
            for el in elements:
                try:
                    title_attr = el.get_attribute("title")
                    if title_attr and "AA" in title_attr.upper():
                        if title_attr not in titles:
                            titles.append(title_attr)
                except Exception:
                    continue
                    
            # Abordagem 2: Fallback buscando por textos diretos na barra lateral
            elements_text = page.locator("#side span[dir='auto']").all()
            for el in elements_text:
                try:
                    text = el.inner_text()
                    if text and "AA" in text.upper():
                        if text not in titles:
                            titles.append(text)
                except Exception:
                    continue

            # Abordagem 3: Buscar elementos com class/attributes específicos
            elements_custom = page.locator("div[role='listitem'] span").all()
            for el in elements_custom:
                try:
                    text = el.inner_text()
                    if text and text.startswith("AA") and len(text) < 50:
                        if text not in titles:
                            titles.append(text)
                except Exception:
                    continue
            
            print(f"\nResultados encontrados ({len(titles)} grupos/conversas):", flush=True)
            for t in sorted(titles):
                print(f" - {t}", flush=True)
            
            # Salva o resultado em um JSON em documentos/
            os.makedirs("documentos", exist_ok=True)
            with open("documentos/grupos_whatsapp.json", "w", encoding="utf-8") as f:
                json.dump({"grupos": sorted(titles), "count": len(titles), "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}, f, ensure_ascii=False, indent=2)
            print("\nResultado salvo em 'documentos/grupos_whatsapp.json'", flush=True)
            
        except Exception as e:
            print(f"\n[ERRO] Falha ao conectar ou buscar no WhatsApp: {str(e)}", file=sys.stderr, flush=True)
            print("\nCertifique-se de que o Microsoft Edge esta rodando em modo de depuracao na porta 9222.", flush=True)
            print("Para ativar, feche o Edge e execute no terminal do Windows:", flush=True)
            print("  start msedge --remote-debugging-port=9222", flush=True)

if __name__ == "__main__":
    main()
