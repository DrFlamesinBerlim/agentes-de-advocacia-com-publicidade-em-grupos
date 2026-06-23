import os
import zipfile
import re
import shutil
import io
import sys
import subprocess
from datetime import datetime
import speech_recognition as sr
from playwright.sync_api import sync_playwright

# Configurações globais
FFMPEG_PATH = r"C:\Users\advog\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"
BASE_DIR = r"C:\Users\advog\Meu Drive\AI downloads"
CLIENTS_DIR = os.path.join(BASE_DIR, "escritorio", "clientes")

def convert_opus_to_wav(opus_path, wav_path):
    """Converte arquivo .opus para .wav mono 16kHz utilizando FFmpeg"""
    if not os.path.exists(FFMPEG_PATH):
        print(f"  [ERRO] FFmpeg não encontrado em: {FFMPEG_PATH}")
        return False
    try:
        cmd = [FFMPEG_PATH, "-y", "-i", opus_path, "-ac", "1", "-ar", "16000", wav_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception as e:
        print(f"  [ERRO] Falha ao converter {os.path.basename(opus_path)}: {e}")
        return False

def transcribe_wav(wav_path):
    """Realiza a transcrição do áudio WAV usando a API SpeechRecognition do Google"""
    r = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
        text = r.recognize_google(audio_data, language="pt-BR")
        return text
    except sr.UnknownValueError:
        return "Áudio sem fala ou incompreensível"
    except sr.RequestError as e:
        return f"Erro na API de transcrição: {e}"
    except Exception as e:
        return f"Erro ao transcrever: {e}"

def generate_pdf_report(client_name, conversation_lines, output_pdf_path):
    """Gera um relatório elegante em PDF da conversa utilizando Playwright"""
    print(f"  📄 Gerando relatório PDF para {client_name}...")
    
    # 1. Parsear as linhas do chat
    parsed_messages = []
    current_message = None
    
    for line in conversation_lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        
        # Expressão regular para capturar as mensagens do WhatsApp
        # Exemplo: 20/05/2026 09:52 - Cli Keila Pastorini: Mensagem
        match = re.match(r'^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}) - ([^:]+): (.*)$', line_clean)
        
        if match:
            if current_message:
                parsed_messages.append(current_message)
            
            timestamp = match.group(1)
            sender = match.group(2).strip()
            content = match.group(3).strip()
            
            current_message = {
                "timestamp": timestamp,
                "sender": sender,
                "content": content
            }
        else:
            if current_message:
                current_message["content"] += "\n" + line_clean
            else:
                # Caso a linha inicial não case (ex: cabeçalhos do chat)
                pass
                
    if current_message:
        parsed_messages.append(current_message)
        
    # 2. Construir HTML
    html_messages = []
    for msg in parsed_messages:
        content = msg["content"]
        sender = msg["sender"]
        timestamp = msg["timestamp"]
        
        # Identificar classe CSS com base no remetente
        is_lawyer = "brito" in sender.lower()
        msg_class = "lawyer" if is_lawyer else "client"
        
        # Verificar anexos e transcrições
        attachment_html = ""
        transcription_html = ""
        
        # Verifica se é áudio PTT com transcrição
        # Formato: PTT-20260520-WA0046.opus (arquivo anexado) [TRANSCRIÇÃO]: deixa eu te falar...
        ptt_match = re.search(r'(PTT-\d+-WA\d+\.opus)\s*\(arquivo anexado\)\s*\[TRANSCRIÇÃO\]:\s*(.*)', content, re.IGNORECASE)
        img_match = re.search(r'(IMG-\d+-WA\d+\.jpg)\s*\(arquivo anexado\)', content, re.IGNORECASE)
        generic_match = re.search(r'([^:\s]+\.(?:pdf|docx|doc|zip|xlsx))\s*\(arquivo anexado\)', content, re.IGNORECASE)
        
        if ptt_match:
            filename = ptt_match.group(1)
            transcription = ptt_match.group(2)
            attachment_html = f'<div class="attachment-box"><span class="icon">🎙️</span> Áudio Anexo: {filename}</div>'
            transcription_html = f'<div class="transcription-box"><span class="icon">📝</span> <strong>Transcrição:</strong> {transcription}</div>'
            content = "" # Oculta o texto do arquivo anexado bruto
        elif img_match:
            filename = img_match.group(1)
            attachment_html = f'<div class="attachment-box"><span class="icon">📷</span> Imagem Anexa: {filename}</div>'
            content = ""
        elif generic_match:
            filename = generic_match.group(1)
            attachment_html = f'<div class="attachment-box"><span class="icon">📄</span> Documento Anexo: {filename}</div>'
            content = ""
            
        # Formata o conteúdo normal se houver texto
        content_html = ""
        if content:
            content_html = f'<div class="message-content">{content}</div>'
            
        html_messages.append(f"""
        <div class="message {msg_class}">
            <div class="message-header">
                <span class="sender">{sender}</span>
                <span class="time">{timestamp}</span>
            </div>
            {content_html}
            {attachment_html}
            {transcription_html}
        </div>
        """)
        
    messages_joined = "\n".join(html_messages)
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Relatório de Conversa - {client_name}</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    body {{
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }}
    .header {{
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 15px;
        margin-bottom: 25px;
    }}
    .header h1 {{
        font-size: 24px;
        margin: 0;
        color: #0f172a;
        font-weight: 700;
    }}
    .header .meta {{
        font-size: 13px;
        color: #64748b;
        margin-top: 5px;
        line-height: 1.6;
    }}
    .chat-container {{
        display: flex;
        flex-direction: column;
        gap: 14px;
    }}
    .message {{
        display: flex;
        flex-direction: column;
        max-width: 85%;
        padding: 10px 14px;
        border-radius: 12px;
        position: relative;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 8px;
    }}
    .message.lawyer {{
        align-self: flex-end;
        background-color: #f1f5f9;
        border-left: 4px solid #1e3a8a;
        margin-left: auto;
    }}
    .message.client {{
        align-self: flex-start;
        background-color: #fafafa;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0d9488;
        margin-right: auto;
    }}
    .message-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4px;
        font-size: 11px;
        font-weight: 600;
    }}
    .message.lawyer .message-header .sender {{
        color: #1e3a8a;
    }}
    .message.client .message-header .sender {{
        color: #0d9488;
    }}
    .message-header .time {{
        color: #94a3b8;
        font-weight: 400;
        margin-left: 10px;
    }}
    .message-content {{
        white-space: pre-wrap;
        word-break: break-word;
    }}
    .transcription-box {{
        margin-top: 8px;
        padding: 8px 12px;
        background-color: #f0fdf4;
        border-left: 3px solid #22c55e;
        border-radius: 6px;
        font-size: 13px;
        color: #166534;
    }}
    .attachment-box {{
        margin-top: 6px;
        padding: 6px 10px;
        background-color: #f8fafc;
        border: 1px dashed #cbd5e1;
        border-radius: 6px;
        font-size: 12px;
        color: #475569;
    }}
    @media print {{
        .message {{
            page-break-inside: avoid;
            break-inside: avoid;
        }}
    }}
