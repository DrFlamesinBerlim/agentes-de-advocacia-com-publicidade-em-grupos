"""
agente_andamentos.py — Orquestrador principal do agente de andamentos.
De Brito Advocacia | OAB/RO 2952

Modos:
  python agente_andamentos.py atualizar   → pipeline completo (DataJud + prazos + calendar)
  python agente_andamentos.py partes      → só busca partes no DataJud
  python agente_andamentos.py calendar    → só sincroniza prazos no Calendar
  python agente_andamentos.py emails      → varre e-mails jurídicos (hotmail IMAP)
  python agente_andamentos.py mabios      → processa rascunhos MABIOS do Gmail
  python agente_andamentos.py tarefas     → exibe painel de tarefas abertas
  python agente_andamentos.py urgentes    → só tarefas urgentes/vencendo hoje
  python agente_andamentos.py status      → resumo geral do sistema
  python agente_andamentos.py tudo        → roda tudo em sequência
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(r"C:/Users/advog/Meu Drive/X")
PROCESSOS_JSON = BASE / "documentos" / "processos.json"
PRAZOS_JSON    = BASE / "documentos" / "prazos_pendentes.json"
TAREFAS_JSON   = BASE / "documentos" / "tarefas.json"


# ─── Comandos individuais ─────────────────────────────────────────────────────

def cmd_atualizar():
    """Pipeline DataJud → prazos → partes → calendar."""
    from atualizar_processos import processar
    processar()


def cmd_partes():
    """Enriquece processos.json com nomes das partes via DataJud."""
    from modulo_partes_datajud import enriquecer_processos
    enriquecer_processos()


def cmd_calendar():
    """Sincroniza prazos pendentes com o Google Calendar."""
    from modulo_calendar import sincronizar_prazos
    sincronizar_prazos()


def cmd_emails():
    """Varre contas Hotmail via IMAP e extrai e-mails jurídicos."""
    from modulo_emails import cmd_verificar
    cmd_verificar()


def cmd_mabios():
    """Lê rascunhos MABIOS_ACTION do claude_output.txt e atualiza processos/tarefas."""
    from modulo_mabios_email import cmd_processar
    cmd_processar()


def cmd_tarefas():
    """Exibe painel de tarefas abertas e em andamento."""
    from modulo_tarefas import cmd_listar
    cmd_listar(filtro_status=["ABERTA", "EM_ANDAMENTO"])


def cmd_urgentes():
    """Exibe apenas tarefas urgentes ou vencendo em até 2 dias."""
    from modulo_tarefas import cmd_urgentes as _urgentes
    _urgentes()


def cmd_status():
    """Resumo geral: processos, prazos, tarefas."""
    print(f"\n{'='*55}")
    print(f"  STATUS — De Brito Advocacia | OAB/RO 2952")
    print(f"  {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}")
    print(f"{'='*55}")

    # Processos
    if PROCESSOS_JSON.exists():
        dados = json.loads(PROCESSOS_JSON.read_text(encoding="utf-8"))
        procs = dados.get("processos", [])
        ativos     = [p for p in procs if p.get("status", "ATIVO") == "ATIVO"]
        conferidos = [p for p in procs if p.get("status") == "CONFERIDO"]
        arquivados = [p for p in procs if p.get("status") == "ARQUIVADO"]
        print(f"\n📂 Processos: {len(procs)} total")
        print(f"   🟢 Ativos: {len(ativos)}  ✅ Conferidos: {len(conferidos)}  📁 Arquivados: {len(arquivados)}")
        sem_partes = [p["numero"] for p in ativos if not p.get("partes_datajud")]
        if sem_partes:
            print(f"   ⚠️  Sem partes DataJud: {len(sem_partes)}")
    else:
        print("  ❌ processos.json não encontrado")

    # Prazos
    if PRAZOS_JSON.exists():
        prazos = json.loads(PRAZOS_JSON.read_text(encoding="utf-8")).get("prazos", [])
        hoje = datetime.now().date().isoformat()
        vencidos = [p for p in prazos if p.get("vencimento", "") < hoje]
        hoje_prazos = [p for p in prazos if p.get("vencimento") == hoje]
        print(f"\n⏰ Prazos pendentes: {len(prazos)}")
        if vencidos:
            print(f"   🔴 Vencidos: {len(vencidos)}")
        if hoje_prazos:
            print(f"   🟡 Vencem HOJE: {len(hoje_prazos)}")
    else:
        print("  ❌ prazos_pendentes.json não encontrado")

    # Tarefas
    if TAREFAS_JSON.exists():
        tarefas = json.loads(TAREFAS_JSON.read_text(encoding="utf-8")).get("tarefas", [])
        abertas   = [t for t in tarefas if t.get("status") == "ABERTA"]
        urgentes  = [t for t in abertas if t.get("prioridade") == "URGENTE"]
        print(f"\n📋 Tarefas abertas: {len(abertas)}")
        if urgentes:
            print(f"   🔴 URGENTES: {len(urgentes)}")
            for t in urgentes:
                print(f"      [{t['id']}] {t['titulo']} — vence {t.get('vencimento','sem prazo')}")
    else:
        print("  ❌ tarefas.json não encontrado")

    print(f"\n{'='*55}\n")


def cmd_tudo():
    """Roda pipeline completo: mabios → atualizar → emails → tarefas."""
    print("\n[TUDO] Iniciando ciclo completo...\n")
    cmd_mabios()
    cmd_atualizar()
    cmd_tarefas()
    print("\n[TUDO] Ciclo concluído.")


# ─── Dispatch ─────────────────────────────────────────────────────────────────

COMANDOS = {
    "atualizar": cmd_atualizar,
    "partes":    cmd_partes,
    "calendar":  cmd_calendar,
    "emails":    cmd_emails,
    "mabios":    cmd_mabios,
    "tarefas":   cmd_tarefas,
    "urgentes":  cmd_urgentes,
    "status":    cmd_status,
    "tudo":      cmd_tudo,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd not in COMANDOS:
        print(f"Comando inválido: '{cmd}'")
        print(f"Use: {' | '.join(COMANDOS.keys())}")
        sys.exit(1)
    COMANDOS[cmd]()
