"""
agente_andamentos.py — Orquestrador principal do agente de andamentos.
Pode ser chamado manualmente ou agendado pelo loop_monitor.py.

Modos:
  python agente_andamentos.py atualizar   → atualiza processos + prazos + calendar
  python agente_andamentos.py partes      → só busca partes no DataJud
  python agente_andamentos.py calendar    → só sincroniza prazos no Calendar
  python agente_andamentos.py status      → exibe status atual
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(r"C:/Users/advog/Meu Drive/X")
PROCESSOS_JSON = BASE / "documentos" / "processos.json"
PRAZOS_JSON    = BASE / "documentos" / "prazos_pendentes.json"


def cmd_atualizar():
    from atualizar_processos import processar
    processar()


def cmd_partes():
    from modulo_partes_datajud import enriquecer_processos
    enriquecer_processos()


def cmd_calendar():
    from modulo_calendar import sincronizar_prazos
    sincronizar_prazos()


def cmd_status():
    print(f"\n{'='*50}")
    print(f"  STATUS — De Brito Advocacia | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*50}")

    if PROCESSOS_JSON.exists():
        dados = json.loads(PROCESSOS_JSON.read_text(encoding="utf-8"))
        procs = dados.get("processos", [])
        print(f"\n📂 Processos monitorados: {len(procs)}")
        sem_partes = [p["numero"] for p in procs if not p.get("partes_datajud")]
        if sem_partes:
            print(f"  ⚠️  Sem partes: {len(sem_partes)} processo(s)")
    else:
        print("  ❌ processos.json não encontrado")

    if PRAZOS_JSON.exists():
        prazos = json.loads(PRAZOS_JSON.read_text(encoding="utf-8")).get("prazos", [])
        hoje = datetime.now().date().isoformat()
        vencidos = [p for p in prazos if p.get("vencimento", "") < hoje and not p.get("calendar_id")]
        hoje_prazos = [p for p in prazos if p.get("vencimento") == hoje]
        print(f"\n⏰ Prazos pendentes: {len(prazos)}")
        if vencidos:
            print(f"  🔴 Vencidos sem sync: {len(vencidos)}")
        if hoje_prazos:
            print(f"  🟡 Vencem HOJE: {len(hoje_prazos)}")
    else:
        print("  ❌ prazos_pendentes.json não encontrado")

    print(f"\n{'='*50}\n")


COMANDOS = {
    "atualizar": cmd_atualizar,
    "partes":    cmd_partes,
    "calendar":  cmd_calendar,
    "status":    cmd_status,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd not in COMANDOS:
        print(f"Comando inválido: {cmd}. Use: {list(COMANDOS.keys())}")
        sys.exit(1)
    COMANDOS[cmd]()
