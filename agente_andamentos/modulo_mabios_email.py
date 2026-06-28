"""
modulo_mabios_email.py — Processador de rascunhos MABIOS
De Brito Advocacia | OAB/RO 2952

Protocolo MABIOS Email:
  Dr. Jefferson escreve rascunho em flamesinberlim@gmail.com com:
  Assunto: MABIOS_ACTION:TIPO:NUMERO_PROCESSO
  Corpo:   instrução/observação livre

  Tipos suportados:
    CONFERIDO  → marca processo como conferido (some dos relatórios ativos)
    ARQUIVAR   → marca processo como arquivado definitivamente
    ATIVO      → reativa processo arquivado/conferido
    URGENTE    → eleva prioridade de todas as tarefas do processo
    NOTA       → adiciona nota ao processo (corpo do rascunho)
    CONCLUIR   → conclui tarefa específica (NUMERO = ID da tarefa, ex: T-001)

Como funciona:
  1. Antigravity chama: python modulo_mabios_email.py processar
  2. Script lê processos.json e tarefas.json locais
  3. Aplica as ações dos rascunhos recebidos via claude_output.txt
  4. Salva os arquivos atualizados
  5. Claude lê os rascunhos via Gmail MCP e gera a lista de ações

Como usar:
  python modulo_mabios_email.py processar       → aplica ações do claude_output.txt
  python modulo_mabios_email.py listar          → mostra rascunhos MABIOS pendentes
  python modulo_mabios_email.py status          → resumo do status de cada processo
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, date, timezone

BASE = Path(r"C:/Users/advog/Meu Drive/X")
PROCESSOS_JSON = BASE / "documentos" / "processos.json"
TAREFAS_JSON   = BASE / "documentos" / "tarefas.json"
CANAL_IN       = BASE / "claude_output.txt"
CANAL_OUT      = BASE / "antigravity_output.txt"

STATUS_VALIDOS = ["ATIVO", "CONFERIDO", "ARQUIVADO"]


# ─── Carregar / Salvar ────────────────────────────────────────────────────────

def carregar_processos() -> dict:
    if not PROCESSOS_JSON.exists():
        return {"atualizado_em": datetime.now(timezone.utc).isoformat(), "processos": []}
    return json.loads(PROCESSOS_JSON.read_text(encoding="utf-8"))


def salvar_processos(dados: dict) -> None:
    dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    PROCESSOS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def carregar_tarefas() -> dict:
    if not TAREFAS_JSON.exists():
        return {"atualizado_em": datetime.now(timezone.utc).isoformat(), "tarefas": []}
    return json.loads(TAREFAS_JSON.read_text(encoding="utf-8"))


def salvar_tarefas(dados: dict) -> None:
    dados["atualizado_em"] = datetime.now(timezone.utc).isoformat()
    TAREFAS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


# ─── Parser de rascunhos ──────────────────────────────────────────────────────

REGEX_MABIOS = re.compile(
    r"MABIOS_ACTION:([A-Z_]+):([^\s\|]+)(?:\|(.+))?",
    re.IGNORECASE
)


def parse_acoes(texto: str) -> list[dict]:
    """Extrai lista de ações MABIOS de um bloco de texto (claude_output.txt)."""
    acoes = []
    for match in REGEX_MABIOS.finditer(texto):
        acoes.append({
            "tipo":    match.group(1).upper(),
            "numero":  match.group(2).strip(),
            "nota":    match.group(3).strip() if match.group(3) else "",
        })
    return acoes


# ─── Aplicar ações ────────────────────────────────────────────────────────────

def aplicar_acao(acao: dict, dados_proc: dict, dados_tar: dict) -> str:
    tipo   = acao["tipo"]
    numero = acao["numero"]
    nota   = acao["nota"]
    hoje   = date.today().isoformat()

    # Ações sobre tarefas (CONCLUIR T-XXX)
    if tipo == "CONCLUIR" and numero.upper().startswith("T-"):
        for t in dados_tar["tarefas"]:
            if t["id"].upper() == numero.upper():
                t["status"] = "CONCLUIDA"
                t["concluida_em"] = hoje
                salvar_tarefas(dados_tar)
                return f"✅ Tarefa {numero} marcada CONCLUÍDA"
        return f"⚠️  Tarefa {numero} não encontrada"

    # Ações sobre processos
    processos = dados_proc["processos"]
    processo = next((p for p in processos if p["numero"] == numero), None)

    if processo is None:
        # Criar entrada mínima
        processo = {
            "numero": numero,
            "status": "ATIVO",
            "tribunal": "TJRO",
            "comarca": "Porto Velho",
            "vara": "",
            "classe": "",
            "partes": {"advogado_reu": "Dr. Jefferson De Brito — OAB/RO 2952"},
            "andamentos": [],
            "origem_mabios": f"criado via MABIOS — {hoje}"
        }
        processos.append(processo)

    if tipo == "CONFERIDO":
        processo["status"] = "CONFERIDO"
        processo["conferido_em"] = hoje
        if nota:
            processo.setdefault("notas", [])
            if isinstance(processo["notas"], str):
                processo["notas"] = [processo["notas"]] if processo["notas"] else []
            processo["notas"].append(f"{hoje}: {nota}")
        return f"✅ {numero} → CONFERIDO"

    elif tipo == "ARQUIVAR":
        processo["status"] = "ARQUIVADO"
        processo["arquivado_em"] = hoje
        if nota:
            processo["motivo_arquivamento"] = nota
        return f"📁 {numero} → ARQUIVADO"

    elif tipo == "ATIVO":
        processo["status"] = "ATIVO"
        processo.pop("conferido_em", None)
        processo.pop("arquivado_em", None)
        return f"🔄 {numero} → ATIVO (reativado)"

    elif tipo == "URGENTE":
        # Eleva prioridade das tarefas abertas do processo
        count = 0
        for t in dados_tar["tarefas"]:
            if t.get("processo") == numero and t.get("status") not in ("CONCLUIDA", "CANCELADA"):
                t["prioridade"] = "URGENTE"
                count += 1
        if count:
            salvar_tarefas(dados_tar)
        return f"🔴 {numero} → {count} tarefa(s) elevada(s) para URGENTE"

    elif tipo == "NOTA":
        processo.setdefault("notas", [])
        if isinstance(processo["notas"], str):
            processo["notas"] = [processo["notas"]] if processo["notas"] else []
        processo["notas"].append(f"{hoje}: {nota}")
        return f"📝 {numero} → nota adicionada: {nota[:50]}"

    elif tipo == "OUTRO":
        # Tipo genérico: apenas adiciona nota
        if nota:
            processo.setdefault("notas", [])
            if isinstance(processo["notas"], str):
                processo["notas"] = [processo["notas"]] if processo["notas"] else []
            processo["notas"].append(f"{hoje} [OUTRO]: {nota}")
            return f"📎 {numero} → nota: {nota[:50]}"
        return f"⚠️  OUTRO sem nota para {numero}"

    else:
        return f"❓ Tipo '{tipo}' não reconhecido para {numero}"


# ─── Comandos ────────────────────────────────────────────────────────────────

def cmd_processar():
    """Lê claude_output.txt e aplica ações MABIOS."""
    if not CANAL_IN.exists():
        print("[ERRO] claude_output.txt não encontrado")
        return

    texto = CANAL_IN.read_text(encoding="utf-8")
    acoes = parse_acoes(texto)

    if not acoes:
        print("Nenhuma ação MABIOS encontrada em claude_output.txt")
        return

    dados_proc = carregar_processos()
    dados_tar  = carregar_tarefas()
    resultados = []

    print(f"\n=== PROCESSANDO {len(acoes)} AÇÃO(ÕES) MABIOS ===\n")
    for acao in acoes:
        resultado = aplicar_acao(acao, dados_proc, dados_tar)
        print(f"  {resultado}")
        resultados.append(resultado)

    salvar_processos(dados_proc)

    # Reportar para antigravity_output.txt
    relatorio = (
        f"MABIOS_RESULT | {datetime.now(timezone.utc).isoformat()}\n"
        f"{len(acoes)} ação(ões) processada(s):\n"
        + "\n".join(f"  {r}" for r in resultados)
    )
    with open(CANAL_OUT, "a", encoding="utf-8") as f:
        f.write(f"\n\n{'='*60}\n{relatorio}\n")

    print(f"\n✅ Salvo em processos.json | Resultado em antigravity_output.txt")


def cmd_listar():
    """Lista processos por status."""
    dados = carregar_processos()
    ativos     = [p for p in dados["processos"] if p.get("status", "ATIVO") == "ATIVO"]
    conferidos = [p for p in dados["processos"] if p.get("status") == "CONFERIDO"]
    arquivados = [p for p in dados["processos"] if p.get("status") == "ARQUIVADO"]

    print(f"\n{'='*60}")
    print(f"  STATUS DOS PROCESSOS — {date.today().strftime('%d/%m/%Y')}")
    print(f"{'='*60}")
    print(f"\n  🟢 ATIVOS ({len(ativos)})")
    for p in ativos:
        print(f"     {p['numero']} — {p.get('classe','')} {p.get('vara','')}")
    print(f"\n  ✅ CONFERIDOS ({len(conferidos)})")
    for p in conferidos:
        print(f"     {p['numero']} — conferido em {p.get('conferido_em','')}")
    print(f"\n  📁 ARQUIVADOS ({len(arquivados)})")
    for p in arquivados:
        print(f"     {p['numero']} — arquivado em {p.get('arquivado_em','')}")
    print(f"\n{'='*60}\n")


def cmd_status():
    """Resumo rápido de status."""
    dados = carregar_processos()
    total = len(dados["processos"])
    por_status = {}
    for p in dados["processos"]:
        s = p.get("status", "ATIVO")
        por_status[s] = por_status.get(s, 0) + 1
    print(f"\nTotal: {total} processo(s)")
    for s, n in sorted(por_status.items()):
        print(f"  {s}: {n}")
    print()


COMANDOS = {
    "processar": cmd_processar,
    "listar":    cmd_listar,
    "status":    cmd_status,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "listar"
    if cmd not in COMANDOS:
        print(f"Uso: {sys.argv[0]} processar | listar | status")
        sys.exit(1)
    COMANDOS[cmd]()
