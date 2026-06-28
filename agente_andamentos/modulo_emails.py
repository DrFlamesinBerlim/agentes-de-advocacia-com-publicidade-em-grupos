"""
modulo_emails.py — Extração de tarefas jurídicas de 4 contas de e-mail
De Brito Advocacia | OAB/RO 2952

CANAIS MONITORADOS:
  1. advogadobrito@hotmail.com    → principal escritório (DJE, PJe, intimações)
  2. jeffersondebrito@hotmail.com → pessoal Dr. Jefferson
  3. tribuna.livre.ro@gmail.com   → Gmail OAuth (caixa de entrada jurídica)
  4. flamesinberlim@gmail.com     → Gmail OAuth (backup)

ARQUITETURA:
  - Hotmail (1 e 2): Antigravity acessa via IMAP local (python-imaplib)
  - Gmail (3 e 4):   Antigravity acessa via OAuth (token.json) — autônomo

Como usar (Antigravity):
  python modulo_emails.py verificar   → varre todos os 4 e-mails + Gmail inbox
  python modulo_emails.py gmail       → só Gmail (caixa de entrada via OAuth)
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
EMAILS_JSON    = BASE / "documentos" / "emails_juridicos.json"
TAREFAS_JSON   = BASE / "documentos" / "tarefas.json"
PROCESSOS_JSON = BASE / "documentos" / "processos.json"
PRAZOS_JSON    = BASE / "documentos" / "prazos_pendentes.json"
TOKEN_PATH     = BASE / "config" / "token.json"
CREDS_PATH     = BASE / "config" / "credentials.json"

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]
LABEL_JURIDICO = "JURIDICO_PROCESSADO"

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
        "pjepush@tjro",
        "dje@tjro",
        "tjro.jus.br",
        "tjam.jus.br",
        "stj.jus.br",
        "stf.jus.br",
        "cnj.jus.br",
        "trf1.jus.br",
        "trf2.jus.br",
        "trf3.jus.br",
        "trf4.jus.br",
        "jfro.jus.br",
        "projudi",
        "datajud",
        "intimacao",
        "notificacao",
        "2turmarecursal@tjro",
        "naoresponda.pje",
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
            entry = {
                "conta": conta["email"],
                "assunto": assunto,
                "remetente": remetente,
                "data": data_email,
                "corpo_resumo": corpo[:500],
                **meta,
            }
            emails_juridicos.append(entry)

            if meta["numeros_processo"]:
                _registrar_andamento(entry)
                _criar_tarefa_de_email(entry)

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


def _gmail_service():
    """Retorna serviço Gmail autenticado via token.json existente."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), GMAIL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
        else:
            raise RuntimeError("token.json inválido ou ausente — execute OAuth uma vez manualmente")
    return build("gmail", "v1", credentials=creds)


def _gmail_label_id(service, nome: str) -> str:
    """Retorna ID do label criando-o se necessário."""
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for lb in labels:
        if lb["name"] == nome:
            return lb["id"]
    novo = service.users().labels().create(userId="me", body={"name": nome}).execute()
    return novo["id"]


def _gmail_body(service, msg_id: str) -> str:
    """Extrai texto plano da mensagem Gmail (máx 2000 chars)."""
    import base64
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    payload = msg.get("payload", {})

    def extrair(p):
        if p.get("mimeType") == "text/plain":
            data = p.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        for part in p.get("parts", []):
            r = extrair(part)
            if r:
                return r
        return ""

    return extrair(payload)[:2000]


