"""
modulo_emails.py — Extração de tarefas jurídicas de 4 contas de e-mail
De Brito Advocacia | OAB/RO 2952

CANAIS MONITORADOS:
  1. advogadobrito@hotmail.com    → principal escritório (DJE, PJe, intimações)
  2. jeffersondebrito@hotmail.com → pessoal Dr. Jefferson
  3. tribuna.livre.ro@gmail.com   → institucional
  4. flamesinberlim@gmail.com     → pessoal/backup

ARQUITETURA:
  - Hotmail (1 e 2): Antigravity acessa via IMAP local (python-imaplib)
  - Gmail (3 e 4):   Claude acessa via Gmail MCP na nuvem

Como usar (Antigravity):
  python modulo_emails.py verificar   → varre todos os 4 e-mails
  python modulo_emails.py hotmail     → só contas hotmail (IMAP local)
  python modulo_emails.py exportar    → salva e-mails jurídicos em JSON
"""

import imaplib
import email
import json
import re
import sys
from pathlib import Path
from datetime import datetime, date, timezone, timedelta
from email.header import decode_header

BASE = Path(r"C:/Users/advog/Meu Drive/X")
EMAILS_JSON   = BASE / "documentos" / "emails_juridicos.json"
TAREFAS_JSON  = BASE / "documentos" / "tarefas.json"

# ─── Configuração das contas ────────────────────────────────────────────────

CONTAS = {
    "advogadobrito": {
        "email":    "advogadobrito@hotmail.com",
        "servidor": "imap-mail.outlook.com",
        "porta":    993,
        "tipo":     "IMAP",
        "prioridade": "PRINCIPAL",
    },
    "jeffersondebrito": {
        "email":    "jeffersondebrito@hotmail.com",
        "servidor": "imap-mail.outlook.com",
        "porta":    993,
        "tipo":     "IMAP",
        "prioridade": "SECUNDARIO",
    },
    "tribuna_gmail": {
        "email":    "tribuna.livre.ro@gmail.com",
        "tipo":     "GMAIL_MCP",
        "prioridade": "INSTITUCIONAL",
    },
    "flamesinberlim": {
        "email":    "flamesinberlim@gmail.com",
        "tipo":     "GMAIL_MCP",
        "prioridade": "BACKUP",
    },
}

# Remetentes e assuntos que indicam movimentação jurídica
FILTROS_JURIDICOS = {
    "remetentes": [
        "noreply@pje",
        "pje@tjro",
        "dje@tjro",
        "tjro.jus.br",
        "tjam.jus.br",
        "stj.jus.br",
        "cnj.jus.br",
        "datajud",
        "noreply@projudi",
        "intimacao",
        "notificacao",
        "2turmarecursal@tjro",
    ],
    "assuntos": [
        "intimação", "intimacao", "citação", "citacao",
        "prazo", "diário", "dje", "pje", "pauta",
        "julgamento", "sentença", "sentenca", "decisão", "decisao",
        "despacho", "acórdão", "acordao", "recurso",
        "mandado", "cumprimento", "execução", "execucao",
        "audiência", "audiencia", "sessão", "sessao",
        "publicação", "publicacao", "disponibilização",
    ],
}

# Padrões regex para extrair dados de e-mails
REGEX_NUMERO = re.compile(
    r"\b(\d{7}-\d{2}\.\d{4}\.\d{1,2}\.\d{2}\.\d{4})\b"
)
REGEX_PRAZO = re.compile(
    r"prazo[^\d]*(\d{1,2})[^\d]*dias?\s*[úu]teis?",
    re.IGNORECASE
)
REGEX_DATA = re.compile(
    r"\b(\d{2}/\d{2}/\d{4})\b"
)


def _decode_str(s):
    if s is None:
        return ""
    parts = decode_header(s)
    decoded = []
    for part, enc in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def eh_juridico(assunto: str, remetente: str) -> bool:
    assunto_low = assunto.lower()
    remetente_low = remetente.lower()
    for termo in FILTROS_JURIDICOS["assuntos"]:
        if termo in assunto_low:
            return True
    for rem in FILTROS_JURIDICOS["remetentes"]:
        if rem in remetente_low:
            return True
    return False


def extrair_metadados(assunto: str, corpo: str) -> dict:
    """Extrai números de processo, prazos e datas do texto."""
    texto = f"{assunto} {corpo}"
    numeros = list(set(REGEX_NUMERO.findall(texto)))
    prazos = REGEX_PRAZO.findall(texto)
    datas = REGEX_DATA.findall(texto)
    return {
        "numeros_processo": numeros,
        "prazos_dias_uteis": [int(p) for p in prazos],
        "datas_mencionadas": datas[:5],
    }


