#!/usr/bin/env python3
"""
Orquestrador MABIOS — matriz unificadora CC-001 + GA-002
Dr. Jefferson Silva de Brito | OAB/RO 2952 | De Brito Advocacia

O QUE ESTE SCRIPT É:
  O "heartbeat" permanente do sistema. Roda em loop, numa máquina que fica
  sempre ligada (VM do Google Cloud, PC dedicado, etc.), e faz três coisas:

  1. UNIFICA relatórios — lê processos.json no Drive, gera e envia UM relatório
     por email (substitui o antigo antes de mandar o novo, nunca acumula).
     Isso substitui os envios duplicados que hoje vêm separadamente do
     CC-001 (Apps Script) e do GA-002 (loop_monitor.py).

  2. INDEXA a Pasta X — varre recursivamente e mantém um índice pesquisável
     (indice_pasta_x.json) com nome, id, tipo, data de modificação e caminho
     de cada arquivo. Pesquisar fica instantâneo (busca no índice local, não
     precisa varrer o Drive de novo toda vez).

  3. PROPÕE reorganização — de tempos em tempos, analisa o índice em busca de
     duplicatas, nomes inconsistentes, arquivos soltos fora de pastas
     temáticas etc., e ESCREVE UMA PROPOSTA em propostas_reorganizacao.md.
     NUNCA move, renomeia ou apaga nada sozinho. Você lê a proposta e
     autoriza execução explícita (rodar com --aplicar-proposta N).

O QUE ELE NÃO FAZ (por design, não por limitação esquecida):
  - Não decide sozinho o que apagar ou mover — só sugere.
  - Não substitui a autorização humana em nenhuma ação destrutiva.
  - Não roda dentro desta sessão remota (ela é efêmera). Precisa rodar numa
    máquina sua que fique ligada — VM do Google Cloud, PC local, etc.

SETUP (uma vez):
  1. pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
  2. No Google Cloud Console, ative as APIs: Drive API + Gmail API
  3. Crie uma credencial OAuth "Desktop app", baixe como credentials.json
     e coloque nesta mesma pasta.
  4. Rode: python orquestrador_mabios.py --primeira-vez
     (abre o navegador, você autoriza, gera token.json — só acontece 1x)

USO CONTÍNUO (a matriz rodando):
  python orquestrador_mabios.py
  (roda para sempre, ctrl+C para parar; ideal como serviço systemd / Tarefa
   Agendada do Windows / screen/tmux numa VM)

USO PONTUAL:
  python orquestrador_mabios.py --uma-vez        # roda um ciclo e sai
  python orquestrador_mabios.py --so-indexar     # só reindexar a Pasta X
  python orquestrador_mabios.py --so-relatorio   # só enviar o relatório
  python orquestrador_mabios.py --buscar "termo" # pesquisa no índice local
"""

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
from base64 import urlsafe_b64encode
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ──────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ──────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent

CONFIG = {
    # ID da pasta "X" no Google Drive (a mesma que já existe, com MABIOS_V4,
    # loop_monitor.py, agentes/, documentos/, automacoes/ etc.)
    "PASTA_X_ID": "1ELTiHNa-OYPS_jvfloH4n9I_RNOHMWmW",

    # ID do processos.json no Drive
    "PROCESSOS_FILE_ID": "1HpfH2bbsfbtFstygaNevn4oIl5uBeHgz",

    "EMAIL_DESTINO": "flamesinberlim@gmail.com",

    # Assunto que identifica o relatório unificado. Qualquer email antigo
    # com este OU com os assuntos legados (CC-001, GA-002/MABIOS v3) é
    # substituído — nunca acumula.
    "ASSUNTO_RELATORIO": "[MABIOS] Relatório Unificado",
    "ASSUNTOS_LEGADOS_PARA_SUBSTITUIR": [
        "[CC-001] Relatório Diário",
        "[MOB] [DE BRITO ADV]",
        "[DSK] [DE BRITO ADV]",
        "[MOB] [MABIOS v3]",
        "[DSK] [MABIOS v3]",
    ],

    "SCOPES": [
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ],

    "CREDENTIALS_FILE": str(BASE_DIR / "credentials.json"),
    "TOKEN_FILE": str(BASE_DIR / "token.json"),
    "INDICE_FILE": str(BASE_DIR / "indice_pasta_x.json"),
    "PROPOSTAS_FILE": str(BASE_DIR / "propostas_reorganizacao.md"),
    "LOG_FILE": str(BASE_DIR / "orquestrador.log"),

    # Intervalos do heartbeat, em minutos
    "INTERVALO_RELATORIO_MIN": 60,       # unificação de relatório
    "INTERVALO_INDEXACAO_MIN": 30,       # reindexar Pasta X
    "INTERVALO_PROPOSTA_MIN": 24 * 60,   # propor reorganização 1x/dia
    "INTERVALO_HEARTBEAT_MIN": 5,        # granularidade do loop principal
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(CONFIG["LOG_FILE"], encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("mabios")


# ──────────────────────────────────────────────────────────────────────────
# AUTENTICAÇÃO
# ──────────────────────────────────────────────────────────────────────────

def autenticar():
    """Fluxo OAuth padrão. Gera token.json na primeira vez, depois reutiliza
    e renova sozinho — não pede autorização de novo a cada execução."""
    creds = None
    token_path = Path(CONFIG["TOKEN_FILE"])

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), CONFIG["SCOPES"])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(CONFIG["CREDENTIALS_FILE"]).exists():
                log.error(
                    "credentials.json não encontrado. Baixe do Google Cloud "
                    "Console (OAuth Client ID → Desktop app) e coloque em: %s",
                    CONFIG["CREDENTIALS_FILE"],
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                CONFIG["CREDENTIALS_FILE"], CONFIG["SCOPES"]
            )
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds


