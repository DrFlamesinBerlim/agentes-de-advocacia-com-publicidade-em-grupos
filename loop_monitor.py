"""
loop_monitor.py — Watchdog principal do Antigravity (De Brito Advocacia)

Ciclo permanente:
  1. Puxa GitHub (sync_github.py pull)
  2. Lê claude_output.txt e executa tags XML
  3. A cada MABIOS_INTERVAL minutos: processa rascunhos MABIOS
  4. A cada FULL_INTERVAL minutos: pipeline completo (DataJud + prazos + calendar)
  5. Push do antigravity_output.txt para o GitHub

Iniciar:
  python loop_monitor.py

Parar:
  Ctrl+C  ou  Stop-Process -Name python -Force
"""

import subprocess
import sys
import time
import logging
import re
import shutil
from pathlib import Path
from datetime import datetime, timezone

# ─── Configuração ─────────────────────────────────────────────────────────────

BASE        = Path(r"C:/Users/advog/Meu Drive/X")
REPO_DIR    = BASE  # o repo git é a própria Pasta X
CANAL_IN    = BASE / "claude_output.txt"
CANAL_OUT   = BASE / "antigravity_output.txt"
AGENTE_DIR  = BASE / "agente_andamentos"

LOG_FILE    = BASE / "logs" / "loop_monitor.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

WATCH_INTERVAL  = 30    # segundos entre cada leitura do claude_output.txt
MABIOS_INTERVAL = 15    # minutos entre cada rodada de rascunhos MABIOS
FULL_INTERVAL   = 120   # minutos entre cada pipeline completo (DataJud)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [MONITOR] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("loop_monitor")


# ─── Utilitários ──────────────────────────────────────────────────────────────

def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_out(msg: str) -> None:
    """Append ao antigravity_output.txt."""
    with open(CANAL_OUT, "a", encoding="utf-8") as f:
        f.write(f"\n[{stamp()}] {msg}\n")