def verificar_imap(conta_key: str, senha: str) -> list[dict]:
    """Varre conta IMAP (hotmail) e retorna e-mails jurídicos."""
    conta = CONTAS[conta_key]
    emails_juridicos = []

    try:
        mail = imaplib.IMAP4_SSL(conta["servidor"], conta["porta"])
        mail.login(conta["email"], senha)
        mail.select("INBOX")

        # Buscar últimos 30 dias
        desde = (date.today() - timedelta(days=30)).strftime("%d-%b-%Y")
        _, ids = mail.search(None, f'(SINCE "{desde}")')

        for num in ids[0].split()[-50:]:  # máx 50 e-mails
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            assunto = _decode_str(msg.get("Subject", ""))
            remetente = _decode_str(msg.get("From", ""))
            data_email = msg.get("Date", "")

            if not eh_juridico(assunto, remetente):
                continue

            # Extrair corpo
            corpo = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        corpo = part.get_payload(decode=True).decode("utf-8", errors="replace")
                        break
            else:
                corpo = msg.get_payload(decode=True).decode("utf-8", errors="replace")

            meta = extrair_metadados(assunto, corpo[:2000])
            emails_juridicos.append({
                "conta": conta["email"],
                "assunto": assunto,
                "remetente": remetente,
                "data": data_email,
                "corpo_resumo": corpo[:500],
                **meta,
            })

        mail.logout()
    except Exception as e:
        print(f"[ERRO IMAP {conta['email']}] {e}")

    print(f"[{conta['email']}] {len(emails_juridicos)} e-mail(s) jurídico(s) encontrado(s)")
    return emails_juridicos


def salvar_emails(emails: list[dict]) -> None:
    dados = {
        "extraido_em": datetime.now(timezone.utc).isoformat(),
        "total": len(emails),
        "emails": emails,
    }
    EMAILS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[SALVO] {EMAILS_JSON} — {len(emails)} e-mail(s)")


def _senha_do_env(key: str) -> str:
    """Lê senha do .env. Fallback: variável de ambiente do sistema."""
    import os
    env_file = BASE / ".env"
    if env_file.exists():
        for linha in env_file.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha.startswith("#") or "=" not in linha:
                continue
            nome, _, valor = linha.partition("=")
            os.environ.setdefault(nome.strip(), valor.strip())
    var_map = {
        "advogadobrito":   "HOTMAIL_ADVO_SENHA",
        "jeffersondebrito": "HOTMAIL_JEFF_SENHA",
    }
    return os.environ.get(var_map.get(key, ""), "")


def cmd_verificar():
    """Varre as contas hotmail via IMAP. Gmail via Claude MCP (nuvem)."""
    print("\n=== VARREDURA E-MAILS JURÍDICOS ===")
    print("Hotmail 1: advogadobrito@hotmail.com")
    print("Hotmail 2: jeffersondebrito@hotmail.com")
    print("Gmail: verificação feita pelo Claude na nuvem via MCP")
    print()

    todos = []
    for key in ["advogadobrito", "jeffersondebrito"]:
        senha = _senha_do_env(key)
        if not senha:
            print(f"[AVISO] Senha não encontrada no .env para {key} — pulando")
            continue
        emails = verificar_imap(key, senha)
        todos.extend(emails)

    if todos:
        salvar_emails(todos)
        print(f"\n✅ Total: {len(todos)} e-mail(s) jurídico(s) extraído(s)")
        for e in todos:
            print(f"  → [{e['conta']}] {e['assunto'][:60]}")
            if e["numeros_processo"]:
                print(f"    Processos: {', '.join(e['numeros_processo'])}")
    else:
        print("Nenhum e-mail jurídico encontrado nos últimos 30 dias.")


def cmd_exportar():
    """Exporta e-mails já salvos e sugere tarefas."""
    if not EMAILS_JSON.exists():
        print("[ERRO] emails_juridicos.json não encontrado. Execute 'verificar' primeiro.")
        return
    dados = json.loads(EMAILS_JSON.read_text(encoding="utf-8"))
    print(f"\n{len(dados['emails'])} e-mail(s) em {dados['extraido_em'][:10]}")
    for e in dados["emails"]:
        print(f"\n  📧 {e['assunto']}")
        print(f"     De: {e['remetente']}")
        if e["numeros_processo"]:
            print(f"     Processos: {', '.join(e['numeros_processo'])}")
        if e["prazos_dias_uteis"]:
            print(f"     Prazos: {e['prazos_dias_uteis']} dias úteis")


COMANDOS = {
    "verificar": cmd_verificar,
    "exportar":  cmd_exportar,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verificar"
    if cmd not in COMANDOS:
        print(f"Uso: {sys.argv[0]} verificar | exportar")
        sys.exit(1)
    COMANDOS[cmd]()