def get_services(creds):
    drive = build("drive", "v3", credentials=creds)
    gmail = build("gmail", "v1", credentials=creds)
    return drive, gmail


# ──────────────────────────────────────────────────────────────────────────
# 1. RELATÓRIO UNIFICADO (substitui CC-001 + GA-002)
# ──────────────────────────────────────────────────────────────────────────

def ler_processos(drive):
    request = drive.files().get_media(fileId=CONFIG["PROCESSOS_FILE_ID"])
    conteudo = request.execute().decode("utf-8")
    return json.loads(conteudo)


def parse_data_br(data_str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except (TypeError, ValueError):
        return None


def classificar_prazo(processo):
    prazo = processo.get("prazo_calculado") or {}
    data_final = parse_data_br(prazo.get("data_prazo_final"))
    if not data_final:
        return None, None
    dias_restantes = (data_final.date() - datetime.now().date()).days
    if dias_restantes < 0:
        return "VENCIDO", dias_restantes
    if dias_restantes <= 3:
        return "CRÍTICO", dias_restantes
    if dias_restantes <= 7:
        return "URGENTE", dias_restantes
    if dias_restantes <= 14:
        return "PRÓXIMO", dias_restantes
    return "OK", dias_restantes


def gerar_relatorio_html(processos):
    grupos = {"VENCIDO": [], "CRÍTICO": [], "URGENTE": [], "PRÓXIMO": [], "OK": [], "SEM_PRAZO": []}

    for p in processos:
        status, dias = classificar_prazo(p)
        chave = status or "SEM_PRAZO"
        grupos[chave].append((p, dias))

    def linha(p, dias):
        numero = p.get("numero", "—")
        cliente = p.get("cliente", "—")
        partes = p.get("polo_ativo", "—") + " x " + p.get("polo_passivo", "—") \
            if p.get("polo_ativo") or p.get("polo_passivo") else p.get("partes", "—")
        link = f'https://pje.tjro.jus.br/consulta/?numero={numero}'
        prazo_txt = p.get("prazo_calculado", {}).get("descricao", "—")
        dias_txt = f"{dias}d" if dias is not None else "—"
        return (
            f'<tr><td><a href="{link}">{numero}</a></td>'
            f'<td>{cliente}</td><td>{partes}</td>'
            f'<td>{prazo_txt}</td><td>{dias_txt}</td></tr>'
        )

    ordem = ["VENCIDO", "CRÍTICO", "URGENTE", "PRÓXIMO", "OK", "SEM_PRAZO"]
    cores = {
        "VENCIDO": "#7a0000", "CRÍTICO": "#c0392b", "URGENTE": "#e67e22",
        "PRÓXIMO": "#f1c40f", "OK": "#27ae60", "SEM_PRAZO": "#7f8c8d",
    }

    secoes = []
    for chave in ordem:
        itens = grupos[chave]
        if not itens:
            continue
        linhas = "".join(linha(p, d) for p, d in itens)
        secoes.append(f"""
        <h3 style="color:{cores[chave]}">{chave} ({len(itens)})</h3>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%">
          <tr style="background:#eee"><th>Processo</th><th>Cliente</th><th>Partes</th><th>Prazo</th><th>Dias</th></tr>
          {linhas}
        </table>
        """)

    total = len(processos)
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    return f"""
    <html><body style="font-family:Arial,sans-serif">
      <h2>MABIOS — Relatório Unificado ({total} processos)</h2>
      <p>Gerado em {agora} pelo orquestrador Python (matriz única, substitui CC-001 e GA-002).</p>
      {''.join(secoes)}
    </body></html>
    """


def apagar_emails_antigos(gmail):
    """Substitui, nunca acumula: apaga qualquer relatório anterior (unificado
    ou legado dos dois sistemas antigos) antes de mandar o novo."""
    assuntos = [CONFIG["ASSUNTO_RELATORIO"]] + CONFIG["ASSUNTOS_LEGADOS_PARA_SUBSTITUIR"]
    apagados = 0
    for assunto in assuntos:
        query = f'in:sent subject:"{assunto}"'
        resultado = gmail.users().messages().list(userId="me", q=query).execute()
        for msg in resultado.get("messages", []):
            try:
                gmail.users().messages().trash(userId="me", id=msg["id"]).execute()
                apagados += 1
            except HttpError as e:
                log.warning("Não consegui apagar mensagem %s: %s", msg["id"], e)
    if apagados:
        log.info("Apagados %d email(s) antigo(s) antes de enviar o novo.", apagados)


def enviar_relatorio(gmail, html):
    msg = MIMEText(html, "html", "utf-8")
    msg["to"] = CONFIG["EMAIL_DESTINO"]
    msg["subject"] = f'{CONFIG["ASSUNTO_RELATORIO"]} — {datetime.now().strftime("%d/%m %H:%M")}'
    raw = urlsafe_b64encode(msg.as_bytes()).decode()
    gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
    log.info("Relatório unificado enviado para %s.", CONFIG["EMAIL_DESTINO"])


def ciclo_relatorio(drive, gmail):
    log.info("── Ciclo de relatório iniciado ──")
    try:
        processos = ler_processos(drive)
    except Exception as e:
        log.error("Falha ao ler processos.json: %s", e)
        return
    html = gerar_relatorio_html(processos)
    apagar_emails_antigos(gmail)
    enviar_relatorio(gmail, html)


# ──────────────────────────────────────────────────────────────────────────
# 2. INDEXAÇÃO DA PASTA X (para pesquisa rápida)
# ──────────────────────────────────────────────────────────────────────────

def listar_arquivos_recursivo(drive, pasta_id, caminho="/"):
    arquivos = []
    query = f"'{pasta_id}' in parents and trashed = false"
    page_token = None
    while True:
        resposta = drive.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
            pageToken=page_token,
        ).execute()
        for f in resposta.get("files", []):
            item = {
                "id": f["id"],
                "nome": f["name"],
                "tipo": f["mimeType"],
                "modificado": f.get("modifiedTime"),
                "tamanho": f.get("size"),
                "caminho": caminho + f["name"],
            }
            arquivos.append(item)
            if f["mimeType"] == "application/vnd.google-apps.folder":
                arquivos.extend(
                    listar_arquivos_recursivo(drive, f["id"], caminho + f["name"] + "/")
                )
        page_token = resposta.get("nextPageToken")
        if not page_token:
            break
    return arquivos