def _registrar_andamento(email_info: dict) -> int:
    """Registra andamento em processos.json e prazo em prazos_pendentes.json.

    Retorna o número de processos atualizados.
    """
    numeros = email_info.get("numeros_processo", [])
    if not numeros:
        return 0

    if not PROCESSOS_JSON.exists():
        return 0

    dados = json.loads(PROCESSOS_JSON.read_text(encoding="utf-8"))
    processos = dados.get("processos", [])
    idx = {p["numero"]: p for p in processos}

    assunto   = email_info.get("assunto", "")
    remetente = email_info.get("remetente", "")
    # normaliza data para ISO — aceita RFC2822 e ISO 8601
    try:
        from email.utils import parsedate_to_datetime
        data_iso = parsedate_to_datetime(email_info.get("data", "")).date().isoformat()
    except Exception:
        raw = email_info.get("data", "")
        data_iso = raw[:10] if len(raw) >= 10 and raw[4] == "-" else date.today().isoformat()

    novos_prazos = []
    atualizados  = 0

    for numero in numeros:
        proc = idx.get(numero)
        if proc is None:
            # cria entrada mínima para o processo desconhecido
            proc = {
                "numero": numero,
                "status": "ATIVO",
                "tribunal": "",
                "comarca": "",
                "vara": "",
                "partes": {"advogado_reu": "Dr. Jefferson De Brito — OAB/RO 2952"},
                "andamentos": [],
            }
            processos.append(proc)
            idx[numero] = proc

        # Evita duplicata de andamento (mesma data + mesmo trecho de movimento)
        andamentos_existentes = {
            (a.get("data", ""), a.get("movimento", "")[:40])
            for a in proc.get("andamentos", [])
        }
        chave = (data_iso, assunto[:40])
        if chave in andamentos_existentes:
            continue

        # Calcula prazo
        prazo_info = {}
        try:
            from modulo_prazos import calcular_prazo
            prazo_info = calcular_prazo(date.fromisoformat(data_iso), assunto)
        except Exception:
            pass

        andamento = {
            "data": data_iso,
            "movimento": assunto[:120],
            "origem": f"email:{remetente[:60]}",
        }
        if prazo_info.get("vencimento"):
            andamento["prazo_calculado"] = prazo_info["vencimento"]
            andamento["prazo_tipo"]      = prazo_info.get("tipo", "")
            andamento["prazo_status"]    = prazo_info.get("status", "PENDENTE")
            novos_prazos.append({
                "numero":     numero,
                "vencimento": prazo_info["vencimento"],
                "tipo":       prazo_info.get("tipo", ""),
                "movimento":  assunto[:80],
                "origem":     "email",
            })

        proc.setdefault("andamentos", []).insert(0, andamento)
        proc["andamentos"] = proc["andamentos"][:5]  # mantém últimos 5
        atualizados += 1

    if atualizados:
        dados["processos"] = processos
        dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
        PROCESSOS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    if novos_prazos:
        prazos_existentes = []
        if PRAZOS_JSON.exists():
            prazos_existentes = json.loads(PRAZOS_JSON.read_text(encoding="utf-8")).get("prazos", [])
        numeros_existentes = {(p["numero"], p["vencimento"]) for p in prazos_existentes}
        novos = [p for p in novos_prazos if (p["numero"], p["vencimento"]) not in numeros_existentes]
        if novos:
            prazos_existentes.extend(novos)
            PRAZOS_JSON.write_text(
                json.dumps({"prazos": prazos_existentes}, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

    return atualizados


def _criar_tarefa_de_email(email_info: dict) -> None:
    """Cria tarefa em tarefas.json se encontrou número de processo e prazo."""
    numeros = email_info.get("numeros_processo", [])
    prazos  = email_info.get("prazos_dias_uteis", [])
    if not numeros or not prazos:
        return

    dados = {"tarefas": []}
    if TAREFAS_JSON.exists():
        dados = json.loads(TAREFAS_JSON.read_text(encoding="utf-8"))

    tarefas = dados.get("tarefas", [])
    ids_existentes = {t.get("id") for t in tarefas}

    for numero in numeros:
        # ID baseado em assunto truncado + número — evita duplicatas
        tid = f"E-{numero[-7:]}-{date.today().isoformat()}"
        if tid in ids_existentes:
            continue

        vencimento = ""
        if prazos:
            from modulo_prazos import calcular_prazo
            try:
                res = calcular_prazo(date.today(), email_info.get("assunto", ""))
                vencimento = res.get("vencimento", "")
            except Exception:
                pass

        tarefas.append({
            "id": tid,
            "titulo": email_info.get("assunto", "")[:80],
            "processo": numero,
            "status": "PENDENTE",
            "prioridade": "NORMAL",
            "vencimento": vencimento,
            "origem": "email",
            "conta": email_info.get("conta", ""),
        })

    dados["tarefas"] = tarefas
    TAREFAS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def verificar_gmail_inbox() -> list[dict]:
    """Varre caixa de entrada do Gmail por e-mails jurídicos não processados."""
    try:
        service = _gmail_service()
    except Exception as e:
        print(f"[GMAIL INBOX] OAuth indisponível: {e}")
        return []

    label_id = _gmail_label_id(service, LABEL_JURIDICO)

    # Busca emails dos últimos 60 dias que NÃO tenham o label processado
    # Sem is:unread — emails lidos mas não processados também devem ser capturados
    query = f"in:inbox newer_than:60d -label:{LABEL_JURIDICO}"
    resp = service.users().messages().list(userId="me", q=query, maxResults=50).execute()
    msgs = resp.get("messages", [])

    emails_juridicos = []
    for m in msgs:
        msg = service.users().messages().get(
            userId="me", id=m["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        assunto   = headers.get("Subject", "")
        remetente = headers.get("From", "")
        data_str  = headers.get("Date", "")

        if not eh_juridico(assunto, remetente):
            continue

        corpo = _gmail_body(service, m["id"])
        meta  = extrair_metadados(assunto, corpo)

        entry = {
            "conta": "gmail/flamesinberlim",
            "assunto": assunto,
            "remetente": remetente,
            "data": data_str,
            "corpo_resumo": corpo[:500],
            **meta,
        }
        emails_juridicos.append(entry)

        # Registra andamento em processos.json + prazo em prazos_pendentes.json
        if meta["numeros_processo"]:
            _registrar_andamento(entry)
            _criar_tarefa_de_email(entry)

        # Marca com label para não reprocessar
        service.users().messages().modify(
            userId="me", id=m["id"],
            body={"addLabelIds": [label_id]}
        ).execute()

    print(f"[Gmail Inbox] {len(emails_juridicos)} e-mail(s) jurídico(s) encontrado(s)")
    return emails_juridicos


def cmd_verificar():
    """Varre Hotmail via IMAP e Gmail inbox via OAuth."""
    print("\n=== VARREDURA E-MAILS JURÍDICOS ===")

    todos = []

    # Hotmail IMAP
    for key in ["advogadobrito", "jeffersondebrito"]:
        senha = _senha_do_env(key)
        if not senha:
            print(f"[AVISO] Senha não encontrada no .env para {key} — pulando")
            continue
        emails = verificar_imap(key, senha)
        todos.extend(emails)

    # Gmail OAuth (inbox)
    gmail_emails = verificar_gmail_inbox()
    todos.extend(gmail_emails)

    if todos:
        salvar_emails(todos)
        print(f"\n✅ Total: {len(todos)} e-mail(s) jurídico(s) extraído(s)")
        for e in todos:
            print(f"  → [{e['conta']}] {e['assunto'][:60]}")
            if e["numeros_processo"]:
                print(f"    Processos: {', '.join(e['numeros_processo'])}")
    else:
        print("Nenhum e-mail jurídico encontrado nos últimos 30 dias.")


def cmd_gmail():
    """Só Gmail inbox via OAuth (sem IMAP)."""
    print("\n=== GMAIL INBOX — E-MAILS JURÍDICOS ===")
    emails = verificar_gmail_inbox()
    if emails:
        salvar_emails(emails)
    else:
        print("Nenhum e-mail jurídico novo na caixa de entrada.")


def cmd_andamentos():
    """Varre Gmail inbox, registra andamentos em processos.json e prazos."""
    print("\n=== ANDAMENTOS VIA EMAIL ===")
    emails = verificar_gmail_inbox()
    if not emails:
        print("Nenhum e-mail jurídico novo.")
        return
    total_proc = sum(len(e.get("numeros_processo", [])) for e in emails)
    print(f"\n✅ {len(emails)} e-mail(s) processado(s) → {total_proc} andamento(s) registrado(s)")
    for e in emails:
        if e.get("numeros_processo"):
            print(f"  → {e['assunto'][:60]}")
            for n in e["numeros_processo"]:
                print(f"     Processo: {n}")
            if e.get("prazos_dias_uteis"):
                print(f"     Prazo: {e['prazos_dias_uteis']} dias úteis")


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
    "verificar":   cmd_verificar,
    "gmail":       cmd_gmail,
    "andamentos":  cmd_andamentos,
    "exportar":    cmd_exportar,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verificar"
    if cmd not in COMANDOS:
        print(f"Uso: {sys.argv[0]} verificar | gmail | andamentos | exportar")
        sys.exit(1)
    COMANDOS[cmd]()
