"""
modulo_mabios_email.py — Processador autônomo de rascunhos MABIOS
De Brito Advocacia | OAB/RO 2952

Roda localmente no Antigravity. Lê rascunhos MABIOS_ACTION: diretamente
do Gmail via OAuth (token.json) — sem depender de sessão com Claude.

Protocolo MABIOS Email:
  Assunto: MABIOS_ACTION:TIPO:NUMERO_PROCESSO
  Corpo:   observação livre (opcional)

  Tipos:
    CONFERIDO  → processo some dos relatórios ativos
    ARQUIVAR   → processo arquivado definitivamente
    ATIVO      → reativa processo
    URGENTE    → eleva prioridade de tarefas do processo
    NOTA       → adiciona nota ao processo
    CONCLUIR   → conclui tarefa (NUMERO = T-001, T-002...)

Como usar:
  python modulo_mabios_email.py gmail     → lê Gmail e processa rascunhos (MODO PRINCIPAL)
  python modulo_mabios_email.py processar → lê claude_output.txt (fallback)
  python modulo_mabios_email.py listar    → mostra processos por status
  python modulo_mabios_email.py status    → contagem por status

Loop automático (chamado pelo loop_monitor.py a cada 15 min):
  python modulo_mabios_email.py gmail
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, date, timezone

BASE           = Path(r"C:/Users/advog/Meu Drive/X")
PROCESSOS_JSON = BASE / "documentos" / "processos.json"
TAREFAS_JSON   = BASE / "documentos" / "tarefas.json"
CANAL_IN       = BASE / "claude_output.txt"
CANAL_OUT      = BASE / "antigravity_output.txt"
TOKEN_PATH     = BASE / "config" / "token.json"
CREDS_PATH     = BASE / "config" / "credentials.json"
LOG_MABIOS     = BASE / "logs" / "mabios_processados.json"

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]

LABEL_PROCESSADO = "MABIOS_PROCESSADO"


# ─── Auth Gmail ───────────────────────────────────────────────────────────────

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
            # Primeira vez com escopo Gmail: abre browser para autorizar
            from google_auth_oauthlib.flow import InstalledAppFlow
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
            TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

    return build("gmail", "v1", credentials=creds)


def _garantir_label(service) -> str | None:
    """Cria label MABIOS_PROCESSADO se não existir. Retorna o ID."""
    try:
        labels = service.users().labels().list(userId="me").execute().get("labels", [])
        for lb in labels:
            if lb["name"] == LABEL_PROCESSADO:
                return lb["id"]
        novo = service.users().labels().create(
            userId="me",
            body={"name": LABEL_PROCESSADO, "labelListVisibility": "labelShow",
                  "messageListVisibility": "show"}
        ).execute()
        return novo["id"]
    except Exception:
        return None


# ─── Carregar / Salvar dados ──────────────────────────────────────────────────

def _load(path: Path) -> dict:
    if not path.exists():
        return {"processos": [], "tarefas": [], "atualizado_em": _stamp()}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, dados: dict) -> None:
    dados["atualizado_em"] = _stamp()
    path.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_mabios(acoes: list[dict]) -> None:
    """Registra histórico de ações processadas."""
    LOG_MABIOS.parent.mkdir(parents=True, exist_ok=True)
    historico = []
    if LOG_MABIOS.exists():
        historico = json.loads(LOG_MABIOS.read_text(encoding="utf-8"))
    historico.extend(acoes)
    LOG_MABIOS.write_text(json.dumps(historico, ensure_ascii=False, indent=2), encoding="utf-8")


def _log_out(msg: str) -> None:
    with open(CANAL_OUT, "a", encoding="utf-8") as f:
        f.write(f"\n[{_stamp()}] [MABIOS] {msg}\n")


# ─── Parser ───────────────────────────────────────────────────────────────────

REGEX_MABIOS = re.compile(r"MABIOS_ACTION:([A-Z_]+):([^\s\|<\r\n]+)", re.IGNORECASE)


def _parse_assunto(assunto: str) -> dict | None:
    m = REGEX_MABIOS.search(assunto)
    if not m:
        return None
    return {"tipo": m.group(1).upper(), "numero": m.group(2).strip()}


def _extrair_nota(body: str) -> str:
    """Extrai instrução livre do corpo do rascunho."""
    if not body:
        return ""
    # Ignora linhas do template Outlook
    ignorar = ["clique em enviar", "obter o outlook", "digite sua instrucao",
                "escreva na linha abaixo", "aka.ms"]
    linhas = []
    for linha in body.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if any(ig in linha.lower() for ig in ignorar):
            continue
        linhas.append(linha)
    return " ".join(linhas)[:300]


# ─── Aplicar ação ─────────────────────────────────────────────────────────────

def _aplicar(acao: dict, dados_proc: dict, dados_tar: dict) -> str:
    tipo   = acao["tipo"]
    numero = acao["numero"]
    nota   = acao.get("nota", "")
    hoje   = date.today().isoformat()

    # Tarefas (CONCLUIR T-XXX)
    if tipo == "CONCLUIR" and numero.upper().startswith("T-"):
        for t in dados_tar.get("tarefas", []):
            if t["id"].upper() == numero.upper():
                t["status"] = "CONCLUIDA"
                t["concluida_em"] = hoje
                return f"✅ Tarefa {numero} → CONCLUÍDA"
        return f"⚠️  Tarefa {numero} não encontrada"

    # Processos
    processos = dados_proc.setdefault("processos", [])
    proc = next((p for p in processos if p["numero"] == numero), None)

    if proc is None:
        proc = {
            "numero": numero, "status": "ATIVO",
            "tribunal": "TJRO", "comarca": "Porto Velho",
            "vara": "", "classe": "",
            "partes": {"advogado_reu": "Dr. Jefferson De Brito — OAB/RO 2952"},
            "andamentos": [],
            "origem_mabios": f"criado via MABIOS — {hoje}"
        }
        processos.append(proc)

    def add_nota(texto):
        notas = proc.setdefault("notas", [])
        if isinstance(notas, str):
            proc["notas"] = [notas] if notas else []
        proc["notas"].append(f"{hoje}: {texto}")

    if tipo == "CONFERIDO":
        proc["status"] = "CONFERIDO"
        proc["conferido_em"] = hoje
        if nota:
            add_nota(nota)
        # Concluir tarefas abertas do processo automaticamente
        for t in dados_tar.get("tarefas", []):
            if t.get("processo") == numero and t.get("status") == "ABERTA":
                t["status"] = "CONCLUIDA"
                t["concluida_em"] = hoje
        return f"✅ {numero} → CONFERIDO"

    elif tipo == "ARQUIVAR":
        proc["status"] = "ARQUIVADO"
        proc["arquivado_em"] = hoje
        if nota:
            proc["motivo_arquivamento"] = nota
        return f"📁 {numero} → ARQUIVADO"

    elif tipo == "ATIVO":
        proc["status"] = "ATIVO"
        proc.pop("conferido_em", None)
        proc.pop("arquivado_em", None)
        return f"🔄 {numero} → ATIVO"

    elif tipo == "URGENTE":
        count = 0
        for t in dados_tar.get("tarefas", []):
            if t.get("processo") == numero and t.get("status") not in ("CONCLUIDA", "CANCELADA"):
                t["prioridade"] = "URGENTE"
                count += 1
        return f"🔴 {numero} → {count} tarefa(s) URGENTE"

    elif tipo in ("NOTA", "OUTRO"):
        if nota:
            add_nota(nota)
            return f"📝 {numero} → nota: {nota[:60]}"
        return f"⚠️  {tipo} sem nota para {numero}"

    else:
        return f"❓ Tipo '{tipo}' desconhecido para {numero}"


# ─── Modo principal: ler Gmail diretamente ────────────────────────────────────

def cmd_gmail():
    """Lê rascunhos MABIOS_ACTION: do Gmail e processa localmente."""
    print("\n=== MABIOS — Lendo rascunhos do Gmail ===")

    try:
        service = _gmail_service()
    except Exception as e:
        print(f"[ERRO] Autenticação Gmail falhou: {e}")
        _log_out(f"[ERRO AUTH] {e}")
        return

    label_id = _garantir_label(service)

    # Buscar rascunhos com assunto MABIOS_ACTION
    try:
        resp = service.users().drafts().list(
            userId="me",
            q="subject:MABIOS_ACTION"
        ).execute()
        drafts = resp.get("drafts", [])
    except Exception as e:
        print(f"[ERRO] Falha ao listar rascunhos: {e}")
        _log_out(f"[ERRO LIST] {e}")
        return

    if not drafts:
        print("Nenhum rascunho MABIOS encontrado.")
        return

    print(f"Encontrado(s): {len(drafts)} rascunho(s)\n")

    dados_proc = _load(PROCESSOS_JSON)
    dados_tar  = _load(TAREFAS_JSON)
    resultados = []
    ids_processados = []

    for draft_ref in drafts:
        try:
            draft = service.users().drafts().get(
                userId="me", id=draft_ref["id"], format="full"
            ).execute()
            msg = draft.get("message", {})
            headers = {h["name"].lower(): h["value"]
                       for h in msg.get("payload", {}).get("headers", [])}
            assunto = headers.get("subject", "")

            acao = _parse_assunto(assunto)
            if not acao:
                continue

            # Extrair nota do corpo
            body_raw = ""
            payload = msg.get("payload", {})
            if payload.get("body", {}).get("data"):
                import base64
                body_raw = base64.urlsafe_b64decode(
                    payload["body"]["data"] + "=="
                ).decode("utf-8", errors="replace")
            elif payload.get("parts"):
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        import base64
                        body_raw = base64.urlsafe_b64decode(
                            part["body"]["data"] + "=="
                        ).decode("utf-8", errors="replace")
                        break

            acao["nota"] = _extrair_nota(body_raw)

            resultado = _aplicar(acao, dados_proc, dados_tar)
            print(f"  {resultado}")
            resultados.append(resultado)
            ids_processados.append(draft_ref["id"])

            # Registrar no log histórico
            _log_mabios([{
                "draft_id": draft_ref["id"],
                "assunto": assunto,
                "acao": acao,
                "resultado": resultado,
                "processado_em": _stamp(),
            }])

            # Mover rascunho para lixeira (processado)
            try:
                service.users().drafts().delete(userId="me", id=draft_ref["id"]).execute()
            except Exception:
                # Se não conseguir deletar, só loga
                pass

        except Exception as e:
            print(f"  [ERRO] rascunho {draft_ref['id']}: {e}")

    if ids_processados:
        _save(PROCESSOS_JSON, dados_proc)
        _save(TAREFAS_JSON, dados_tar)

    relatorio = (
        f"MABIOS:GMAIL | {_stamp()} | "
        f"{len(ids_processados)}/{len(drafts)} processado(s)\n"
        + "\n".join(f"  {r}" for r in resultados)
    )
    _log_out(relatorio)

    print(f"\n✅ {len(ids_processados)} ação(ões) aplicada(s) | processos.json e tarefas.json atualizados")


# ─── Modo fallback: ler claude_output.txt ─────────────────────────────────────

def cmd_processar():
    """Fallback: lê ações MABIOS do claude_output.txt."""
    if not CANAL_IN.exists():
        print("[ERRO] claude_output.txt não encontrado")
        return
    texto = CANAL_IN.read_text(encoding="utf-8")
    acoes = [{"tipo": m.group(1).upper(), "numero": m.group(2).strip(), "nota": ""}
             for m in REGEX_MABIOS.finditer(texto)]
    if not acoes:
        print("Nenhuma ação MABIOS em claude_output.txt")
        return

    dados_proc = _load(PROCESSOS_JSON)
    dados_tar  = _load(TAREFAS_JSON)
    resultados = []

    print(f"\n=== MABIOS — {len(acoes)} ação(ões) do canal ===\n")
    for acao in acoes:
        r = _aplicar(acao, dados_proc, dados_tar)
        print(f"  {r}")
        resultados.append(r)

    _save(PROCESSOS_JSON, dados_proc)
    _save(TAREFAS_JSON, dados_tar)
    _log_out("MABIOS:CANAL | " + " | ".join(resultados))
    print(f"\n✅ Salvo.")


# ─── Status / Listar ──────────────────────────────────────────────────────────

def cmd_listar():
    dados = _load(PROCESSOS_JSON)
    por_status: dict[str, list] = {}
    for p in dados.get("processos", []):
        s = p.get("status", "ATIVO")
        por_status.setdefault(s, []).append(p)

    print(f"\n{'='*55}")
    print(f"  PROCESSOS POR STATUS — {date.today().strftime('%d/%m/%Y')}")
    print(f"{'='*55}")
    for status, procs in sorted(por_status.items()):
        icon = {"ATIVO": "🟢", "CONFERIDO": "✅", "ARQUIVADO": "📁"}.get(status, "•")
        print(f"\n  {icon} {status} ({len(procs)})")
        for p in procs:
            print(f"     {p['numero']} — {p.get('comarca','')} {p.get('classe','')}")
    print(f"\n{'='*55}\n")


def cmd_status():
    dados = _load(PROCESSOS_JSON)
    total = len(dados.get("processos", []))
    por_status: dict[str, int] = {}
    for p in dados.get("processos", []):
        s = p.get("status", "ATIVO")
        por_status[s] = por_status.get(s, 0) + 1
    print(f"\nTotal: {total} processo(s)")
    for s, n in sorted(por_status.items()):
        print(f"  {s}: {n}")
    print()


# ─── Dispatch ─────────────────────────────────────────────────────────────────

COMANDOS = {
    "gmail":     cmd_gmail,
    "processar": cmd_processar,
    "listar":    cmd_listar,
    "status":    cmd_status,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "gmail"
    if cmd not in COMANDOS:
        print(f"Uso: {sys.argv[0]} gmail | processar | listar | status")
        sys.exit(1)
    COMANDOS[cmd]()