def ciclo_indexacao(drive):
    log.info("── Indexação da Pasta X iniciada ──")
    try:
        arquivos = listar_arquivos_recursivo(drive, CONFIG["PASTA_X_ID"])
    except Exception as e:
        log.error("Falha ao indexar Pasta X: %s", e)
        return
    indice = {"gerado_em": datetime.now().isoformat(), "total": len(arquivos), "arquivos": arquivos}
    Path(CONFIG["INDICE_FILE"]).write_text(
        json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log.info("Índice atualizado: %d arquivo(s).", len(arquivos))


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return texto.lower()


def buscar_no_indice(termo):
    indice_path = Path(CONFIG["INDICE_FILE"])
    if not indice_path.exists():
        print("Índice ainda não existe. Rode --so-indexar primeiro.")
        return
    indice = json.loads(indice_path.read_text(encoding="utf-8"))
    termo_norm = normalizar(termo)
    achados = [a for a in indice["arquivos"] if termo_norm in normalizar(a["nome"])]
    if not achados:
        print(f'Nada encontrado para "{termo}".')
        return
    print(f'{len(achados)} resultado(s) para "{termo}":')
    for a in achados:
        print(f'  {a["caminho"]}  (modificado {a["modificado"]})')


# ──────────────────────────────────────────────────────────────────────────
# 3. PROPOSTA DE REORGANIZAÇÃO (nunca executa sozinho)
# ──────────────────────────────────────────────────────────────────────────

def detectar_duplicatas(arquivos):
    vistos = {}
    duplicatas = []
    for a in arquivos:
        chave = normalizar(a["nome"])
        if chave in vistos:
            duplicatas.append((vistos[chave], a))
        else:
            vistos[chave] = a
    return duplicatas


def detectar_soltos_na_raiz(arquivos):
    """Arquivos direto na raiz da Pasta X que parecem pertencer a uma
    subpasta temática já existente (mesmo prefixo de nome que arquivos lá
    dentro), mas que não foram movidos."""
    soltos = [a for a in arquivos if a["caminho"].count("/") == 1 and
              a["tipo"] != "application/vnd.google-apps.folder"]
    return soltos


def gerar_propostas(arquivos):
    duplicatas = detectar_duplicatas(arquivos)
    soltos = detectar_soltos_na_raiz(arquivos)

    linhas = [f"# Propostas de reorganização — {datetime.now().strftime('%d/%m/%Y %H:%M')}", ""]
    n = 0

    if duplicatas:
        linhas.append("## Possíveis duplicatas (mesmo nome, locais diferentes)")
        for original, dup in duplicatas:
            n += 1
            linhas.append(
                f"{n}. `{dup['caminho']}` parece duplicar `{original['caminho']}` "
                f"— sugestão: revisar e manter só a versão mais recente."
            )
        linhas.append("")

    if soltos:
        linhas.append("## Arquivos soltos na raiz da Pasta X")
        for a in soltos:
            n += 1
            linhas.append(
                f"{n}. `{a['caminho']}` — sugestão: mover para uma subpasta "
                f"temática (agentes/, documentos/, automacoes/, backups/)."
            )
        linhas.append("")

    if n == 0:
        linhas.append("Nenhuma sugestão desta vez — estrutura parece organizada.")

    linhas.append("")
    linhas.append(
        "> Nada foi movido, apagado ou renomeado automaticamente. "
        "Revise e autorize execução explicitamente antes de qualquer ação."
    )

    return "\n".join(linhas)


def ciclo_proposta():
    log.info("── Gerando propostas de reorganização ──")
    indice_path = Path(CONFIG["INDICE_FILE"])
    if not indice_path.exists():
        log.warning("Índice ainda não existe, pulando proposta desta vez.")
        return
    indice = json.loads(indice_path.read_text(encoding="utf-8"))
    proposta_md = gerar_propostas(indice["arquivos"])
    Path(CONFIG["PROPOSTAS_FILE"]).write_text(proposta_md, encoding="utf-8")
    log.info("Propostas gravadas em %s", CONFIG["PROPOSTAS_FILE"])


# ──────────────────────────────────────────────────────────────────────────
# LOOP PRINCIPAL (heartbeat)
# ──────────────────────────────────────────────────────────────────────────

def rodar_heartbeat(creds):
    drive, gmail = get_services(creds)

    ultimo_relatorio = datetime.min
    ultima_indexacao = datetime.min
    ultima_proposta = datetime.min

    log.info("Orquestrador MABIOS iniciado — matriz rodando permanentemente.")

    while True:
        agora = datetime.now()

        if agora - ultimo_relatorio >= timedelta(minutes=CONFIG["INTERVALO_RELATORIO_MIN"]):
            ciclo_relatorio(drive, gmail)
            ultimo_relatorio = agora

        if agora - ultima_indexacao >= timedelta(minutes=CONFIG["INTERVALO_INDEXACAO_MIN"]):
            ciclo_indexacao(drive)
            ultima_indexacao = agora

        if agora - ultima_proposta >= timedelta(minutes=CONFIG["INTERVALO_PROPOSTA_MIN"]):
            ciclo_proposta()
            ultima_proposta = agora

        time.sleep(CONFIG["INTERVALO_HEARTBEAT_MIN"] * 60)


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Orquestrador MABIOS — matriz unificadora")
    parser.add_argument("--primeira-vez", action="store_true", help="Roda o fluxo de autorização OAuth e sai.")
    parser.add_argument("--uma-vez", action="store_true", help="Roda um ciclo completo (relatório + índice) e sai.")
    parser.add_argument("--so-indexar", action="store_true", help="Só reindexar a Pasta X.")
    parser.add_argument("--so-relatorio", action="store_true", help="Só enviar o relatório unificado.")
    parser.add_argument("--so-propor", action="store_true", help="Só gerar propostas de reorganização.")
    parser.add_argument("--buscar", metavar="TERMO", help="Pesquisar um termo no índice local.")
    args = parser.parse_args()

    if args.buscar:
        buscar_no_indice(args.buscar)
        return

    creds = autenticar()

    if args.primeira_vez:
        log.info("Autorização concluída. token.json gerado.")
        return

    drive, gmail = get_services(creds)

    if args.so_indexar:
        ciclo_indexacao(drive)
        return
    if args.so_relatorio:
        ciclo_relatorio(drive, gmail)
        return
    if args.so_propor:
        ciclo_proposta()
        return
    if args.uma_vez:
        ciclo_relatorio(drive, gmail)
        ciclo_indexacao(drive)
        ciclo_proposta()
        return

    rodar_heartbeat(creds)


if __name__ == "__main__":
    main()
