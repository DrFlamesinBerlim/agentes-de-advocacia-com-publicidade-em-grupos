import os
import time
import json
import hashlib
import re
import subprocess
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# CONFIGURAÇÕES DE MONITORAMENTO
MONITOR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(MONITOR_DIR, "sync_state.json")
LOG_FILE = os.path.join(MONITOR_DIR, "sync_history.log")
ANTIGRAVITY_OUTPUT = os.path.join(MONITOR_DIR, "antigravity_output.txt")
HEARTBEAT_INTERVAL = 300  # Fallback a cada 5 minutos

def get_file_hash(filepath):
    """Retorna o hash SHA-256 do arquivo para verificar mudanças de conteúdo reais."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception:
        return None

def log_event(message):
    """Registra eventos no log de histórico local."""
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] {message}\n"
    print(log_line.strip())
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as lf:
            lf.write(log_line)
    except Exception as e:
        print(f"Erro ao gravar log: {e}")

def load_state():
    """Carrega o último estado registrado no JSON para persistência."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_event(f"Erro ao carregar sync_state.json: {e}")
    return {"files": {}, "last_scan": None, "machine_id": os.environ.get("COMPUTERNAME", "UNKNOWN_PC")}

def save_state(state):
    """Salva o estado atualizado no JSON."""
    state["last_scan"] = datetime.now().isoformat()
    try:
        temp_file = STATE_FILE + ".tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, STATE_FILE)
    except Exception as e:
        log_event(f"Erro ao salvar sync_state.json: {e}")

