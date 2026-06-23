"""
sync_github.py — Ponte entre Antigravity (local) e Claude (nuvem) via GitHub.

Como funciona:
  1. Antigravity escreve em antigravity_output.txt (local)
  2. Este script faz push automático para o GitHub
  3. Claude lê o arquivo no GitHub e escreve em claude_output.txt no repo
  4. Este script faz pull e copia claude_output.txt para a Pasta X local
  5. loop_monitor.py detecta a mudança e executa as tags XML

Resultado: Claude e Antigravity falam a mesma língua via GitHub.
"""

import subprocess
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(r"C:/Users/advog/Meu Drive/X")
REPO_DIR = BASE / "repo"  # git clone do repositório aqui
LOG_FILE = BASE / "antigravity_output.txt"

REPO_URL = "https://github.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos.git"
BRANCH = "claude/upbeat-fermat-0x6gd8"

ARQUIVOS_SYNC_PUSH = [
    "antigravity_output.txt",
    "documentos/processos.json",
    "documentos/prazos_pendentes.json",
    "sync_state.json",
    "STATUS_OFFICE.md",
]

ARQUIVOS_SYNC_PULL = [
    "claude_output.txt",
]

logging.basicConfig(
    filename=str(LOG_FILE),
    filemode="a",
    format="%(asctime)s [SYNC_GITHUB] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.INFO,
)
log = logging.getLogger("sync_github")


def run(cmd: list, cwd=None) -> str:
    result = subprocess.run(cmd, cwd=cwd or REPO_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        log.warning("CMD ERRO: %s\n%s", " ".join(cmd), result.stderr)
    return result.stdout.strip()


def clone_ou_pull():
    if not REPO_DIR.exists():
        log.info("Clonando repositório...")
        subprocess.run(["git", "clone", "-b", BRANCH, REPO_URL, str(REPO_DIR)], check=True)
    else:
        run(["git", "pull", "origin", BRANCH])


def push_para_github():
    """Copia arquivos locais da Pasta X para o repo e faz push."""
    alterou = False
    for arquivo in ARQUIVOS_SYNC_PUSH:
        origem = BASE / arquivo
        destino = REPO_DIR / arquivo
        if not origem.exists():
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists() or origem.read_bytes() != destino.read_bytes():
            shutil.copy2(origem, destino)
            run(["git", "add", arquivo])
            alterou = True
            log.info("STAGED para push: %s", arquivo)

    if alterou:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        run(["git", "commit", "-m", f"sync(antigravity): atualização automática {ts}"])
        run(["git", "push", "origin", BRANCH])
        log.info("PUSH concluído para GitHub")
    else:
        log.info("Nenhuma alteração para push")


def pull_do_github():
    """Faz pull e copia claude_output.txt do repo para a Pasta X local."""
    run(["git", "pull", "origin", BRANCH])
    for arquivo in ARQUIVOS_SYNC_PULL:
        origem = REPO_DIR / arquivo
        destino = BASE / arquivo
        if not origem.exists():
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        conteudo_novo = origem.read_bytes()
        conteudo_atual = destino.read_bytes() if destino.exists() else b""
        if conteudo_novo != conteudo_atual:
            shutil.copy2(origem, destino)
            log.info("PULL aplicado localmente: %s", arquivo)


def loop(intervalo: int = 10):
    """Loop principal: push a cada ciclo, pull para detectar instruções do Claude."""
    log.info("=== SYNC_GITHUB INICIADO (intervalo=%ds) ===", intervalo)
    clone_ou_pull()
    while True:
        try:
            push_para_github()
            pull_do_github()
        except Exception as e:
            log.exception("Erro no ciclo de sync: %s", e)
        time.sleep(intervalo)


if __name__ == "__main__":
    loop(intervalo=10)
