"""
AGENTE DE ANDAMENTOS PROCESSUAIS — DE BRITO ADVOCACIA
Dr. Jefferson Silva de Brito | OAB/RO 2952
Consulta CNJ DataJud + envia e-mail diário + salva no Google Drive

Roda todo dia às 07h00 via Agendador de Tarefas (Windows)
"""

import json
import os
import smtplib
import ssl
import requests
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Módulos De Brito Advocacia
from modulo_prazos import (
    detectar_tipo_prazo,
    calcular_prazo_final,
    gerar_eventos_calendar,
    TABELA_PRAZOS,
)
from modulo_calendar import (
    autenticar_calendar,
    criar_todos_marcos,
    listar_proximos_prazos,
)

# ─────────────────────────────────────────
# CONFIGURAÇÃO — EDITAR APENAS AQUI
# ─────────────────────────────────────────

CONFIG = {
    # E-mail
    "email_remetente": "flamesinberlim@gmail.com",
    "email_senha_app": "ezaxgwekapoiewpm",  # Ver LEIAME.txt
    "email_destinatario": "flamesinberlim@gmail.com",

    # CNJ DataJud
    "cnj_api_key": "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==",  # Ver LEIAME.txt

    # Arquivos locais
    "arquivo_processos": "processos.json",
    "arquivo_historico": "historico_andamentos.json",
    "pasta_relatorios": "relatorios",
}

# ─────────────────────────────────────────
# PROCESSOS MONITORADOS
# Adicione aqui ou edite processos.json
# ─────────────────────────────────────────

PROCESSOS_PADRAO = [
    {
        "numero": "0000000-00.0000.8.22.0001",  # Substitua pelos números reais
        "cliente": "Charles Novais de Almeida",
        "tipo": "Civil — Caminhão",
        "tribunal": "TJRO"
    },
    # Adicione mais processos aqui
]


# ─────────────────────────────────────────
# FUNÇÕES PRINCIPAIS
# ─────────────────────────────────────────