def write_execution_result(output_content):
    """Escreve o resultado da execução em antigravity_output.txt."""
    try:
        timestamp = datetime.now().isoformat()
        with open(ANTIGRAVITY_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(f"# MABIOS EXECUTION LOG\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Mente: [ANTIGRAVITY:AGENTE_LOCAL]\n\n")
            f.write(output_content)
        log_event("Escreveu o resultado da execução em 'antigravity_output.txt'")
    except Exception as e:
        log_event(f"Erro ao gravar antigravity_output.txt: {e}")

def execute_agent_instructions(filepath, agent_name):
    """Lê o arquivo de instruções do agente, cria arquivos e executa comandos se houver tags XML."""
    log_event(f"[MABIOS] Processando instruções de '{agent_name}' em '{os.path.basename(filepath)}'")
    
    # Pequena pausa extra para garantir a liberação do arquivo pelo sincronizador do Drive
    time.sleep(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log_event(f"Erro ao ler arquivo de instruções: {e}")
        return

    # 1. Parse de arquivos para escrever (<write_file path="...">...</write_file>)
    write_blocks = re.findall(r'<write_file\s+path="([^"]+)">([\s\S]*?)<\/write_file>', content)
    for path, code in write_blocks:
        normalized_path = os.path.abspath(path.strip())
        log_event(f"[MABIOS] Gravando arquivo por solicitação de {agent_name}: '{normalized_path}'")
        try:
            os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
            with open(normalized_path, 'w', encoding='utf-8') as wf:
                wf.write(code.strip())
            log_event(f"[SUCESSO] Arquivo gravado com sucesso.")
        except Exception as e:
            log_event(f"[ERRO] Falha ao gravar arquivo '{normalized_path}': {e}")

    # 2. Parse de comandos para executar (<commands>...</commands>)
    commands_blocks = re.findall(r'<commands>([\s\S]*?)<\/commands>', content)
    execution_results = []
    
    for block in commands_blocks:
        commands = [cmd.strip() for cmd in block.strip().split('\n') if cmd.strip()]
        for cmd in commands:
            log_event(f"[MABIOS] Executando comando de {agent_name}: '{cmd}'")
            execution_results.append(f"--- COMANDO: {cmd} ---")
            try:
                # Executa no diretório do monitor
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=MONITOR_DIR, timeout=60)
                stdout = res.stdout.strip()
                stderr = res.stderr.strip()
                
                if stdout:
                    execution_results.append(f"[STDOUT]\n{stdout}")
                if stderr:
                    execution_results.append(f"[STDERR]\n{stderr}")
                execution_results.append(f"Código de retorno: {res.returncode}\n")
                log_event(f"[CONCLUÍDO] Retorno: {res.returncode}")
            except subprocess.TimeoutExpired:
                execution_results.append("[TIMEOUT] Comando excedeu o limite de 60 segundos.\n")
                log_event(f"[TIMEOUT] Comando expirou.")
            except Exception as e:
                execution_results.append(f"[ERRO DE EXECUÇÃO] {e}\n")
                log_event(f"[ERRO] Falha ao rodar comando: {e}")

    # Se executou algo, escreve o resultado no antigravity_output.txt
    if write_blocks or commands_blocks:
        result_text = "\n".join(execution_results) if execution_results else "Arquivos gravados com sucesso. Nenhum comando de terminal solicitado."
        write_execution_result(result_text)

    # Renomeia o arquivo para evitar re-execução em loop
    processed_path = filepath + ".processed"
    try:
        if os.path.exists(processed_path):
            os.remove(processed_path)
        os.rename(filepath, processed_path)
        log_event(f"[MABIOS] Arquivo renomeado para '{os.path.basename(processed_path)}' para evitar re-execução.")
    except Exception as e:
        log_event(f"Erro ao renomear arquivo processado: {e}")

def scan_directory():
    """Varre o diretório monitorado, executa comandos recebidos e detecta modificações."""
    state = load_state()
    current_files = {}
    changes_detected = False

    # Verifica se há arquivos de entrada de agentes para executar
    claude_in = os.path.join(MONITOR_DIR, "claude_output.txt")
    gemini_in = os.path.join(MONITOR_DIR, "gemini_output.txt")

    if os.path.exists(claude_in):
        execute_agent_instructions(claude_in, "Claude")
        changes_detected = True

    if os.path.exists(gemini_in):
        execute_agent_instructions(gemini_in, "Gemini")
        changes_detected = True

    # Varre a raiz do diretório X
    for entry in os.scandir(MONITOR_DIR):
        if entry.is_file():
            filename = entry.name
            # Ignora arquivos de estado, log, outputs ou arquivos processados
            if filename in ("sync_state.json", "sync_history.log", "sync_state.json.tmp", "antigravity_output.txt", "claude_output.txt", "gemini_output.txt") or filename.endswith(".processed"):
                continue

            filepath = entry.path
            try:
                mtime = entry.stat().st_mtime
                file_hash = get_file_hash(filepath)
                current_files[filename] = {
                    "mtime": mtime,
                    "hash": file_hash,
                    "last_checked": datetime.now().isoformat()
                }

                # Verifica se é um arquivo novo ou se foi modificado
                old_info = state["files"].get(filename)
                if not old_info:
                    log_event(f"[NOVO ARQUIVO] Detectado: '{filename}' (mtime: {time.ctime(mtime)})")
                    changes_detected = True
                elif old_info.get("hash") != file_hash:
                    log_event(f"[MODIFICAÇÃO] Detectado alteração em: '{filename}' (novo hash: {file_hash[:8]}...)")
                    changes_detected = True

            except Exception as e:
                log_event(f"Erro ao ler arquivo '{filename}': {e}")

    # Detecta arquivos deletados
    for old_filename in list(state["files"].keys()):
        if old_filename not in current_files:
            log_event(f"[REMOÇÃO] Arquivo removido ou renomeado: '{old_filename}'")
            changes_detected = True

    # Se houve mudanças, atualiza o arquivo de estado
    if changes_detected:
        state["files"] = current_files
        save_state(state)
    else:
        save_state(state)

class MabiosHandler(FileSystemEventHandler):
    """Manipulador de eventos do sistema de arquivos para responder em tempo real."""
    def process(self, event):
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
        # Ignora arquivos internos de estado do monitor para evitar loop recursivo
        if filename in ("sync_state.json", "sync_history.log", "sync_state.json.tmp", "antigravity_output.txt") or filename.endswith(".processed"):
            return
            
        # Debounce de 2 segundos para dar tempo do arquivo ser completamente baixado/escrito pelo Drive
        time.sleep(2)
        log_event(f"[FUNDO] Evento de sistema de arquivos detectado para '{filename}'. Escaneando...")
        scan_directory()

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

def main():
    log_event(f"Iniciando monitoramento MABIOS v3 (Event-Driven com Watchdog) em '{MONITOR_DIR}'...")
    
    # Executa varredura inicial
    scan_directory()
    
    # Configura e inicia o Watchdog Observer
    event_handler = MabiosHandler()
    observer = Observer()
    observer.schedule(event_handler, MONITOR_DIR, recursive=False)
    observer.start()
    
    log_event("[SISTEMA] Watchdog ativado. Escuta ativa e execução instantânea ligada!")
    
    try:
        while True:
            # Fallback/Heartbeat periódico a cada 5 minutos
            time.sleep(HEARTBEAT_INTERVAL)
            log_event("[SISTEMA] Heartbeat periódico de segurança executado.")
            scan_directory()
    except KeyboardInterrupt:
        log_event("[SISTEMA] Encerrando monitoramento...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
