"""
Módulo: modulo_partes_datajud.py
Consulta o DataJud CNJ e enriquece processos.json com nomes das partes.
Executado pelo Antigravity via <commands> ou diretamente pelo loop_monitor.py.
"""

import json
import logging
import time
from pathlib import Path

import requests

BASE = Path(r"C:/Users/advog/Meu Drive/X")
PROCESSOS_JSON = BASE / "documentos" / "processos.json"
LOG_FILE = BASE / "antigravity_output.txt"

DATAJUD_KEY = "ApiKey cDZHYzlZa0JadVREZDJCendFbXNwWnA6MusICgs4R14wMWI1ZUp1ZmQ5djVncw=="
DATAJUD_URL = "https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search"

TRIBUNAL_MAP = {
    "TJRO": "tjro",
    "TJAM": "tjam",
    "TJMT": "tjmt",
    "TJPA": "tjpa",
    "STJ":  "stj",
    "STF":  "stf",
    "TRF1": "trf1",
    "TRF3": "trf3",
}

logging.basicConfig(
    filename=str(LOG_FILE),
    filemode="a",
    format="%(asctime)s [PARTES_DATAJUD] %(levelname)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
    level=logging.INFO,
)
log = logging.getLogger("modulo_partes_datajud")


def consultar_partes(numero: str, tribunal: str) -> list[dict]:
    """Consulta o DataJud e retorna lista de partes do processo."""
    sigla = TRIBUNAL_MAP.get(tribunal.upper())
    if not sigla:
        log.warning("Tribunal não mapeado: %s", tribunal)
        return []

    url = DATAJUD_URL.format(tribunal=sigla)
    headers = {
        "Authorization": DATAJUD_KEY,
        "Content-Type": "application/json",
    }
    payload = {"query": {"match": {"numeroProcesso": numero}}}

    for tentativa in range(1, 4):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=15)
            r.raise_for_status()
            hits = r.json().get("hits", {}).get("hits", [])
            if not hits:
                log.warning("Nenhum resultado no DataJud para %s", numero)
                return []
            src = hits[0]["_source"]
            partes = []
            for p in src.get("partes", []):
                partes.append({
                    "tipoParte": p.get("tipoParte", ""),
                    "nome": p.get("nome", ""),
                    "documento": p.get("documento", ""),
                    "advogados": [
                        {"nome": a.get("nome", ""), "oab": a.get("numeroOAB", "")}
                        for a in p.get("advogados", [])
                    ],
                })
            log.info("Partes obtidas para %s: %d parte(s)", numero, len(partes))
            return partes
        except requests.RequestException as e:
            log.warning("Tentativa %d falhou para %s: %s", tentativa, numero, e)
            time.sleep(2 ** tentativa)

    log.error("Falha definitiva ao consultar %s", numero)
    return []


def enriquecer_processos() -> None:
    """Lê processos.json, consulta DataJud para cada processo sem partes e salva."""
    if not PROCESSOS_JSON.exists():
        log.error("processos.json não encontrado em %s", PROCESSOS_JSON)
        return

    with open(PROCESSOS_JSON, encoding="utf-8") as f:
        dados = json.load(f)

    atualizados = 0
    for proc in dados.get("processos", []):
        partes_atuais = proc.get("partes_datajud", [])
        # Só consulta se ainda não tiver partes preenchidas
        if partes_atuais:
            log.info("SKIP — partes já existem para %s", proc["numero"])
            continue

        partes = consultar_partes(proc["numero"], proc.get("tribunal", ""))
        if partes:
            proc["partes_datajud"] = partes
            # Preenche campos legados de forma amigável
            autores = [p["nome"] for p in partes if "ativo" in p["tipoParte"].lower()
                       or "autor" in p["tipoParte"].lower()
                       or "requerente" in p["tipoParte"].lower()
                       or "exequente" in p["tipoParte"].lower()]
            reus = [p["nome"] for p in partes if "passivo" in p["tipoParte"].lower()
                    or "réu" in p["tipoParte"].lower()
                    or "requerido" in p["tipoParte"].lower()
                    or "executado" in p["tipoParte"].lower()]
            proc.setdefault("partes", {})
            proc["partes"]["autor"] = " / ".join(autores) if autores else proc["partes"].get("autor", "")
            proc["partes"]["reu"] = " / ".join(reus) if reus else proc["partes"].get("reu", "")
            atualizados += 1

    from datetime import datetime, timezone
    dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()

    with open(PROCESSOS_JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    log.info("processos.json atualizado — %d processo(s) enriquecido(s)", atualizados)
    print(f"[PARTES:DONE] {atualizados} processo(s) atualizado(s) com partes do DataJud.")


if __name__ == "__main__":
    enriquecer_processos()
