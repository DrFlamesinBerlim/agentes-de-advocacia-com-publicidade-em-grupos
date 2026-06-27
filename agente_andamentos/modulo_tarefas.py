"""
modulo_tarefas.py — Gestão completa de tarefas jurídicas (De Brito Advocacia)

Tipos de tarefa suportados:
  PRAZO_FATAL      → prazo improrrogável (sustentação oral, contestação, recurso)
  PRAZO_NORMAL     → prazo ordinário (manifestação, petição, juntada)
  SESSAO           → sessão de julgamento (presencial ou eletrônica)
  AUDIENCIA        → audiência marcada
  PEÇA_JURIDICA    → peça a ser redigida (recurso, memorial, embargos)
  DILIGENCIA       → diligência a cumprir (citar, intimar, expedir)
  MONITORAMENTO    → acompanhar andamento sem prazo imediato
  RECURSO          → recurso a interpor após decisão

Status do ciclo de vida:
  ABERTA → EM_ANDAMENTO → CONCLUIDA | CANCELADA | VENCIDA

Como usar:
  python modulo_tarefas.py listar          → todas as tarefas abertas
  python modulo_tarefas.py urgentes        → só as urgentes/vencendo hoje
  python modulo_tarefas.py nova            → assistente interativo para nova tarefa
  python modulo_tarefas.py concluir <id>  → marca tarefa como concluída
  python modulo_tarefas.py processo <num> → tarefas de um processo específico
"""

import json
import sys
from pathlib import Path
from datetime import datetime, date, timezone, timedelta

BASE = Path(r"C:/Users/advog/Meu Drive/X")
TAREFAS_JSON = BASE / "documentos" / "tarefas.json"
PROCESSOS_JSON = BASE / "documentos" / "processos.json"

TIPOS_VALIDOS = [
    "PRAZO_FATAL", "PRAZO_NORMAL", "SESSAO", "AUDIENCIA",
    "PEÇA_JURIDICA", "DILIGENCIA", "MONITORAMENTO", "RECURSO"
]

PRIORIDADE_ORDEM = {"URGENTE": 0, "ALTA": 1, "NORMAL": 2, "BAIXA": 3}

ICONS = {
    "PRAZO_FATAL":   "🔴",
    "PRAZO_NORMAL":  "🟡",
    "SESSAO":        "⚖️",
    "AUDIENCIA":     "🏛️",
    "PEÇA_JURIDICA": "📝",
    "DILIGENCIA":    "📋",
    "MONITORAMENTO": "👁️",
    "RECURSO":       "⬆️",
}


def carregar_tarefas() -> dict:
    if not TAREFAS_JSON.exists():
        return {"atualizado_em": datetime.now(timezone.utc).isoformat(), "tarefas": []}
    return json.loads(TAREFAS_JSON.read_text(encoding="utf-8"))


def salvar_tarefas(dados: dict) -> None:
    dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    TAREFAS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def proximo_id(tarefas: list) -> str:
    ids = [int(t["id"].replace("T-", "")) for t in tarefas if t["id"].startswith("T-")]
    return f"T-{(max(ids) + 1) if ids else 1:03d}"


def dias_para_vencer(vencimento_str: str) -> int | None:
    if not vencimento_str:
        return None
    try:
        venc = date.fromisoformat(vencimento_str)
        return (venc - date.today()).days
    except ValueError:
        return None


def status_prazo(dias: int | None) -> str:
    if dias is None:
        return ""
    if dias < 0:
        return f"🚨 VENCIDO há {abs(dias)}d"
    if dias == 0:
        return "🔴 VENCE HOJE"
    if dias <= 2:
        return f"🔴 {dias}d restante(s)"
    if dias <= 7:
        return f"🟡 {dias}d restante(s)"
    return f"🟢 {dias}d restante(s)"


