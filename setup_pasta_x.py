"""
PROMPT DO AGENTE — SETUP DA PASTA X (De Brito Advocacia)

Você é um agente Python autônomo responsável por criar e inicializar
a estrutura completa da Pasta X no Google Drive local. Siga as etapas
abaixo sem desvio. Relate cada ação concluída no antigravity_output.txt.

OBJETIVO:
  Criar todos os diretórios, subdiretórios e arquivos-esqueleto necessários
  para o ecossistema Trans-LLM funcionar corretamente desde o primeiro boot.

REGRAS:
  - Nunca sobrescrever arquivo existente com conteúdo não-vazio.
  - Logar cada operação em antigravity_output.txt (append mode).
  - Ao terminar, escrever [SETUP:DONE] na última linha do log.
  - Em caso de erro em qualquer etapa, escrever [SETUP:ERROR] + traceback.
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

# ── Configuração ──────────────────────────────────────────────────────────────

BASE = Path(r"C:/Users/advog/Meu Drive/X")
LOG_FILE = BASE / "antigravity_output.txt"

logging.basicConfig(
    filename=str(LOG_FILE),
    filemode="a",
    format="%(asctime)s [SETUP] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.INFO,
)
log = logging.getLogger("setup_pasta_x")


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_write(path: Path, content: str) -> None:
    """Cria o arquivo apenas se estiver ausente ou vazio."""
    if path.exists() and path.stat().st_size > 0:
        log.info("SKIP (já existe) — %s", path)
        return
    path.write_text(content, encoding="utf-8")
    log.info("CRIADO — %s", path)


# ── Estrutura de diretórios ───────────────────────────────────────────────────

DIRS = [
    BASE,
    BASE / "documentos",
    BASE / "agente_andamentos",
    BASE / "rascunhos",
    BASE / "logs",
]


def create_dirs() -> None:
    for d in DIRS:
        d.mkdir(parents=True, exist_ok=True)
        log.info("DIR OK — %s", d)


# ── Arquivos-esqueleto ────────────────────────────────────────────────────────

def create_skeleton_files() -> None:

    # antigravity_output.txt — preenchido pelo agente local; inicia vazio c/ header
    safe_write(
        BASE / "antigravity_output.txt",
        f"# antigravity_output.txt — gerado em {stamp()}\n"
        "[SYSTEM:BOOT] Antigravity ainda não reportou status.\n",
    )

    # claude_output.txt — onde o Claude escreve instruções XML
    safe_write(
        BASE / "claude_output.txt",
        f"# claude_output.txt — gerado em {stamp()}\n"
        "# Claude deve escrever tags XML aqui para controlar a máquina local.\n",
    )

    # gemini_output.txt — reservado para futuro agente Gemini
    safe_write(
        BASE / "gemini_output.txt",
        f"# gemini_output.txt — gerado em {stamp()}\n",
    )

    # STATUS_OFFICE.md
    safe_write(
        BASE / "STATUS_OFFICE.md",
        "# STATUS DO ESCRITÓRIO\n\n"
        "**Lock:** `[OFFICE:STANDBY]`\n\n"
        f"*Inicializado em: {stamp()}*\n",
    )

    # prompt.txt — protocolo MABIOS
    safe_write(
        BASE / "prompt.txt",
        "# MABIOS — Protocolo de Comunicação Inter-Agentes\n\n"
        "Versão: 1.0\n"
        "Escritório: De Brito Advocacia\n"
        f"Gerado: {stamp()}\n\n"
        "## Regras gerais\n"
        "1. Toda instrução ao agente local deve ser encapsulada em XML.\n"
        "2. Claude escreve em claude_output.txt; Antigravity lê e executa.\n"
        "3. Antigravity reporta resultados em antigravity_output.txt.\n"
        "4. Nenhum agente sobrescreve o arquivo do outro sem lock.\n",
    )

    # zzz_init.md — compliance
    safe_write(
        BASE / "zzz_init.md",
        "# COMPLIANCE OAB/RO 2952 — Anti-Alucinação\n\n"
        "- Nunca afirmar fatos processuais sem fonte verificada em processos.json.\n"
        "- Nunca calcular prazo sem conferir o calendário judicial atualizado.\n"
        "- Nunca redigir peça sem confirmação explícita do Dr. Jefferson (VSI).\n"
        "- Toda saída deve citar o número do processo e o andamento-base.\n",
    )

    # PROMPT_COORDENACAO_AGENTES.md
    safe_write(
        BASE / "PROMPT_COORDENACAO_AGENTES.md",
        "# Coordenação Multi-Máquinas — Regras de Sincronização\n\n"
        "## Concorrência\n"
        "- Apenas um agente por vez pode escrever em claude_output.txt.\n"
        "- Use sync_state.json para verificar o hash do último estado lido.\n\n"
        "## Handshake\n"
        "1. Agente lê sync_state.json e extrai `last_hash`.\n"
        "2. Agente computa SHA-256 do arquivo alvo antes de escrever.\n"
        "3. Se hashes coincidem, prossegue; caso contrário, aguarda 2s e retry.\n",
    )

    # sync_state.json
    initial_sync = {
        "last_hash": hashlib.sha256(b"").hexdigest(),
        "last_updated": stamp(),
        "last_agent": "setup_pasta_x.py",
    }
    safe_write(
        BASE / "sync_state.json",
        json.dumps(initial_sync, ensure_ascii=False, indent=2),
    )

    # ledger.json
    safe_write(
        BASE / "ledger.json",
        json.dumps(
            {"transacoes": [], "gerado_em": stamp()},
            ensure_ascii=False, indent=2
        ),
    )

    # documentos/processos.json
    safe_write(
        BASE / "documentos" / "processos.json",
        json.dumps(
            {"processos": [], "atualizado_em": stamp()},
            ensure_ascii=False, indent=2
        ),
    )

    # documentos/prazos_pendentes.json
    safe_write(
        BASE / "documentos" / "prazos_pendentes.json",
        json.dumps(
            {"prazos": [], "atualizado_em": stamp()},
            ensure_ascii=False, indent=2
        ),
    )

    # agente_andamentos/__init__.py
    safe_write(BASE / "agente_andamentos" / "__init__.py", "")

    # loop_monitor.py — esqueleto mínimo para o watchdog
    safe_write(
        BASE / "loop_monitor.py",
        '"""\nloop_monitor.py — Monitor em segundo plano (watchdog).\n'
        "Lê claude_output.txt em busca de tags XML e executa as instruções.\n"
        'Substitua este esqueleto pela implementação completa do Antigravity.\n"""\n\n'
        "# TODO: implementar watchdog sobre claude_output.txt\n"
        "if __name__ == '__main__':\n"
        "    print('[MONITOR] Esqueleto iniciado. Implemente o watchdog aqui.')\n",
    )


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    log.info("=== INÍCIO DO SETUP DA PASTA X ===")
    try:
        create_dirs()
        create_skeleton_files()
        log.info("=== SETUP CONCLUÍDO COM SUCESSO ===")
        print("[SETUP:DONE] Estrutura da Pasta X criada em:", BASE)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[SETUP:DONE]\n")
    except Exception as exc:
        log.exception("Falha durante o setup")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[SETUP:ERROR] {exc}\n")
        raise


if __name__ == "__main__":
    main()
