import sys
sys.path.insert(0, r"C:\Users\advog\Meu Drive\@ PROJETOS IAS\@ cópia de publicidade\whatsweb_bot\.venv\Lib\site-packages")
import os

# Garante que o diretório automacoes esteja no sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from whatsapp_processor_core import process_whatsapp_zip, BASE_DIR

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("MABIOS v3 — Iniciando processador de zips locais...")
    
    # Pastas para buscar arquivos ZIP de exportação
    dirs_to_check = [
        BASE_DIR,
        os.path.join(BASE_DIR, "escritorio")
    ]
    
    zip_files = []
    for d in dirs_to_check:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            filepath = os.path.join(d, f)
            if os.path.isfile(filepath) and f.endswith(".zip") and "ffmpeg" not in f.lower():
                zip_files.append(filepath)
                
    print(f"Encontrados {len(zip_files)} arquivo(s) ZIP para processamento local.")
    
    processed_count = 0
    for zf in zip_files:
        if process_whatsapp_zip(zf, zf, is_local_file=True):
            processed_count += 1
            
    print(f"\nProcessamento local concluído! Total de zips processados: {processed_count}")

if __name__ == "__main__":
    main()
