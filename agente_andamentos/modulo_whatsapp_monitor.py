"""
modulo_whatsapp_monitor.py — Monitoramento automático de exports WhatsApp.

Monitora a pasta documentos/whatsapp/inbox/ a cada ciclo do loop_monitor.
Quando encontra um .txt novo, processa automaticamente:
  1. Parse das mensagens → JSON estruturado
  2. Geração de prova processual (.txt formatado)
  3. Move o arquivo para documentos/whatsapp/processados/
  4. Registra no antigravity_output.txt

Uso direto:
  python modulo_whatsapp_monitor.py          → processa todos os .txt pendentes
  python modulo_whatsapp_monitor.py <arquivo> → processa arquivo específico

Para integrar com o loop_monitor, basta chamar checar_inbox() a cada ciclo.
"""

import json
import logging
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE        = Path(r"C:/Users/advog/Meu Drive/X")
INBOX_DIR   = BASE / "documentos" / "whatsapp" / "inbox"
SAIDA_DIR   = BASE / "documentos" / "whatsapp" / "processados"
LOG_FILE    = BASE / "antigravity_output.txt"
CANAL_OUT   = BASE / "antigravity_output.txt"

PADROES_DATA = [
    re.compile(r"\[(\d{2}/\d{2}/\d{4}),?\s(\d{2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)"),  # iPhone
    re.compile(r"(\d{2}/\d{2}/\d{4})\s(\d{2}:\d{2})\s-\s([^:]+):\s(.+)"),            # Android
]

logging.basicConfig(
    filename=str(LOG_FILE), filemode="a",
    format="%(asctime)s [WA_MONITOR] %(levelname)s — %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("modulo_whatsapp_monitor")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log_out(msg: str) -> None:
    with open(CANAL_OUT, "a", encoding="utf-8") as f:
        f.write(f"\n[{_stamp()}] {msg}\n")


def _parse_arquivo(caminho: Path) -> list[dict]:
    msgs = []
    with open(caminho, encoding="utf-8", errors="replace") as f:
        linhas = f.readlines()

    msg_atual = None
    for linha in linhas:
        linha_strip = linha.strip()
        if not linha_strip:
            continue

        matched = False
        for padrao in PADROES_DATA:
            m = padrao.match(linha_strip)
            if m:
                data_str, hora_str, contato, texto = m.groups()
                try:
                    dt = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    try:
                        dt = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%Y %H:%M")
                    except ValueError:
                        dt = None
                msg_atual = {
                    "datetime": dt.isoformat() if dt else f"{data_str} {hora_str}",
                    "data": data_str,
                    "hora": hora_str,
                    "contato": contato.strip(),
                    "mensagem": texto.strip(),
                }
                msgs.append(msg_atual)
                matched = True
                break

        # Mensagem multilinhas — continua na linha seguinte
        if not matched and msg_atual is not None:
            msg_atual["mensagem"] += " " + linha_strip

    return msgs


def _salvar_json(msgs: list[dict], nome_base: str, saida_dir: Path) -> Path:
    saida_dir.mkdir(parents=True, exist_ok=True)
    saida = saida_dir / f"{nome_base}_parsed.json"
    dados = {
        "exportado_em": datetime.now(timezone.utc).isoformat(),
        "total_mensagens": len(msgs),
        "mensagens": msgs,
    }
    saida.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return saida


def _gerar_prova(msgs: list[dict], nome_base: str, saida_dir: Path, processo: str = "") -> Path:
    saida_dir.mkdir(parents=True, exist_ok=True)
    saida = saida_dir / f"{nome_base}_PROVA_PROCESSUAL.txt"

    contagem: dict[str, int] = defaultdict(int)
    for m in msgs:
        contagem[m["contato"]] += 1
    contatos_str = " | ".join(f"{c} ({n} msgs)" for c, n in sorted(contagem.items(), key=lambda x: -x[1]))

    cabecalho = (
        "=" * 70 + "\n"
        "TRANSCRIÇÃO DE CONVERSA — WHATSAPP\n"
        f"Processo: {processo or 'A PREENCHER'}\n"
        f"Data de exportação: {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n"
        f"Total de mensagens: {len(msgs)}\n"
        f"Participantes: {contatos_str}\n"
        "Autenticidade: exportação direta do aplicativo WhatsApp\n"
        "Advogado: Dr. Jefferson Silva de Brito — OAB/RO 2952\n"
        "=" * 70 + "\n\n"
    )

    corpo = ""
    for m in msgs:
        corpo += f"[{m['data']} {m['hora']}] {m['contato']}:\n  {m['mensagem']}\n\n"

    saida.write_text(cabecalho + corpo, encoding="utf-8")
    return saida


def processar_arquivo(caminho: Path) -> bool:
    """Processa um .txt do WhatsApp e move para a pasta de processados."""
    log.info("Processando: %s", caminho.name)
    try:
        msgs = _parse_arquivo(caminho)
        if not msgs:
            log.warning("Nenhuma mensagem encontrada em %s", caminho.name)
            return False

        nome_base = caminho.stem
        SAIDA_DIR.mkdir(parents=True, exist_ok=True)

        json_path  = _salvar_json(msgs, nome_base, SAIDA_DIR)
        prova_path = _gerar_prova(msgs, nome_base, SAIDA_DIR)

        # Conta participantes e período
        contatos = {m["contato"] for m in msgs}
        primeira = msgs[0]["data"] if msgs else "?"
        ultima   = msgs[-1]["data"] if msgs else "?"

        resumo = (
            f"[WA:OK] {caminho.name} — {len(msgs)} msgs | "
            f"{len(contatos)} participante(s) | {primeira}→{ultima}\n"
            f"  → JSON: {json_path.name}\n"
            f"  → PROVA: {prova_path.name}"
        )
        log.info(resumo)
        _log_out(resumo)

        # Move o arquivo original para processados/originals
        originals = SAIDA_DIR / "originals"
        originals.mkdir(parents=True, exist_ok=True)
        shutil.move(str(caminho), str(originals / caminho.name))
        log.info("Movido para: %s", originals / caminho.name)

        return True

    except Exception as e:
        log.error("Erro processando %s: %s", caminho.name, e)
        _log_out(f"[WA:ERRO] {caminho.name} — {e}")
        return False


def checar_inbox() -> int:
    """Verifica pasta inbox/ e processa todos os .txt pendentes. Retorna qtd processados."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    pendentes = sorted(INBOX_DIR.glob("*.txt"))
    if not pendentes:
        return 0

    log.info("%d arquivo(s) WhatsApp pendente(s)", len(pendentes))
    processados = sum(processar_arquivo(p) for p in pendentes)
    return processados


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arq = Path(sys.argv[1])
        if not arq.exists():
            print(f"[ERRO] Arquivo não encontrado: {arq}")
            sys.exit(1)
        ok = processar_arquivo(arq)
        sys.exit(0 if ok else 1)
    else:
        n = checar_inbox()
        print(f"[WA_MONITOR] {n} arquivo(s) processado(s).")
