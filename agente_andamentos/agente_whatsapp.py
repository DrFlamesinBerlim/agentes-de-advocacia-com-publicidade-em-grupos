"""
agente_whatsapp.py — Exportação e parsing de conversas do WhatsApp.

Modos:
  python agente_whatsapp.py parse   <arquivo.txt>   → processa export do WhatsApp
  python agente_whatsapp.py prova   <arquivo.txt>   → gera PDF formatado como prova processual
  python agente_whatsapp.py contato <arquivo.txt>   → lista contatos e contagem de mensagens

Como exportar do WhatsApp:
  Android/iPhone → Conversa → ⋮ Menu → Mais → Exportar conversa → Sem mídia (ou com mídia)
  O arquivo gerado é um .txt com o formato:
  [DD/MM/AAAA HH:MM:SS] Contato: Mensagem
"""

import re
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

BASE = Path(r"C:/Users/advog/Meu Drive/X")
SAIDA_DIR = BASE / "documentos" / "whatsapp"

# Padrões de data do WhatsApp (Android e iPhone variam)
PADROES_DATA = [
    re.compile(r"\[(\d{2}/\d{2}/\d{4}),?\s(\d{2}:\d{2}:\d{2})\]\s([^:]+):\s(.+)"),  # iPhone
    re.compile(r"(\d{2}/\d{2}/\d{4})\s(\d{2}:\d{2})\s-\s([^:]+):\s(.+)"),            # Android
]


def parse_arquivo(caminho: str) -> list[dict]:
    """Lê o .txt exportado e retorna lista de mensagens estruturadas."""
    msgs = []
    caminho = Path(caminho)
    if not caminho.exists():
        print(f"[ERRO] Arquivo não encontrado: {caminho}")
        return []

    with open(caminho, encoding="utf-8", errors="replace") as f:
        linhas = f.readlines()

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        for padrao in PADROES_DATA:
            m = padrao.match(linha)
            if m:
                data_str, hora_str, contato, texto = m.groups()
                try:
                    dt = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    try:
                        dt = datetime.strptime(f"{data_str} {hora_str}", "%d/%m/%Y %H:%M")
                    except ValueError:
                        dt = None
                msgs.append({
                    "datetime": dt.isoformat() if dt else f"{data_str} {hora_str}",
                    "data": data_str,
                    "hora": hora_str,
                    "contato": contato.strip(),
                    "mensagem": texto.strip(),
                })
                break

    print(f"[PARSE] {len(msgs)} mensagens encontradas em {caminho.name}")
    return msgs


def listar_contatos(msgs: list[dict]) -> None:
    contagem = defaultdict(int)
    for m in msgs:
        contagem[m["contato"]] += 1
    print("\n📱 CONTATOS NA CONVERSA:")
    for contato, qtd in sorted(contagem.items(), key=lambda x: -x[1]):
        print(f"  {contato}: {qtd} mensagens")


def salvar_json(msgs: list[dict], nome_base: str) -> Path:
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    saida = SAIDA_DIR / f"{nome_base}_parsed.json"
    dados = {
        "exportado_em": datetime.now(timezone.utc).isoformat(),
        "total_mensagens": len(msgs),
        "mensagens": msgs,
    }
    saida.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SALVO] {saida}")
    return saida


def gerar_prova_txt(msgs: list[dict], nome_base: str, processo: str = "") -> Path:
    """Gera arquivo .txt formatado para juntada como prova processual."""
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    saida = SAIDA_DIR / f"{nome_base}_PROVA_PROCESSUAL.txt"

    cabecalho = (
        "=" * 70 + "\n"
        "TRANSCRIÇÃO DE CONVERSA — WHATSAPP\n"
        f"Processo: {processo or 'A PREENCHER'}\n"
        f"Data de exportação: {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n"
        f"Total de mensagens: {len(msgs)}\n"
        "Autenticidade: exportação direta do aplicativo WhatsApp\n"
        "=" * 70 + "\n\n"
    )

    corpo = ""
    for m in msgs:
        corpo += f"[{m['data']} {m['hora']}] {m['contato']}:\n  {m['mensagem']}\n\n"

    saida.write_text(cabecalho + corpo, encoding="utf-8")
    print(f"[PROVA] Documento gerado: {saida}")
    return saida


def cmd_parse(arquivo):
    msgs = parse_arquivo(arquivo)
    if msgs:
        nome = Path(arquivo).stem
        salvar_json(msgs, nome)
        listar_contatos(msgs)


def cmd_prova(arquivo):
    msgs = parse_arquivo(arquivo)
    if msgs:
        nome = Path(arquivo).stem
        processo = input("Número do processo (Enter para pular): ").strip()
        gerar_prova_txt(msgs, nome, processo)
        salvar_json(msgs, nome)


def cmd_contato(arquivo):
    msgs = parse_arquivo(arquivo)
    if msgs:
        listar_contatos(msgs)


COMANDOS = {
    "parse":   cmd_parse,
    "prova":   cmd_prova,
    "contato": cmd_contato,
}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    arquivo = sys.argv[2]
    if cmd not in COMANDOS:
        print(f"Comando inválido: {cmd}. Use: {list(COMANDOS.keys())}")
        sys.exit(1)
    COMANDOS[cmd](arquivo)
