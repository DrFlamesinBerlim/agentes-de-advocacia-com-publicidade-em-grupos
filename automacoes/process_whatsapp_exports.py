import sys
sys.path.insert(0, r"C:\Users\advog\Meu Drive\@ PROJETOS IAS\@ cópia de publicidade\whatsweb_bot\.venv\Lib\site-packages")
import imaplib
import email
from email.header import decode_header
import os
import sys
from datetime import datetime

# Garante que o diretório automacoes esteja no sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from whatsapp_processor_core import process_whatsapp_zip, USERNAME, PASSWORD

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("MABIOS v3 — Iniciando Processamento de Exportações do WhatsApp via GMail...")
    
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(USERNAME, PASSWORD)
        mail.select("INBOX")
        
        # Buscar emails de hoje
        today = datetime.now().strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{today}")')
        
        if status != "OK":
            print("Erro ao buscar emails.")
            return
            
        email_ids = messages[0].split()
        print(f"Total de emails hoje na INBOX: {len(email_ids)}")
        
        processed_count = 0
        
        for eid in email_ids:
            res, msg_data = mail.fetch(eid, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject_header = msg["Subject"]
                    if not subject_header:
                        continue
                    
                    decoded_sub, encoding = decode_header(subject_header)[0]
                    if isinstance(decoded_sub, bytes):
                        subject = decoded_sub.decode(encoding or "utf-8", errors="ignore")
                    else:
                        subject = decoded_sub
                    
                    # Só processa se o assunto contiver WhatsApp
                    if "whatsapp" in subject.lower():
                        print(f"\nEmail de exportação do WhatsApp encontrado: {subject}")
                        for part in msg.walk():
                            if part.get_content_maintype() == 'multipart':
                                continue
                            if part.get('Content-Disposition') is None:
                                continue
                            filename = part.get_filename()
                            if filename:
                                decoded_fn, encoding_fn = decode_header(filename)[0]
                                if isinstance(decoded_fn, bytes):
                                    filename = decoded_fn.decode(encoding_fn or "utf-8", errors="ignore")
                                    
                                if filename.endswith(".zip"):
                                    file_data = part.get_payload(decode=True)
                                    print(f"  Baixando anexo: {filename}")
                                    if process_whatsapp_zip(file_data, filename, is_local_file=False):
                                        processed_count += 1
                                        
        print(f"\nProcessamento de emails finalizado! Total de exportações processadas: {processed_count}")
        
    except Exception as e:
        print(f"Erro geral no processador de emails: {e}")
    finally:
        try:
            mail.logout()
        except Exception:
            pass

if __name__ == "__main__":
    main()