def carregar_processos():
    """Carrega lista de processos do JSON ou usa padrão"""
    arquivo = Path(CONFIG["arquivo_processos"])
    if arquivo.exists():
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # Cria arquivo com processos padrão
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(PROCESSOS_PADRAO, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Arquivo {arquivo} criado com processos padrão. Edite antes de rodar.")
        return PROCESSOS_PADRAO


def carregar_historico():
    """Carrega histórico de andamentos já vistos"""
    arquivo = Path(CONFIG["arquivo_historico"])
    if arquivo.exists():
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_historico(historico):
    """Salva histórico atualizado"""
    with open(CONFIG["arquivo_historico"], "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


def consultar_datajud(numero_processo):
    """
    Consulta a API DataJud do CNJ
    Retorna lista de movimentos ou None em caso de erro
    """
    # Normaliza número (remove pontos e traços para a query)
    numero_limpo = numero_processo.replace(".", "").replace("-", "")

    url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjro/_search"

    # Adapta a URL conforme o tribunal (detecta pelo número ou campo tribunal)
    headers = {
        "Authorization": f"ApiKey {CONFIG['cnj_api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": {
            "match": {
                "numeroProcesso": numero_processo
            }
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            return None

        processo = hits[0].get("_source", {})
        movimentos = processo.get("movimentos", [])
        return movimentos

    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Falha ao consultar {numero_processo}: {e}")
        return None


def get_url_tribunal(tribunal):
    """Retorna URL base da API DataJud por tribunal"""
    urls = {
        "TJRO":  "https://api-publica.datajud.cnj.jus.br/api_publica_tjro/_search",
        "TJAM":  "https://api-publica.datajud.cnj.jus.br/api_publica_tjam/_search",
        "TRT14": "https://api-publica.datajud.cnj.jus.br/api_publica_trt14/_search",
        "TRF1":  "https://api-publica.datajud.cnj.jus.br/api_publica_trf1/_search",
        "STJ":   "https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search",
        "STF":   "https://api-publica.datajud.cnj.jus.br/api_publica_stf/_search",
        "TST":   "https://api-publica.datajud.cnj.jus.br/api_publica_tst/_search",
    }
    return urls.get(tribunal.upper(), urls["TJRO"])


def consultar_processo_completo(processo_info):
    """Consulta DataJud com URL correta por tribunal"""
    numero = processo_info["numero"]
    tribunal = processo_info.get("tribunal", "TJRO")
    url = get_url_tribunal(tribunal)

    headers = {
        "Authorization": f"ApiKey {CONFIG['cnj_api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": {
            "match": {
                "numeroProcesso": numero
            }
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            return None
        return hits[0].get("_source", {})
    except Exception as e:
        print(f"[ERRO] {numero}: {e}")
        return None


def detectar_prazos(movimento_nome):
    """Detecta se um andamento implica prazo a correr"""
    gatilhos = [
        "intimad", "citad", "notificad", "prazo", "contrarrazões",
        "resposta", "manifestação", "impugnação", "recurso", "embargos",
        "audiência", "julgamento", "sentença", "acórdão", "despacho"
    ]
    nome_lower = movimento_nome.lower()
    for gatilho in gatilhos:
        if gatilho in nome_lower:
            return True
    return False


def processar_novidades(processos, historico):
    """
    Compara andamentos novos com histórico.
    Retorna lista de novidades.
    """
    novidades = []

    for proc in processos:
        numero = proc["numero"]
        print(f"[INFO] Consultando: {numero} ({proc['cliente']})")

        dados = consultar_processo_completo(proc)
        if not dados:
            print(f"[AVISO] Sem dados para {numero}")
            continue

        movimentos = dados.get("movimentos", [])
        if not movimentos:
            continue

        # Pega o último movimento
        ultimo = movimentos[0]  # DataJud retorna em ordem decrescente
        ultima_data = ultimo.get("dataHora", "")
        ultimo_nome = ultimo.get("nome", "")

        # Chave do histórico
        chave = numero

        # Verifica se é novo
        ultimo_visto = historico.get(chave, {}).get("ultima_data", "")

        if ultima_data != ultimo_visto:
            # É novidade!
            tem_prazo = detectar_prazos(ultimo_nome)
            novidades.append({
                "numero": numero,
                "cliente": proc["cliente"],
                "tipo": proc["tipo"],
                "tribunal": proc.get("tribunal", "TJRO"),
                "movimento": ultimo_nome,
                "data": ultima_data,
                "tem_prazo": tem_prazo,
                "todos_movimentos_hoje": [
                    m for m in movimentos
                    if m.get("dataHora", "").startswith(str(date.today()))
                ]
            })

            # Atualiza histórico
            historico[chave] = {
                "ultima_data": ultima_data,
                "ultimo_movimento": ultimo_nome,
                "atualizado_em": datetime.now().isoformat()
            }

    return novidades, historico


def formatar_email_html(novidades, data_consulta):
    """Gera HTML do e-mail de relatório"""

    if not novidades:
        corpo = """
        <p>Nenhuma movimentação nova foi detectada nos processos monitorados.</p>
        <p>O sistema continua monitorando.</p>
        """
    else:
        itens = ""
        alertas_prazo = [n for n in novidades if n["tem_prazo"]]

        if alertas_prazo:
            itens += """
            <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:12px;margin-bottom:20px;border-radius:4px;">
                <strong>⚠️ ATENÇÃO — POSSÍVEL PRAZO EM CURSO</strong><br>
                Os processos abaixo tiveram movimentações que podem indicar prazo correndo.
                Verifique imediatamente.
            </div>
            """

        for n in novidades:
            cor_borda = "#dc3545" if n["tem_prazo"] else "#198754"
            icone = "⚠️" if n["tem_prazo"] else "📋"
            alerta_prazo = "<br><span style='color:#dc3545;font-weight:bold;'>⚠️ VERIFICAR PRAZO</span>" if n["tem_prazo"] else ""

            # Formata data
            try:
                dt = datetime.fromisoformat(n["data"].replace("Z", "+00:00"))
                data_fmt = dt.strftime("%d/%m/%Y %H:%M")
            except:
                data_fmt = n["data"]

            itens += f"""
            <div style="border-left:4px solid {cor_borda};padding:12px;margin-bottom:16px;background:#f8f9fa;border-radius:4px;">
                <strong>{icone} {n['cliente']}</strong>{alerta_prazo}<br>
                <span style="color:#666;font-size:13px;">Processo: {n['numero']} | {n['tribunal']}</span><br>
                <span style="color:#666;font-size:13px;">Tipo: {n['tipo']}</span><br>
                <hr style="border:none;border-top:1px solid #ddd;margin:8px 0;">
                <strong>Movimentação:</strong> {n['movimento']}<br>
                <strong>Data:</strong> {data_fmt}
            </div>
            """

        corpo = itens

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;padding:20px;color:#333;">

        <div style="background:#1a1a2e;color:white;padding:20px;border-radius:8px;margin-bottom:24px;">
            <h2 style="margin:0;font-size:18px;">⚖️ DE BRITO ADVOCACIA</h2>
            <p style="margin:4px 0 0;font-size:13px;opacity:0.8;">
                Dr. Jefferson Silva de Brito | OAB/RO 2952<br>
                Relatório de Andamentos — {data_consulta}
            </p>
        </div>

        <h3 style="color:#1a1a2e;border-bottom:2px solid #1a1a2e;padding-bottom:8px;">
            Movimentações Detectadas
        </h3>

        {corpo}

        <div style="margin-top:32px;padding:12px;background:#f0f0f0;border-radius:4px;font-size:12px;color:#666;">
            Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br>
            Fonte: CNJ DataJud | Agente De Brito Advocacia
        </div>

    </body>
    </html>
    """
    return html


def salvar_relatorio_local(novidades, data_consulta):
    """Salva relatório JSON localmente"""
    pasta = Path(CONFIG["pasta_relatorios"])
    pasta.mkdir(exist_ok=True)

    nome_arquivo = f"andamentos_{date.today().isoformat()}.json"
    caminho = pasta / nome_arquivo

    relatorio = {
        "data_consulta": data_consulta,
        "total_novidades": len(novidades),
        "novidades": novidades
    }

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Relatório salvo em: {caminho}")
    return caminho


def enviar_email(html_body, novidades, data_consulta):
    """Envia e-mail via Gmail SMTP"""
    total = len(novidades)
    tem_prazo = any(n["tem_prazo"] for n in novidades)

    # Assunto dinâmico
    if total == 0:
        assunto = f"✅ Andamentos {data_consulta} — Sem novidades"
    elif tem_prazo:
        assunto = f"⚠️ PRAZO! Andamentos {data_consulta} — {total} movimentação(ões)"
    else:
        assunto = f"📋 Andamentos {data_consulta} — {total} movimentação(ões)"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = CONFIG["email_remetente"]
    msg["To"] = CONFIG["email_destinatario"]

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(CONFIG["email_remetente"], CONFIG["email_senha_app"])
            server.sendmail(
                CONFIG["email_remetente"],
                CONFIG["email_destinatario"],
                msg.as_bytes()
            )
        print(f"[OK] E-mail enviado: {assunto}")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail: {e}")
        return False


# ─────────────────────────────────────────
# EXECUÇÃO PRINCIPAL
# ─────────────────────────────────────────

def processar_prazos_calendar(novidades: list, service) -> int:
    """
    Para cada novidade, detecta se há prazo, gera os 4 marcos
    e cria os eventos no Google Calendar.
    Retorna total de eventos criados.
    """
    if not service:
        print("[AVISO] Google Calendar não autenticado — prazos não serão criados")
        return 0

    total_criados = 0

    for nov in novidades:
        movimento = nov.get("movimento", "")
        tipo_prazo = detectar_tipo_prazo(movimento)

        if not tipo_prazo:
            print(f"[INFO] Movimento sem prazo mapeado: {movimento[:50]}")
            continue

        prazo_info = TABELA_PRAZOS.get(tipo_prazo, {})
        print(f"[PRAZO] {nov['cliente']} → {prazo_info.get('descricao', tipo_prazo)}")

        # Tenta parsear a data do movimento
        try:
            dt_str = nov.get("data", "")
            if dt_str:
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                data_pub = dt.date()
            else:
                data_pub = date.today()
        except Exception:
            data_pub = date.today()

        # Gera os 5 eventos (publicação + 3 marcos + final)
        eventos = gerar_eventos_calendar(
            processo_info={
                "numero": nov["numero"],
                "cliente": nov["cliente"],
                "tipo": nov.get("tipo", ""),
                "tribunal": nov.get("tribunal", "TJRO"),
            },
            movimento=movimento,
            data_publicacao=data_pub,
        )

        if eventos:
            criados = criar_todos_marcos(service, eventos)
            total_criados += criados
            print(f"[OK] {criados} marcos criados no Calendar para {nov['cliente']}")

    return total_criados


def main():
    print("=" * 60)
    print(f"AGENTE DE ANDAMENTOS — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("De Brito Advocacia | Dr. Jefferson | OAB/RO 2952")
    print("=" * 60)

    data_consulta = date.today().strftime("%d/%m/%Y")

    # 1. Carrega dados
    processos = carregar_processos()
    historico = carregar_historico()
    print(f"[INFO] {len(processos)} processo(s) monitorado(s)")

    # 2. Autentica Google Calendar
    print("[INFO] Autenticando Google Calendar...")
    service_calendar = autenticar_calendar()

    # 3. Consulta CNJ e detecta novidades
    novidades, historico_atualizado = processar_novidades(processos, historico)

    # 4. Salva histórico atualizado
    salvar_historico(historico_atualizado)

    # 5. Cria prazos no Google Calendar
    if novidades:
        print(f"\n[PRAZOS] Processando {len(novidades)} novidade(s)...")
        total_eventos = processar_prazos_calendar(novidades, service_calendar)
        print(f"[PRAZOS] {total_eventos} evento(s) criados no Google Calendar")

    # 6. Lista próximos prazos (para incluir no e-mail)
    proximos_prazos = []
    if service_calendar:
        proximos_prazos = listar_proximos_prazos(service_calendar, dias=15)

    # 7. Salva relatório local
    salvar_relatorio_local(novidades, data_consulta)

    # 8. Gera e envia e-mail
    html = formatar_email_html(novidades, data_consulta)
    enviar_email(html, novidades, data_consulta)

    print(f"\n[CONCLUÍDO] {len(novidades)} novidade(s) | {len(proximos_prazos)} prazo(s) nos próximos 15 dias")
    print("=" * 60)


if __name__ == "__main__":
    main()