</style>
</head>
<body>
    <div class="header">
        <h1>Relatório de Conversa - WhatsApp</h1>
        <div class="meta">
            <strong>Escritório:</strong> De Brito Advocacia<br>
            <strong>Cliente:</strong> {client_name}<br>
            <strong>Data do Relatório:</strong> {date_str}
        </div>
    </div>
    <div class="chat-container">
        {messages_joined}
    </div>
</body>
</html>
"""
    
    # Salvar HTML temporário
    temp_html_path = output_pdf_path + ".temp.html"
    try:
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # 3. Converter HTML para PDF usando Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"file:///{os.path.abspath(temp_html_path)}")
            page.wait_for_load_state("networkidle")
            page.pdf(
                path=output_pdf_path,
                format="A4",
                print_background=True,
                margin={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"}
            )
            browser.close()
        print(f"  [OK] PDF gerado com sucesso em: {output_pdf_path}")
    except Exception as e:
        print(f"  [ERRO] Falha ao gerar PDF para {client_name}: {e}")
    finally:
        # Remover HTML temporário
        if os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except Exception:
                pass

def process_whatsapp_zip(zip_source, filename_or_path, is_local_file=True):
    """
    Função principal que processa um arquivo ZIP de exportação do WhatsApp.
    Mapeia os arquivos e cria a estrutura:
    escritorio/clientes/[Nome do Cliente]/
      - PTT/ (áudios e transcrições)
      - arquivos/ (outros anexos)
      - Relatório - [Nome do Cliente].pdf
      - Conversa do WhatsApp com [Nome do Cliente].txt
    """
    chat_name = os.path.splitext(os.path.basename(filename_or_path))[0]
    chat_name = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '', chat_name).strip()
    
    # Tenta extrair o nome do cliente a partir do nome da exportação
    if chat_name.lower().startswith("conversa do whatsapp com "):
        client_name = chat_name[len("conversa do whatsapp com "):].strip()
    else:
        client_name = chat_name

    print(f"\n==================================================")
    print(f"Processando Cliente: {client_name}")
    print(f"==================================================")
    
    # 1. Extração temporária
    temp_dir = os.path.join(os.environ.get("TEMP", r"C:\Temp"), f"extract_core_{int(datetime.now().timestamp())}")
    os.makedirs(temp_dir, exist_ok=True)
    
    txt_file_name = None
    try:
        if is_local_file:
            with zipfile.ZipFile(zip_source) as z:
                z.extractall(temp_dir)
                for name in z.namelist():
                    if name.endswith(".txt"):
                        txt_file_name = name
                        break
        else:
            with zipfile.ZipFile(io.BytesIO(zip_source)) as z:
                z.extractall(temp_dir)
                for name in z.namelist():
                    if name.endswith(".txt"):
                        txt_file_name = name
                        break
    except Exception as e:
        print(f"  [ERRO] Falha ao extrair ZIP: {e}")
        return False

    if not txt_file_name:
        print("  [AVISO] Nenhum arquivo de texto (.txt) de conversa encontrado no ZIP.")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False
        
    txt_file_path = os.path.join(temp_dir, txt_file_name)
    
    # 2. Definir pastas de destino estruturadas
    client_dest_dir = os.path.join(CLIENTS_DIR, client_name)
    ptt_dest_dir = os.path.join(client_dest_dir, "PTT")
    arquivos_dest_dir = os.path.join(client_dest_dir, "arquivos")
    
    os.makedirs(client_dest_dir, exist_ok=True)
    os.makedirs(ptt_dest_dir, exist_ok=True)
    os.makedirs(arquivos_dest_dir, exist_ok=True)
    
    # 3. Ler o log de conversa original
    try:
        with open(txt_file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  [ERRO] Falha ao ler conversa original: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    # 4. Processar arquivos extraídos, converter áudios e copiar para os destinos estruturados
    processed_lines = []
    audio_count = 0
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        # Detectar áudios PTT
        ptt_match = re.search(r'(PTT-\d+-WA\d+\.opus)', line_clean)
        
        if ptt_match:
            opus_name = ptt_match.group(1)
            opus_temp_path = os.path.join(temp_dir, opus_name)
            
            if os.path.exists(opus_temp_path):
                # Copia o original .opus para a pasta PTT/
                shutil.copy(opus_temp_path, os.path.join(ptt_dest_dir, opus_name))
                
                # Converter para WAV mono 16kHz
                wav_name = os.path.splitext(opus_name)[0] + ".wav"
                wav_dest_path = os.path.join(ptt_dest_dir, wav_name)
                
                print(f"  🎙️ Áudio encontrado: {opus_name}")
                if convert_opus_to_wav(os.path.join(ptt_dest_dir, opus_name), wav_dest_path):
                    # Realizar a transcrição do áudio
                    transcript = transcribe_wav(wav_dest_path)
                    print(f"    Transcrição: {transcript}")
                    
                    # Salvar transcrição individual no PTT/
                    trans_file_name = os.path.splitext(opus_name)[0] + "_transcription.txt"
                    with open(os.path.join(ptt_dest_dir, trans_file_name), "w", encoding="utf-8") as tf:
                        tf.write(transcript)
                        
                    # Adicionar transcrição na linha do chat
                    line_with_trans = line_clean + f" [TRANSCRIÇÃO]: {transcript}\n"
                    processed_lines.append(line_with_trans)
                    audio_count += 1
                else:
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
        else:
            # Não é um áudio PTT, vamos ver se é outro tipo de anexo para organizar
            # Se for imagem ou outro documento, copia para a pasta arquivos/
            # E adiciona a linha original ao arquivo processado
            processed_lines.append(line)
            
            # Tentar capturar nome de anexo genérico ou de imagem
            # Ex: IMG-20260520-WA0029.jpg (arquivo anexado)
            file_match = re.search(r'([^\:\s]+\.(?:jpg|png|pdf|docx|doc|xlsx|zip))\s*\(arquivo anexado\)', line_clean, re.IGNORECASE)
            if file_match:
                att_name = file_match.group(1)
                att_temp_path = os.path.join(temp_dir, att_name)
                if os.path.exists(att_temp_path):
                    shutil.copy(att_temp_path, os.path.join(arquivos_dest_dir, att_name))

    # Copiar fotos ou documentos que estão soltos na pasta temporária e que possam não ter sido detectados
    # por regex no log, garantindo que tudo vá para arquivos/ ou PTT/
    for item in os.listdir(temp_dir):
        item_path = os.path.join(temp_dir, item)
        if os.path.isdir(item_path) or item == txt_file_name:
            continue
            
        if item.endswith(".opus") or item.endswith(".wav"):
            dest_item_path = os.path.join(ptt_dest_dir, item)
        else:
            dest_item_path = os.path.join(arquivos_dest_dir, item)
            
        # Copia se ainda não foi copiado
        if not os.path.exists(dest_item_path):
            shutil.copy(item_path, dest_item_path)

    # 5. Salvar o arquivo de log do chat atualizado diretamente na pasta do cliente
    dest_txt_path = os.path.join(client_dest_dir, txt_file_name)
    with open(dest_txt_path, "w", encoding="utf-8") as f:
        f.writelines(processed_lines)
    print(f"  [OK] Chat txt atualizado salvo em: {dest_txt_path}")

    # 6. Gerar o Relatório em PDF na pasta do cliente
    output_pdf_path = os.path.join(client_dest_dir, f"Relatório - {client_name}.pdf")
    generate_pdf_report(client_name, processed_lines, output_pdf_path)

    # Limpar arquivos temporários
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"[OK] Cliente {client_name} processado. Áudios transcritos: {audio_count}")
    
    # Se for arquivo local, movemos o zip original para a pasta arquivos/ do cliente
    if is_local_file and os.path.exists(zip_source):
        try:
            shutil.move(zip_source, os.path.join(arquivos_dest_dir, os.path.basename(zip_source)))
            print(f"  [OK] ZIP original movido para: {os.path.join(arquivos_dest_dir, os.path.basename(zip_source))}")
        except Exception as e:
            print(f"  [AVISO] Não foi possível mover o arquivo ZIP original: {e}")
            
    return True
