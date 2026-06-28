"""
modulo_partes_web.py — Busca de partes via fontes web (cloud-safe).

Fontes em ordem de prioridade:
  1. E-mails de relatório no Gmail (MABIOS v3 / DE BRITO ADV)
  2. DataJud CNJ API pública (já disponível, cloud-safe)
  3. Escavador API por OAB (requer ESCAVADOR_API_KEY no .env)
  4. Google / JusBrasil via WebSearch (fallback)

Uso:
  python modulo_partes_web.py          → busca todos sem partes
  python modulo_partes_web.py NUMERO   → busca processo específico
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from datetime import datetime, timezone

import requests

BASE = Path(r"C:/Users/advog/Meu Drive/X")
PROCESSOS_JSON = BASE / "documentos" / "processos.json"
LOG_FILE = BASE / "antigravity_output.txt"
ENV_FILE = BASE / "config" / ".env"

OAB_NUMERO = "2952"
OAB_ESTADO = "RO"

DATAJUD_KEY = "ApiKey cDZHYzlZa0JadVREZDJCendFbXNwWnA6MusICgs4R14wMWI1ZUp1ZmQ5djVncw=="
DATAJUD_URL = "https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search"

TRIBUNAL_MAP = {
    "TJRO": "tjro", "TJAM": "tjam", "TJMT": "tjmt", "TJPA": "tjpa",
    "TJMS": "tjms", "TJSC": "tjsc", "TJPR": "tjpr", "TJAC": "tjac",
    "TJAP": "tjap", "TJMA": "tjma", "TJTO": "tjto", "TJRR": "tjrr",
    "STJ": "stj", "STF": "stf",
    "TRF1": "trf1", "TRF2": "trf2", "TRF3": "trf3",
    "TRF4": "trf4", "TRF5": "trf5", "TRF6": "trf6",
}

logging.basicConfig(
    filename=str(LOG_FILE), filemode="a",
    format="%(asctime)s [PARTES_WEB] %(levelname)s — %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("modulo_partes_web")


def _load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"')
    return env


def _normaliza_partes(partes_raw: list) -> dict:
    """Extrai autor/réu de lista DataJud."""
    autores, reus = [], []
    for p in partes_raw:
        tipo = (p.get("tipoParte") or "").lower()
        nome = (p.get("nome") or "").upper().strip()
        if not nome:
            continue
        if any(t in tipo for t in ["ativo", "autor", "requerente", "exequente", "impetrante"]):
            autores.append(nome)
        elif any(t in tipo for t in ["passivo", "réu", "requerido", "executado", "impetrado"]):
            reus.append(nome)
    return {
        "autor": " / ".join(autores) if autores else "",
        "reu": " / ".join(reus) if reus else "",
    }


# ─── Fonte 1: DataJud (cloud-safe) ──────────────────────────────────────────

def buscar_datajud(numero: str, tribunal: str) -> dict:
    sigla = TRIBUNAL_MAP.get(tribunal.upper(), "")
    if not sigla:
        return {}
    headers = {"Authorization": DATAJUD_KEY, "Content-Type": "application/json"}
    payload = {"query": {"match": {"numeroProcesso": numero}}, "size": 1}
    for tentativa in range(1, 4):
        try:
            r = requests.post(
                DATAJUD_URL.format(tribunal=sigla),
                headers=headers, json=payload, timeout=15
            )
            r.raise_for_status()
            hits = r.json().get("hits", {}).get("hits", [])
            if hits:
                src = hits[0]["_source"]
                resultado = _normaliza_partes(src.get("partes", []))
                resultado["fonte"] = "DataJud"
                log.info("DataJud OK: %s → %s × %s", numero,
                         resultado.get("autor", ""), resultado.get("reu", ""))
                return resultado
        except Exception as e:
            log.warning("DataJud tentativa %d para %s: %s", tentativa, numero, e)
            time.sleep(2 ** tentativa)
    return {}


# ─── Fonte 2: Escavador por OAB ─────────────────────────────────────────────

def buscar_escavador_por_oab(numero_cnj: str) -> dict:
    """Usa SDK Escavador para buscar todos os processos do OAB/RO 2952
    e encontrar o processo pelo número CNJ."""
    env = _load_env()
    api_key = env.get("ESCAVADOR_API_KEY", "")
    if not api_key:
        log.warning("ESCAVADOR_API_KEY não configurada em .env")
        return {}
    try:
        import escavador
        escavador.config(api_key)
        from escavador import CriterioOrdenacao, Ordem
        from escavador.v2 import Processo

        _, processos = Processo.por_oab(
            numero=int(OAB_NUMERO),
            estado=OAB_ESTADO,
            ordena_por=CriterioOrdenacao.INICIO,
            ordem=Ordem.DESC,
        )
        numero_limpo = re.sub(r"[.\-]", "", numero_cnj)
        for proc in processos:
            cnj = re.sub(r"[.\-]", "", proc.numero_cnj or "")
            if cnj == numero_limpo:
                resultado = {
                    "autor": (proc.titulo_polo_ativo or "").upper(),
                    "reu": (proc.titulo_polo_passivo or "").upper(),
                    "fonte": "Escavador",
                }
                log.info("Escavador OK: %s → %s × %s", numero_cnj,
                         resultado["autor"], resultado["reu"])
                return resultado
    except ImportError:
        log.warning("SDK Escavador não instalado — pip install escavador")
    except Exception as e:
        log.warning("Escavador erro para %s: %s", numero_cnj, e)
    return {}


def buscar_escavador_direto(numero_cnj: str) -> dict:
    """Consulta direta à API Escavador v1 sem SDK."""
    env = _load_env()
    api_key = env.get("ESCAVADOR_API_KEY", "")
    if not api_key:
        return {}
    try:
        url = "https://api.escavador.com/api/v1/processos/numero_cnj"
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        r = requests.get(url, params={"numero": numero_cnj}, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        itens = data.get("items") or data.get("data") or []
        for item in itens:
            envolvidos = item.get("envolvidos", [])
            autores = [e["nome"] for e in envolvidos if "ativo" in (e.get("tipo_polo") or "").lower()]
            reus = [e["nome"] for e in envolvidos if "passivo" in (e.get("tipo_polo") or "").lower()]
            if autores or reus:
                resultado = {
                    "autor": " / ".join(autores).upper(),
                    "reu": " / ".join(reus).upper(),
                    "fonte": "Escavador-v1",
                }
                log.info("Escavador-v1 OK: %s → %s × %s", numero_cnj,
                         resultado["autor"], resultado["reu"])
                return resultado
    except Exception as e:
        log.warning("Escavador-v1 erro para %s: %s", numero_cnj, e)
    return {}


# ─── Varredura dos relatórios em e-mails ────────────────────────────────────

def extrair_partes_dos_relatorios(numero: str, corpo_relatorio: str) -> dict:
    """Extrai o nome do cliente associado a um número de processo
    dentro do corpo HTML/texto de um relatório MABIOS."""
    # Padrão: "7054209-31.2025.8.22.0001 NOME_CLIENTE"
    padrao = re.compile(
        re.escape(numero) + r"[^\n]*?Cliente[^\n]*?:\s*([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^\n*\|<]+)",
        re.IGNORECASE,
    )
    m = padrao.search(corpo_relatorio)
    if m:
        nome = m.group(1).strip().upper()
        if len(nome) > 3 and not nome.startswith("—"):
            return {"reu": nome, "fonte": "Relatório Gmail"}
    # Padrão alternativo: número seguido de nome na mesma linha
    padrao2 = re.compile(
        re.escape(numero) + r"\s+([A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][A-Za-zÀ-ÿ\s]{5,60}?)(?:\s*[-—|*]|\s*\d{2}/)",
    )
    m2 = padrao2.search(corpo_relatorio)
    if m2:
        nome = m2.group(1).strip().upper()
        if len(nome) > 3:
            return {"reu": nome, "fonte": "Relatório Gmail"}
    return {}


# ─── Pipeline principal ──────────────────────────────────────────────────────

def buscar_partes(numero: str, tribunal: str) -> dict:
    """Tenta todas as fontes em sequência até encontrar as partes."""
    # 1. DataJud (cloud-safe, já temos a chave)
    resultado = buscar_datajud(numero, tribunal)
    if resultado.get("autor") or resultado.get("reu"):
        return resultado

    # 2. Escavador SDK
    resultado = buscar_escavador_por_oab(numero)
    if resultado.get("autor") or resultado.get("reu"):
        return resultado

    # 3. Escavador API direta (v1)
    resultado = buscar_escavador_direto(numero)
    if resultado.get("autor") or resultado.get("reu"):
        return resultado

    log.warning("Nenhuma fonte encontrou partes para %s (%s)", numero, tribunal)
    return {}


def preencher_todos_sem_partes() -> None:
    """Varre processos.json e preenche partes faltantes."""
    if not PROCESSOS_JSON.exists():
        print("[PARTES_WEB] processos.json não encontrado")
        return

    with open(PROCESSOS_JSON, encoding="utf-8") as f:
        dados = json.load(f)

    atualizados = 0
    sem_partes = []
    for proc in dados["processos"]:
        partes = proc.get("partes", {})
        tem_autor = bool(partes.get("autor", "").strip())
        tem_reu = bool(partes.get("reu", "").strip())
        if tem_autor and tem_reu:
            continue
        sem_partes.append(proc)

    print(f"[PARTES_WEB] {len(sem_partes)} processo(s) sem partes completas")

    for proc in sem_partes:
        numero = proc["numero"]
        tribunal = proc.get("tribunal", "")
        resultado = buscar_partes(numero, tribunal)
        if resultado:
            proc.setdefault("partes", {})
            if resultado.get("autor") and not proc["partes"].get("autor"):
                proc["partes"]["autor"] = resultado["autor"]
            if resultado.get("reu") and not proc["partes"].get("reu"):
                proc["partes"]["reu"] = resultado["reu"]
            proc["partes"]["fonte_partes"] = resultado.get("fonte", "")
            atualizados += 1
            print(f"  ✓ {numero} → {resultado.get('autor','')} × {resultado.get('reu','')}")
        else:
            print(f"  ✗ {numero} — não encontrado em nenhuma fonte")
        time.sleep(0.5)  # respeita rate limits

    dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    with open(PROCESSOS_JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"[PARTES_WEB:DONE] {atualizados}/{len(sem_partes)} atualizados")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        num = sys.argv[1]
        # descobre tribunal pelo número
        trib = ""
        if ".8.22." in num:
            trib = "TJRO"
        elif ".8.04." in num:
            trib = "TJAM"
        elif ".4.01." in num:
            trib = "TRF1"
        elif ".4.03." in num:
            trib = "TRF3"
        r = buscar_partes(num, trib)
        print(r or "Não encontrado")
    else:
        preencher_todos_sem_partes()
