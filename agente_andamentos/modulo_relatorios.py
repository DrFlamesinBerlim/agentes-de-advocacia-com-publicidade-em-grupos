"""
modulo_relatorios.py — Relatórios elásticos De Brito Advocacia | OAB/RO 2952

Uso:
  python modulo_relatorios.py --comarca Ariquemes
  python modulo_relatorios.py --cliente "Jonair"
  python modulo_relatorios.py --tribunal TJRO --grau 1
  python modulo_relatorios.py --urgentes
  python modulo_relatorios.py --processo 7057519
  python modulo_relatorios.py --status ATIVO
  python modulo_relatorios.py --tudo

Filtros combinam: --comarca Ariquemes --status ATIVO
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import date, datetime, timezone

BASE           = Path(r"C:/Users/advog/Meu Drive/X")
PROCESSOS_JSON = BASE / "documentos" / "processos.json"
TAREFAS_JSON   = BASE / "documentos" / "tarefas.json"
PRAZOS_JSON    = BASE / "documentos" / "prazos_pendentes.json"


# ─── Carregadores ─────────────────────────────────────────────────────────────

def _processos() -> list[dict]:
    if not PROCESSOS_JSON.exists():
        return []
    return json.loads(PROCESSOS_JSON.read_text(encoding="utf-8")).get("processos", [])


def _tarefas() -> list[dict]:
    if not TAREFAS_JSON.exists():
        return []
    return json.loads(TAREFAS_JSON.read_text(encoding="utf-8")).get("tarefas", [])


def _prazos() -> list[dict]:
    if not PRAZOS_JSON.exists():
        return []
    return json.loads(PRAZOS_JSON.read_text(encoding="utf-8")).get("prazos", [])


# ─── Filtros ──────────────────────────────────────────────────────────────────

def filtrar(processos: list[dict], args) -> list[dict]:
    resultado = processos

    # Status padrão: excluir ARQUIVADO (conferido ainda aparece, pois pode ter prazo)
    if not args.tudo:
        resultado = [p for p in resultado if p.get("status") != "ARQUIVADO"]

    if args.status:
        resultado = [p for p in resultado if p.get("status", "ATIVO").upper() == args.status.upper()]

    if args.comarca:
        termo = args.comarca.lower()
        resultado = [p for p in resultado if termo in p.get("comarca", "").lower()]

    if args.tribunal:
        resultado = [p for p in resultado if args.tribunal.upper() in p.get("tribunal", "").upper()]

    if args.grau:
        # Grau 1: números sem zeros iniciais longos / grau 2: turmas recursais / grau 3: STJ, STF
        grau = str(args.grau)
        if grau == "1":
            resultado = [p for p in resultado if "turma recursal" not in p.get("vara", "").lower()
                         and "tjam" not in p.get("tribunal", "").lower()
                         or "1" in p.get("grau", "")]
        elif grau == "2":
            resultado = [p for p in resultado if "turma recursal" in p.get("vara", "").lower()
                         or p.get("grau") == "2"]

    if args.cliente:
        termo = args.cliente.lower()
        resultado = [p for p in resultado if
                     termo in json.dumps(p.get("partes", {}), ensure_ascii=False).lower()
                     or termo in p.get("obs", "").lower()
                     or termo in " ".join(str(v) for v in p.get("notas", [])).lower()]

    if args.processo:
        resultado = [p for p in resultado if args.processo in p.get("numero", "")]

    if args.urgentes:
        hoje = date.today().isoformat()
        amanha = date.today().isoformat()  # considera hoje e amanhã
        nums_urgentes = set()
        for t in _tarefas():
            if t.get("status") not in ("CONCLUIDA", "CANCELADA") and t.get("prioridade") == "URGENTE":
                nums_urgentes.add(t.get("processo", ""))
        for p in _prazos():
            if p.get("vencimento", "9999") <= hoje:
                nums_urgentes.add(p.get("numero", ""))
        resultado = [p for p in resultado if p.get("numero") in nums_urgentes
                     or any(a.get("prazo_status") in ("URGENTE", "VENCE_HOJE")
                            for a in p.get("andamentos", []))]

    return resultado


# ─── Renderizador ─────────────────────────────────────────────────────────────

def dias_str(venc: str) -> str:
    if not venc:
        return ""
    try:
        d = (date.fromisoformat(venc) - date.today()).days
        if d < 0:
            return f"🚨 VENCIDO há {abs(d)}d"
        if d == 0:
            return "🔴 VENCE HOJE"
        if d <= 2:
            return f"🔴 {d}d"
        if d <= 7:
            return f"🟡 {d}d"
        return f"🟢 {d}d"
    except ValueError:
        return ""


def render_processo(p: dict, tarefas_idx: dict[str, list]) -> str:
    num    = p.get("numero", "")
    status = p.get("status", "ATIVO")
    vara   = p.get("vara", "")
    comarca = p.get("comarca", "")
    classe = p.get("classe", "")
    partes = p.get("partes", {})
    obs    = p.get("obs", "")
    notas  = p.get("notas", [])

    # Partes — usa partes_datajud se disponível, senão campos legados
    partes_dj = p.get("partes_datajud", [])
    if partes_dj:
        nomes = [pt["nome"] for pt in partes_dj if pt.get("nome")]
        cliente = " / ".join(nomes[:3]) or "—"
    else:
        cliente = (partes.get("reu") or partes.get("autor") or
                   partes.get("advogado_reu", "").replace("Dr. Jefferson De Brito — OAB/RO 2952", "").strip()
                   or "—")

    linhas = [f"\n  {'─'*55}"]
    linhas.append(f"  📂 {num}")
    if status != "ATIVO":
        linhas[1] += f"  [{status}]"
    if classe:
        linhas.append(f"     Classe  : {classe}")
    if vara or comarca:
        linhas.append(f"     Vara    : {vara} — {comarca}")
    if cliente and cliente != "—":
        linhas.append(f"     Partes  : {cliente}")

    # Andamentos com prazo
    for a in p.get("andamentos", []):
        venc = a.get("prazo_calculado") or a.get("vencimento", "")
        prazo_info = dias_str(venc)
        mv = a.get("movimento", "")[:60]
        linha = f"     Prazo   : {venc} {prazo_info} | {mv}"
        linhas.append(linha)

    # Tarefas abertas
    for t in tarefas_idx.get(num, []):
        if t.get("status") not in ("CONCLUIDA", "CANCELADA"):
            venc = t.get("vencimento", "")
            prazo_info = dias_str(venc)
            linhas.append(f"     Tarefa  : [{t['id']}] {t['titulo'][:55]} {prazo_info}")

    if obs:
        linhas.append(f"     Obs     : {obs[:80]}")
    if notas:
        nts = notas if isinstance(notas, list) else [notas]
        for n in nts[-1:]:  # só última nota
            linhas.append(f"     Nota    : {str(n)[:80]}")

    return "\n".join(linhas)


def gerar_relatorio(processos: list[dict], titulo: str, args) -> str:
    tarefas = _tarefas()
    tarefas_idx: dict[str, list] = {}
    for t in tarefas:
        num = t.get("processo", "")
        tarefas_idx.setdefault(num, []).append(t)

    linhas = [
        f"\n{'='*57}",
        f"  DE BRITO ADVOCACIA | OAB/RO 2952",
        f"  {titulo}",
        f"  Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"{'='*57}",
    ]

    if not processos:
        linhas.append("\n  Nenhum processo encontrado para o filtro aplicado.")
    else:
        # Agrupar por tribunal/comarca
        grupos: dict[str, list] = {}
        for p in processos:
            chave = f"{p.get('tribunal','?')} — {p.get('comarca','?')}"
            grupos.setdefault(chave, []).append(p)

        for chave, procs in sorted(grupos.items()):
            linhas.append(f"\n  [{chave}] ({len(procs)} processo(s))")
            for p in procs:
                linhas.append(render_processo(p, tarefas_idx))

    linhas.append(f"\n{'='*57}")
    linhas.append(f"  Total: {len(processos)} processo(s)\n")
    return "\n".join(linhas)


# ─── Título automático ────────────────────────────────────────────────────────

def montar_titulo(args) -> str:
    partes = []
    if args.urgentes:
        partes.append("Urgentes / Vencendo Hoje")
    if args.cliente:
        partes.append(f"Cliente: {args.cliente}")
    if args.processo:
        partes.append(f"Processo: {args.processo}")
    if args.comarca:
        partes.append(f"Comarca: {args.comarca}")
    if args.tribunal:
        partes.append(f"Tribunal: {args.tribunal}")
    if args.grau:
        partes.append(f"{args.grau}º Grau")
    if args.status:
        partes.append(f"Status: {args.status}")
    if args.tudo:
        partes.append("Todos os processos (incluindo arquivados)")
    return "Relatório — " + (" | ".join(partes) if partes else "Ativos")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Relatórios elásticos De Brito Advocacia")
    parser.add_argument("--comarca",   help="Filtrar por comarca (ex: Ariquemes)")
    parser.add_argument("--cliente",   help="Filtrar por nome de parte/cliente")
    parser.add_argument("--tribunal",  help="Filtrar por tribunal (TJRO, TJAM, STJ...)")
    parser.add_argument("--grau",      help="Filtrar por grau (1, 2)")
    parser.add_argument("--processo",  help="Filtrar por número (parcial)")
    parser.add_argument("--status",    help="Filtrar por status (ATIVO, CONFERIDO, ARQUIVADO)")
    parser.add_argument("--urgentes",  action="store_true", help="Só urgentes/vencendo hoje")
    parser.add_argument("--tudo",      action="store_true", help="Incluir arquivados")
    parser.add_argument("--salvar",    help="Salvar relatório em arquivo (caminho)")
    args = parser.parse_args()

    processos = _processos()
    filtrados = filtrar(processos, args)
    titulo    = montar_titulo(args)
    relatorio = gerar_relatorio(filtrados, titulo, args)

    print(relatorio)

    if args.salvar:
        Path(args.salvar).write_text(relatorio, encoding="utf-8")
        print(f"Salvo em: {args.salvar}")


if __name__ == "__main__":
    main()