def cmd_listar(filtro_status: list = None):
    dados = carregar_tarefas()
    tarefas = dados.get("tarefas", [])
    if filtro_status:
        tarefas = [t for t in tarefas if t.get("status") in filtro_status]
    tarefas.sort(key=lambda t: (
        PRIORIDADE_ORDEM.get(t.get("prioridade", "NORMAL"), 2),
        t.get("vencimento", "9999-99-99")
    ))

    print(f"\n{'='*65}")
    print(f"  PAINEL DE TAREFAS — De Brito Advocacia | OAB/RO 2952")
    print(f"  {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*65}")

    if not tarefas:
        print("  Nenhuma tarefa encontrada.")
        return

    for t in tarefas:
        icon = ICONS.get(t.get("tipo", ""), "•")
        dias = dias_para_vencer(t.get("vencimento", ""))
        prazo_info = status_prazo(dias)
        venc_str = t.get("vencimento", "sem prazo")

        print(f"\n  {icon} [{t['id']}] {t['titulo']}")
        print(f"     Processo : {t.get('processo', '')} | {t.get('tribunal', '')}")
        print(f"     Partes   : {t.get('partes', '')[:55]}")
        print(f"     Tipo     : {t.get('tipo')} | Prioridade: {t.get('prioridade')}")
        if venc_str and venc_str != "sem prazo":
            print(f"     Prazo    : {venc_str} {prazo_info}")
        print(f"     Ação     : {t.get('acao_necessaria', '')}")
        if t.get("destinatario"):
            print(f"     Para     : {t['destinatario']}")
        if t.get("notas"):
            print(f"     Notas    : {t['notas']}")

    print(f"\n{'='*65}")
    print(f"  Total: {len(tarefas)} tarefa(s)\n")


def cmd_urgentes():
    dados = carregar_tarefas()
    hoje = date.today().isoformat()
    amanha = (date.today() + timedelta(days=2)).isoformat()
    urgentes = [
        t for t in dados.get("tarefas", [])
        if t.get("status") not in ("CONCLUIDA", "CANCELADA")
        and (
            t.get("prioridade") == "URGENTE"
            or (t.get("vencimento", "9999") <= amanha and t.get("vencimento", ""))
        )
    ]
    dados_filtrados = dict(dados)
    dados_filtrados["tarefas"] = urgentes
    dados["tarefas"] = urgentes
    cmd_listar(filtro_status=None)


def cmd_nova():
    dados = carregar_tarefas()
    nova = {}
    nova["id"] = proximo_id(dados["tarefas"])
    nova["criada_em"] = date.today().isoformat()
    nova["status"] = "ABERTA"

    print("\n=== NOVA TAREFA ===")
    nova["processo"] = input("Número do processo: ").strip()
    nova["tribunal"] = input("Tribunal (TJRO/TJAM/STJ...): ").strip().upper()
    nova["classe"] = input("Classe processual: ").strip()
    nova["partes"] = input("Partes (resumido): ").strip()
    nova["titulo"] = input("Título da tarefa: ").strip()
    nova["descricao"] = input("Descrição detalhada: ").strip()

    print(f"Tipo: {', '.join(TIPOS_VALIDOS)}")
    nova["tipo"] = input("Tipo: ").strip().upper()

    nova["vencimento"] = input("Vencimento (AAAA-MM-DD ou Enter para sem prazo): ").strip()
    nova["prioridade"] = input("Prioridade (URGENTE/ALTA/NORMAL/BAIXA): ").strip().upper()
    nova["acao_necessaria"] = input("Ação necessária: ").strip().upper()
    nova["destinatario"] = input("Destinatário (e-mail ou Enter): ").strip()
    nova["pasta_cliente"] = input("Link pasta cliente (ou Enter): ").strip()
    nova["calendar_id"] = ""
    nova["notas"] = input("Notas adicionais (ou Enter): ").strip()
    nova["origem"] = input("Origem (DJE/PJe/WhatsApp/Manual): ").strip()

    dados["tarefas"].append(nova)
    salvar_tarefas(dados)
    print(f"\n✅ Tarefa {nova['id']} criada: {nova['titulo']}")


def cmd_concluir(task_id: str):
    dados = carregar_tarefas()
    for t in dados["tarefas"]:
        if t["id"].upper() == task_id.upper():
            t["status"] = "CONCLUIDA"
            t["concluida_em"] = date.today().isoformat()
            salvar_tarefas(dados)
            print(f"✅ Tarefa {task_id} marcada como CONCLUÍDA.")
            return
    print(f"❌ Tarefa {task_id} não encontrada.")


def cmd_processo(numero: str):
    dados = carregar_tarefas()
    dados["tarefas"] = [t for t in dados["tarefas"] if numero in t.get("processo", "")]
    cmd_listar()


COMANDOS = {
    "listar":   lambda: cmd_listar(["ABERTA", "EM_ANDAMENTO"]),
    "urgentes": cmd_urgentes,
    "nova":     cmd_nova,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "listar"
    if cmd == "concluir" and len(sys.argv) > 2:
        cmd_concluir(sys.argv[2])
    elif cmd == "processo" and len(sys.argv) > 2:
        cmd_processo(sys.argv[2])
    elif cmd in COMANDOS:
        COMANDOS[cmd]()
    else:
        print(f"Comando inválido: {cmd}")
        print(f"Use: listar | urgentes | nova | concluir <ID> | processo <num>")
        sys.exit(1)
