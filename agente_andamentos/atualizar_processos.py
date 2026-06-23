"""
atualizar_processos.py — Pipeline principal do agente de andamentos.
Executa em sequência:
  1. Busca andamentos no DataJud
  2. Calcula prazos
  3. Enriquece com partes
  4. Sincroniza Google Calendar
  5. Registra status em antigravity_output.txt
"""

import json
import logging
import time
import requests
from datetime import date, datetime, timezone
from pathlib import Path

from modulo_prazos import calcular_prazo, salvar_prazos
from modulo_partes_datajud import enriquecer_processos

BASE = Path(r"C:/Users/advog/Meu Drive/X")
PROCESSOS_JSON  = BASE / "documentos" / "processos.json"
PRAZOS_JSON     = BASE / "documentos" / "prazos_pendentes.json"
LOG_FILE        = BASE / "antigravity_output.txt"

DATAJUD_KEY = "ApiKey cDZHYzlZa0JadVREZDJCendFbXNwWnA6MusICgs4R14wMWI1ZUp1ZmQ5djVncw=="
DATAJUD_URL = "https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search"

TRIBUNAL_MAP = {
    "TJRO": "tjro", "TJAM": "tjam", "TJMT": "tjmt",
    "TJPA": "tjpa", "STJ": "stj",  "STF": "stf",
    "TRF1": "trf1", "TRF3": "trf3",
}

logging.basicConfig(
    filename=str(LOG_FILE), filemode="a",
    format="%(asctime)s [ATUALIZAR] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.INFO,
)
log = logging.getLogger("atualizar_processos")


def buscar_andamentos(numero: str, tribunal: str) -> list[dict]:
    sigla = TRIBUNAL_MAP.get(tribunal.upper(), "")
    if not sigla:
        return []
    headers = {"Authorization": DATAJUD_KEY, "Content-Type": "application/json"}
    payload = {
        "query": {"match": {"numeroProcesso": numero}},
        "sort": [{"dataHora": {"order": "desc"}}],
        "size": 1,
    }
    for tentativa in range(1, 4):
        try:
            r = requests.post(
                DATAJUD_URL.format(tribunal=sigla),
                headers=headers, json=payload, timeout=15
            )
            r.raise_for_status()
            hits = r.json().get("hits", {}).get("hits", [])
            if hits:
                return hits[0]["_source"].get("movimentos", [])
        except Exception as e:
            log.warning("Tentativa %d — %s: %s", tentativa, numero, e)
            time.sleep(2 ** tentativa)
    return []


def processar() -> None:
    log.info("=== INÍCIO — atualizar_processos.py ===")

    if not PROCESSOS_JSON.exists():
        log.error("processos.json não encontrado")
        return

    with open(PROCESSOS_JSON, encoding="utf-8") as f:
        dados = json.load(f)

    total = len(dados.get("processos", []))
    atualizados = 0
    novos_prazos = []
    novas_movimentacoes = 0

    for proc in dados["processos"]:
        numero   = proc["numero"]
        tribunal = proc.get("tribunal", "")
        andamentos_anteriores = {a["data"] for a in proc.get("andamentos", [])}

        movimentos = buscar_andamentos(numero, tribunal)
        for mov in movimentos[:3]:  # últimos 3
            data_str  = mov.get("dataHora", "")[:10]
            descricao = mov.get("nome", mov.get("movimento", {}).get("nome", ""))

            if data_str not in andamentos_anteriores:
                novas_movimentacoes += 1
                proc.setdefault("andamentos", []).insert(0, {
                    "data": data_str,
                    "movimento": descricao,
                })
                proc["andamentos"] = proc["andamentos"][:3]  # mantém só últimos 3

                # Calcula prazo se movimento conhecido
                try:
                    data_mov = date.fromisoformat(data_str)
                    prazo = calcular_prazo(data_mov, descricao)
                    prazo["numero"] = numero
                    prazo["tribunal"] = tribunal
                    prazo["processo"] = proc
                    novos_prazos.append(prazo)
                    log.info("Prazo calculado: %s → %s", numero, prazo["vencimento"])
                except Exception as e:
                    log.warning("Sem prazo para %s: %s", numero, e)

        atualizados += 1
        log.info("Processado: %s (%d movimentos novos)", numero, novas_movimentacoes)

    dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    PROCESSOS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    if novos_prazos:
        prazos_existentes = []
        if PRAZOS_JSON.exists():
            prazos_existentes = json.loads(PRAZOS_JSON.read_text(encoding="utf-8")).get("prazos", [])
        salvar_prazos(prazos_existentes + novos_prazos)

    # Enriquece com partes do DataJud
    enriquecer_processos()

    # Tenta sincronizar Calendar
    try:
        from modulo_calendar import sincronizar_prazos
        sincronizar_prazos()
    except Exception as e:
        log.warning("Google Calendar não sincronizado: %s", e)

    resumo = (
        f"\n---\nTimestamp: {datetime.now(timezone.utc).isoformat()}\n"
        f"Origem: Antigravity_Local\nOperação: atualizar_processos.py\n---\n"
        f"Processos atualizados: {atualizados}/{total}\n"
        f"Novas movimentações: {novas_movimentacoes}\n"
        f"Novos prazos calculados: {len(novos_prazos)}\n"
        f"[ATUALIZAR:DONE]\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(resumo)
    print(resumo)


if __name__ == "__main__":
    processar()
