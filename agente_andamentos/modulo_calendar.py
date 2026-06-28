"""
modulo_calendar.py — Sincronização de prazos com Google Calendar.
Requer token.json OAuth2 em BASE/config/token.json.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(r"C:/Users/advog/Meu Drive/X")
LOG_FILE = BASE / "antigravity_output.txt"
TOKEN_PATH = BASE / "config" / "token.json"
CREDENTIALS_PATH = BASE / "config" / "credentials.json"
PRAZOS_JSON = BASE / "documentos" / "prazos_pendentes.json"

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = "primary"

logging.basicConfig(
    filename=str(LOG_FILE), filemode="a",
    format="%(asctime)s [CALENDAR] %(levelname)s — %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("modulo_calendar")


def get_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())
    return build("calendar", "v3", credentials=creds)


def criar_evento(service, prazo: dict, processo: dict) -> str:
    # processo pode vir como dict aninhado (DataJud) ou vazio (email)
    if isinstance(processo, dict) and "numero" in processo:
        numero  = processo.get("numero", prazo.get("numero", ""))
        partes  = processo.get("partes", {})
        tribunal = processo.get("tribunal", "")
    else:
        numero  = prazo.get("numero", "")
        partes  = {}
        tribunal = prazo.get("tribunal", "")

    autor = partes.get("autor", "")
    reu   = partes.get("reu", "")
    partes_str = f"{autor} × {reu}" if (autor or reu) else numero

    titulo = f"⚖️ PRAZO — {numero} | {partes_str}"
    descricao = (
        f"Processo: {numero}\n"
        f"Tribunal: {tribunal}\n"
        f"Movimento: {prazo.get('tipo', prazo.get('tipo_movimento', prazo.get('movimento', '')))}\n"
        f"Vencimento: {prazo.get('vencimento','')}\n"
        f"Origem: {prazo.get('origem','DataJud')}"
    )
    evento = {
        "summary": titulo,
        "description": descricao,
        "start": {"date": prazo["vencimento"]},
        "end":   {"date": prazo["vencimento"]},
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 1440},
                {"method": "popup", "minutes": 120},
            ],
        },
        "colorId": "11",  # vermelho
    }
    resultado = service.events().insert(calendarId=CALENDAR_ID, body=evento).execute()
    log.info("Evento criado: %s → %s", numero, resultado.get("htmlLink"))
    return resultado.get("id", "")


def sincronizar_prazos() -> None:
    if not PRAZOS_JSON.exists():
        log.warning("prazos_pendentes.json não encontrado")
        return
    if not CREDENTIALS_PATH.exists():
        log.error("credentials.json ausente — autenticação Google necessária")
        print("[CALENDAR:ERROR] credentials.json não encontrado em", CREDENTIALS_PATH)
        return

    with open(PRAZOS_JSON, encoding="utf-8") as f:
        dados = json.load(f)

    prazos = [p for p in dados.get("prazos", []) if not p.get("calendar_id")]
    if not prazos:
        log.info("Nenhum prazo novo para sincronizar")
        return

    service = get_service()
    sincronizados = 0
    for prazo in prazos:
        try:
            cal_id = criar_evento(service, prazo, prazo.get("processo", {}))
            prazo["calendar_id"] = cal_id
            prazo["sincronizado_em"] = datetime.now(timezone.utc).isoformat()
            sincronizados += 1
        except Exception as e:
            log.exception("Erro ao criar evento: %s", e)

    dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    PRAZOS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[CALENDAR:DONE] {sincronizados} prazo(s) sincronizado(s) no Google Calendar.")


if __name__ == "__main__":
    sincronizar_prazos()
