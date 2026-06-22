import time
import sys
import os
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
    print("MABIOS v3 — Enviador de Mensagens WhatsApp 'AA'", flush=True)
    print("Conectando ao navegador na porta 9222...", flush=True)
    
    with sync_playwright() as p:
        try:
            # Conecta ao navegador aberto com depuração remota
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("Conectado com sucesso ao navegador!", flush=True)
            
            # Encontra a página do WhatsApp Web
            page = find_whatsapp_page(browser)
            if not page:
                print("[ERRO] Aba do WhatsApp Web não encontrada. Abra o WhatsApp Web no navegador antes de rodar.", flush=True)
                return
            
            page.bring_to_front()
            print(f"Aba do WhatsApp Web ativa: '{page.title()}'", flush=True)
            
            # Garante que o painel está carregado
            page.wait_for_selector("#side", timeout=10000)
            
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
                        break
                except Exception:
                    continue
            
            if not search_box:
                print("[ERRO] Não foi possível localizar a caixa de pesquisa.", flush=True)
                return
            
            # Limpa e pesquisa por "AA"
            search_box.click()
            search_box.press("Control+A")
            search_box.press("Backspace")
            search_box.fill("AA")
            time.sleep(3)  # Aguarda carregar resultados
            
            # Mapeia os chats que contêm "AA" no título
            print("Escaneando a lista de chats filtrados...", flush=True)
            chat_names = []
            
            # Busca spans com atributo title contendo "AA"
            elements = page.locator("#side span[title]").all()
            for el in elements:
                try:
                    title_attr = el.get_attribute("title")
                    if title_attr and "AA" in title_attr.upper():
                        if title_attr not in chat_names:
                            chat_names.append(title_attr)
                except Exception:
                    continue
            
            # Fallback adicionando spans com dir="auto" contendo "AA"
            elements_text = page.locator("#side span[dir='auto']").all()
            for el in elements_text:
                try:
                    text = el.inner_text()
                    if text and "AA" in text.upper() and len(text) < 50:
                        if text not in chat_names:
                            chat_names.append(text)
                except Exception:
                    continue
            
            # Ordena a lista
            chat_names = sorted(list(set(chat_names)))
            
            if not chat_names:
                print("Nenhum grupo ou conversa contendo 'AA' foi localizado na lista lateral.", flush=True)
                return
            
            print(f"\nLocalizado {len(chat_names)} grupos/conversas para envio: {chat_names}\n", flush=True)
            
            sucessos = 0
            for name in chat_names:
                print(f"-> Selecionando o chat: '{name}'...", flush=True)
                try:
                    # Tenta clicar no elemento com o título do chat
                    # Usamos um seletor exato de texto ou título
                    chat_selector = f'#side span[title="{name}"]'
                    chat_element = page.locator(chat_selector).first
                    
                    if not chat_element.is_visible():
                        # Fallback buscando pelo texto dir="auto"
                        chat_selector = f'#side span[dir="auto"]:has-text("{name}")'
                        chat_element = page.locator(chat_selector).first
                        
                    chat_element.click()
                    time.sleep(1.5)  # Aguarda o chat abrir e carregar
                    
                    # Localiza a caixa de entrada de texto da mensagem
                    message_selectors = [
                        "footer div[contenteditable='true']",
                        "div[contenteditable='true'][data-tab='10']",
                        "footer [role='textbox']",
                        "div.lexical-rich-text-input[data-tab='10']"
                    ]
                    
                    input_box = None
                    for msg_sel in message_selectors:
                        try:
                            el = page.locator(msg_sel).first
                            if el.is_visible():
                                input_box = el
                                break
                        except Exception:
                            continue
                    
                    if input_box:
                        # Envia o "Oi!"
                        input_box.click()
                        input_box.fill("Oi!")
                        time.sleep(0.5)
                        input_box.press("Enter")
                        print(f"   [SUCESSO] Mensagem enviada para '{name}'!", flush=True)
                        sucessos += 1
                        time.sleep(1)  # Intervalo de segurança entre envios
                    else:
                        print(f"   [FALHA] Não foi possível localizar a caixa de texto para '{name}'", flush=True)
                except Exception as e:
                    print(f"   [ERRO] Falha ao enviar para '{name}': {str(e)}", flush=True)
            
            # Limpa o campo de busca no final
            print("\nLimpando campo de busca...", flush=True)
            search_box.click()
            search_box.press("Control+A")
            search_box.press("Backspace")
            search_box.press("Escape")
            
            print(f"\nProcesso concluído! Mensagens enviadas com sucesso: {sucessos}/{len(chat_names)}", flush=True)
            
        except Exception as e:
            print(f"\n[ERRO DE CONEXÃO] {str(e)}", file=sys.stderr, flush=True)
            print("\nCertifique-se de fechar as janelas do Edge e abrir novamente com o comando:", flush=True)
            print("  start msedge --remote-debugging-port=9222", flush=True)

if __name__ == "__main__":
    main()
