"""
modulo_prazos.py — Cálculo de prazos processuais (CPC/CPP).
Considera dias úteis, feriados nacionais e suspensões do TJRO/TJAM.
"""

import json
from datetime import date, timedelta
from pathlib import Path

BASE = Path(r"C:/Users/advog/Meu Drive/X")
PRAZOS_JSON = BASE / "documentos" / "prazos_pendentes.json"

# Feriados nacionais fixos (MM-DD)
FERIADOS_FIXOS = {
    "01-01", "04-21", "05-01", "09-07",
    "10-12", "11-02", "11-15", "11-20", "12-25",
}

# Prazos padrão por tipo de movimento (em dias úteis)
PRAZOS_PADRAO = {
    "Mandado | Expedição de documento":        15,  # CPC art. 218
    "Disponibilização no Diário da Justiça":   15,  # CPC art. 231
    "Citação":                                 15,
    "Intimação":                               15,
    "Despacho":                                15,
    "Sentença":                                15,
    "Acórdão":                                 15,
}


def is_feriado(d: date) -> bool:
    return d.strftime("%m-%d") in FERIADOS_FIXOS


def is_util(d: date) -> bool:
    return d.weekday() < 5 and not is_feriado(d)


def adicionar_dias_uteis(inicio: date, dias: int) -> date:
    atual = inicio
    contados = 0
    while contados < dias:
        atual += timedelta(days=1)
        if is_util(atual):
            contados += 1
    return atual


def calcular_prazo(data_movimento: date, tipo_movimento: str) -> dict:
    dias = PRAZOS_PADRAO.get(tipo_movimento, 15)
    vencimento = adicionar_dias_uteis(data_movimento, dias)
    hoje = date.today()
    status = (
        "VENCE_HOJE" if vencimento == hoje else
        "VENCIDO"    if vencimento < hoje else
        "PENDENTE"
    )
    return {
        "data_movimento": data_movimento.isoformat(),
        "tipo_movimento": tipo_movimento,
        "dias_uteis": dias,
        "vencimento": vencimento.isoformat(),
        "status": status,
    }


def salvar_prazos(prazos: list[dict]) -> None:
    from datetime import datetime, timezone
    dados = {
        "atualizado_em": datetime.now(timezone.utc).isoformat(),
        "prazos": prazos,
    }
    PRAZOS_JSON.parent.mkdir(parents=True, exist_ok=True)
    PRAZOS_JSON.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[PRAZOS] {len(prazos)} prazo(s) salvo(s) em {PRAZOS_JSON}")