def run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    """Executa comando e retorna (returncode, output)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(AGENTE_DIR),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return -1, f"TIMEOUT ({timeout}s)"
    except Exception as e:
        return -1, str(e)


def agente(modulo: str) -> tuple[int, str]:
    """Chama: python agente_andamentos.py <modulo>"""
    return run([sys.executable, "agente_andamentos.py", modulo])


# ─── Sync GitHub ──────────────────────────────────────────────────────────────

def git_pull() -> bool:
    code, out = run(
        ["git", "pull", "origin", "claude/upbeat-fermat-0x6gd8"],
        timeout=60,
    )
    if code == 0:
        log.info("git pull OK")
        return True
    log.warning("git pull falhou: %s", out)
    return False


def git_push() -> bool:
    run(["git", "add", "antigravity_output.txt"], timeout=30)
    code, out = run(
        ["git", "commit", "-m", f"Antigravity report {stamp()}"],
        timeout=30,
    )
    if "nothing to commit" in out:
        return True
    code2, out2 = run(
        ["git", "push", "-u", "origin", "claude/upbeat-fermat-0x6gd8"],
        timeout=60,
    )
    if code2 == 0:
        log.info("git push OK")
        return True
    log.warning("git push falhou: %s", out2)
    return False


# ─── Parser de tags XML do claude_output.txt ──────────────────────────────────

PROCESSED_MARKER = BASE / ".canal_last_hash"


def canal_hash() -> str:
    if not CANAL_IN.exists():
        return ""
    import hashlib
    return hashlib.md5(CANAL_IN.read_bytes()).hexdigest()


def canal_mudou() -> bool:
    atual = canal_hash()
    if not PROCESSED_MARKER.exists():
        PROCESSED_MARKER.write_text(atual)
        return True
    anterior = PROCESSED_MARKER.read_text().strip()
    if atual != anterior:
        PROCESSED_MARKER.write_text(atual)
        return True
    return False


def executar_tags_xml() -> None:
    """Lê claude_output.txt e executa <commands> e <write_file>."""
    if not CANAL_IN.exists():
        return

    texto = CANAL_IN.read_text(encoding="utf-8", errors="replace")

    # <commands> ... </commands>
    for bloco in re.findall(r"<commands>(.*?)</commands>", texto, re.DOTALL):
        cmds = [l.strip() for l in bloco.strip().splitlines() if l.strip() and not l.strip().startswith("REM")]
        for cmd_str in cmds:
            log.info("Executando: %s", cmd_str)
            code, out = run(cmd_str.split(), timeout=180)
            status = "OK" if code == 0 else f"ERRO ({code})"
            log.info("%s: %s", status, out[:200])
            log_out(f"[CMD:{status}] {cmd_str}\n{out[:500]}")

    # <write_file path="..."> ... </write_file>
    for match in re.finditer(r'<write_file\s+path="([^"]+)">(.*?)</write_file>', texto, re.DOTALL):
        path_str, content = match.group(1), match.group(2)
        try:
            dest = Path(path_str)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            log.info("write_file OK: %s", path_str)
            log_out(f"[WRITE:OK] {path_str}")
        except Exception as e:
            log.error("write_file falhou (%s): %s", path_str, e)
            log_out(f"[WRITE:ERRO] {path_str} — {e}")

    # MABIOS_ACTION inline no canal
    if "MABIOS_ACTION:" in texto:
        log.info("MABIOS_ACTION detectado no canal — processando...")
        code, out = agente("mabios")
        log_out(f"[MABIOS:CANAL] {out[:500]}")


# ─── Tarefas periódicas ───────────────────────────────────────────────────────

last_mabios = 0.0
last_full   = 0.0


def checar_mabios() -> None:
    global last_mabios
    agora = time.time()
    if agora - last_mabios >= MABIOS_INTERVAL * 60:
        log.info("=== Rodada MABIOS (rascunhos Gmail) ===")
        code, out = agente("mabios")
        log.info("mabios: %s", out[:300] or "sem ações")
        log_out(f"[MABIOS:PERIODICO]\n{out[:800]}")
        last_mabios = agora


def checar_pipeline_completo() -> None:
    global last_full
    agora = time.time()
    if agora - last_full >= FULL_INTERVAL * 60:
        log.info("=== Pipeline completo (DataJud + prazos + calendar) ===")
        code, out = agente("atualizar")
        log.info("atualizar: %s", out[:300] or "ok")
        log_out(f"[PIPELINE:COMPLETO]\n{out[:800]}")
        last_full = agora


# ─── Loop principal ───────────────────────────────────────────────────────────

def main() -> None:
    global last_mabios, last_full

    log.info("=" * 55)
    log.info("ANTIGRAVITY LOOP MONITOR — De Brito Advocacia")
    log.info("Base: %s", BASE)
    log.info("Intervalo canal: %ds | MABIOS: %dmin | Pipeline: %dmin",
             WATCH_INTERVAL, MABIOS_INTERVAL, FULL_INTERVAL)
    log.info("=" * 55)

    log_out("[ANTIGRAVITY:BOOT] loop_monitor iniciado.")

    # Forçar primeira rodada imediatamente
    last_mabios = time.time() - MABIOS_INTERVAL * 60
    last_full   = time.time() - FULL_INTERVAL * 60

    while True:
        try:
            # 1. Puxar atualizações do GitHub
            git_pull()

            # 2. Processar claude_output.txt se mudou
            if canal_mudou():
                log.info("claude_output.txt mudou — processando tags XML")
                executar_tags_xml()

            # 3. Processar rascunhos MABIOS periodicamente
            checar_mabios()

            # 4. Pipeline completo periodicamente
            checar_pipeline_completo()

            # 5. Push do log para o GitHub
            git_push()

        except KeyboardInterrupt:
            log.info("Interrompido pelo usuário.")
            log_out("[ANTIGRAVITY:STOP] loop_monitor encerrado.")
            break
        except Exception as e:
            log.exception("Erro inesperado no loop: %s", e)
            log_out(f"[LOOP:ERRO] {e}")

        time.sleep(WATCH_INTERVAL)


if __name__ == "__main__":
    main()
