"""
modulo_whatsapp_parser.py — Preenchedor do template genérico de WhatsApp exports
De Brito Advocacia | OAB/RO 2952

Orquestrador que:
1. Lê exportação WhatsApp (TXT, JSON, PDF)
2. Extrai dados estruturados
3. Preenche whatsapp_export_template.json com dados reais
4. Gera prova processual formatada
5. Indexa processos/partes mencionadas

Template: CONGELADO v1.0 — não alterar
Padrão: Genérico — adapta a qualquer fonte de exportação
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List
import hashlib

BASE = Path(__file__).parent
TEMPLATE_PATH = BASE / "whatsapp_export_template.json"


def carregar_template() -> Dict[str, Any]:
    """Carrega template congelado."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template não encontrado: {TEMPLATE_PATH}")
    with open(TEMPLATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def extrair_timestamp(texto: str) -> str:
    """Tenta extrair timestamp ISO de formato "DD/MM/YYYY HH:MM"."""
    # Padrão brasileiro: 01/07/2026 14:30 ou similares
    match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{2}):(\d{2})", texto)
    if match:
        dia, mes, ano, hora, minuto = match.groups()
        try:
            dt = datetime(int(ano), int(mes), int(dia), int(hora), int(minuto))
            return dt.isoformat()
        except:
            pass
    return datetime.now(timezone.utc).isoformat()


def extrair_participantes_txt(conteudo: str) -> List[Dict[str, Any]]:
    """Extrai nomes únicos de remetentes em exportação TXT."""
    # Padrão: "DD/MM/YYYY HH:MM - NOME: mensagem"
    pattern = r"^\d{1,2}/\d{1,2}/\d{4}\s+\d{2}:\d{2}\s*-\s*([^:]+):"
    nomes = set(re.findall(pattern, conteudo, re.MULTILINE))

    participantes = []
    for i, nome in enumerate(sorted(nomes)):
        participantes.append({
            "id": f"p_{i:03d}",
            "nome": nome.strip(),
            "eh_cliente": False,
            "eh_adversario": False,
            "eh_terceiro": True,
            "contato_whatsapp": None,
            "email": None
        })
    return participantes


def extrair_mensagens_txt(conteudo: str) -> List[Dict[str, Any]]:
    """Extrai mensagens de exportação TXT."""
    mensagens = []
    msg_id = 0

    # Padrão: "DD/MM/YYYY HH:MM - NOME: TEXTO"
    linhas = conteudo.split("\n")
    buffer_corpo = ""
    msg_atual = None

    for linha in linhas:
        match = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{2}):(\d{2})\s*-\s*([^:]+):\s*(.*)", linha)

        if match:
            # Nova mensagem
            if msg_atual:
                msg_atual["corpo_texto"] = buffer_corpo.strip()
                mensagens.append(msg_atual)

            dia, mes, ano, hora, minuto, remetente, corpo = match.groups()
            dt = datetime(int(ano), int(mes), int(dia), int(hora), int(minuto))

            msg_id += 1
            msg_atual = {
                "id": f"msg_{msg_id:06d}",
                "timestamp": dt.isoformat(),
                "data_local": f"{dia}/{mes}/{ano}",
                "hora": f"{hora}:{minuto}",
                "remetente": remetente.strip(),
                "tipo_conteudo": "texto",
                "corpo_texto": corpo,
                "arquivo_original": None,
                "tamanho_bytes": None,
                "duracao_audio_seg": None
            }
            buffer_corpo = corpo
        elif msg_atual and linha.strip():
            # Continuação de mensagem multi-linha
            buffer_corpo += "\n" + linha

    if msg_atual:
        msg_atual["corpo_texto"] = buffer_corpo.strip()
        mensagens.append(msg_atual)

    return mensagens


def indexar_mencoes(mensagens: List[Dict], template_atual: Dict) -> Dict[str, Any]:
    """Identifica processos, partes e documentos mencionados."""
    # Padrão processo: NNNNNNN-DD.AAAA.J.TR.OOOO
    pattern_processo = r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"

    processos_encontrados = {}
    partes_encontradas = {}
    docs_mencionados = set()

    for msg in mensagens:
        corpo = msg.get("corpo_texto", "")

        # Processos
        for match in re.finditer(pattern_processo, corpo):
            numero = match.group()
            if numero not in processos_encontrados:
                processos_encontrados[numero] = {
                    "numero": numero,
                    "mencionado_por": [msg["remetente"]],
                    "datas_mencao": [msg["timestamp"]],
                    "contexto": corpo[:100] + "..." if len(corpo) > 100 else corpo
                }
            elif msg["remetente"] not in processos_encontrados[numero]["mencionado_por"]:
                processos_encontrados[numero]["mencionado_por"].append(msg["remetente"])
                processos_encontrados[numero]["datas_mencao"].append(msg["timestamp"])

        # Referências a documentos jurídicos
        doc_keywords = ["contrato", "petição", "sentença", "acórdão", "despacho", "decisão"]
        for keyword in doc_keywords:
            if keyword.lower() in corpo.lower():
                docs_mencionados.add(f"{keyword} (mencionado em {msg['timestamp'][:10]})")

    return {
        "processos_mencionados": list(processos_encontrados.values()),
        "partes_mencionadas": [],  # Requer mapeamento manual ou AI
        "documentos_mencionados": [{"documento": doc, "tipo": "outro", "datas_mencao": []} for doc in docs_mencionados]
    }


def processar_arquivo_whatsapp(
    caminho_arquivo: Path,
    origem_nome: str,
    descricao_breve: str = "",
    tipo_chat: str = "grupo"
) -> Dict[str, Any]:
    """
    Processa um arquivo de exportação WhatsApp e preenche o template.

    Args:
        caminho_arquivo: Caminho para arquivo TXT/JSON
        origem_nome: Nome da origem (ex: "keyla_usa", "auzier_grupo")
        descricao_breve: Descrição (ex: "Chat com cliente EUA")
        tipo_chat: "individual" ou "grupo"

    Returns:
        Template preenchido com dados reais
    """
    if not caminho_arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

    # Carregar template
    template = carregar_template()

    # Ler conteúdo
    with open(caminho_arquivo, encoding="utf-8") as f:
        conteudo = f.read()

    # Extrair dados
    if caminho_arquivo.suffix.lower() == ".txt":
        participantes = extrair_participantes_txt(conteudo)
        mensagens = extrair_mensagens_txt(conteudo)
    elif caminho_arquivo.suffix.lower() == ".json":
        dados_json = json.loads(conteudo)
        participantes = dados_json.get("participantes", [])
        mensagens = dados_json.get("mensagens", [])
    else:
        raise ValueError(f"Tipo de arquivo não suportado: {caminho_arquivo.suffix}")

    # Indexar menções
    indice = indexar_mencoes(mensagens, template)

    # Calcular hash
    hash_arquivo = hashlib.sha256(conteudo.encode()).hexdigest()

    # Preencher template
    template["exportacao"]["origem"]["fonte"] = origem_nome
    template["exportacao"]["origem"]["descricao"] = descricao_breve
    template["exportacao"]["metadados"]["data_exportacao"] = datetime.now(timezone.utc).isoformat()
    template["exportacao"]["metadados"]["tipo_chat"] = tipo_chat
    template["exportacao"]["metadados"]["nome_chat"] = caminho_arquivo.stem
    template["exportacao"]["metadados"]["total_mensagens"] = len(mensagens)
    template["exportacao"]["metadados"]["total_participantes"] = len(participantes)

    template["participantes"] = participantes
    template["mensagens"]["total"] = len(mensagens)
    template["mensagens"]["dados"] = mensagens

    if mensagens:
        primeiro = min(mensagens, key=lambda m: m["timestamp"])
        ultimo = max(mensagens, key=lambda m: m["timestamp"])
        template["mensagens"]["periodo"]["inicio"] = primeiro["timestamp"]
        template["mensagens"]["periodo"]["fim"] = ultimo["timestamp"]

    template["indice_processual"] = indice
    template["processamento_sistema"]["status_processamento"] = "concluido"
    template["processamento_sistema"]["data_processamento"] = datetime.now(timezone.utc).isoformat()
    template["processamento_sistema"]["hash_arquivo_original"] = hash_arquivo
    template["localizacao_arquivo"]["caminho_original"] = str(caminho_arquivo.absolute())

    return template


def salvar_json_processado(template_preenchido: Dict, pasta_destino: Path) -> Path:
    """Salva template preenchido como JSON estruturado."""
    pasta_destino.mkdir(parents=True, exist_ok=True)

    nome_saida = f"{template_preenchido['exportacao']['origem']['fonte']}_processado.json"
    caminho_saida = pasta_destino / nome_saida

    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(template_preenchido, f, ensure_ascii=False, indent=2)

    return caminho_saida


def gerar_prova_processual_txt(template_preenchido: Dict) -> str:
    """Gera prova processual em texto formatado para judicial."""
    linhas = []

    linhas.append("=" * 80)
    linhas.append("PROVA DOCUMENTAL — EXPORTAÇÃO DE MENSAGENS WHATSAPP")
    linhas.append("=" * 80)

    meta = template_preenchido["exportacao"]["metadados"]
    linhas.append(f"\nPERÍODO: {meta['periodo_inicio']} a {meta['periodo_fim']}")
    linhas.append(f"TIPO DE CHAT: {meta['tipo_chat']}")
    linhas.append(f"TOTAL DE MENSAGENS: {meta['total_mensagens']}")
    linhas.append(f"PARTICIPANTES: {meta['total_participantes']}")

    linhas.append("\n" + "=" * 80)
    linhas.append("PARTICIPANTES")
    linhas.append("=" * 80)
    for p in template_preenchido["participantes"]:
        linhas.append(f"\n• {p['nome']}")

    linhas.append("\n" + "=" * 80)
    linhas.append("MENSAGENS")
    linhas.append("=" * 80)

    for msg in template_preenchido["mensagens"]["dados"][:50]:  # Primeiras 50
        linhas.append(f"\n[{msg['data_local']} {msg['hora']}] {msg['remetente']}:")
        linhas.append(f"  {msg['corpo_texto']}")

    if len(template_preenchido["mensagens"]["dados"]) > 50:
        linhas.append(f"\n... ({len(template_preenchido['mensagens']['dados']) - 50} mensagens adicionais)")

    linhas.append("\n" + "=" * 80)
    linhas.append("PROCESSAMENTO")
    linhas.append("=" * 80)
    proc = template_preenchido["processamento_sistema"]
    linhas.append(f"Status: {proc['status_processamento']}")
    linhas.append(f"Data: {proc['data_processamento']}")
    linhas.append(f"Hash: {proc['hash_arquivo_original']}")

    return "\n".join(linhas)


# ─── Comando CLI ──────────────────────────────────────────────────────────────

def cmd_processar_exportacao(caminho: str, origem: str, descricao: str = "", tipo: str = "grupo"):
    """Processa um arquivo e salva JSON + prova."""
    print(f"\n[WHATSAPP PARSER] Processando: {caminho}")
    print(f"  Origem: {origem}")
    print(f"  Tipo: {tipo}")

    arquivo = Path(caminho)

    # Processar
    template = processar_arquivo_whatsapp(arquivo, origem, descricao, tipo)

    # Salvar JSON
    pasta_saida = Path(r"C:/Users/advog/Meu Drive/X/documentos/whatsapp/processados")
    json_path = salvar_json_processado(template, pasta_saida)
    print(f"  ✅ JSON salvo: {json_path}")

    # Gerar prova
    prova_txt = gerar_prova_processual_txt(template)
    prova_path = pasta_saida / f"{template['exportacao']['origem']['fonte']}_PROVA_PROCESSUAL.txt"
    with open(prova_path, "w", encoding="utf-8") as f:
        f.write(prova_txt)
    print(f"  ✅ Prova processual: {prova_path}")

    return template


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print(f"Uso: python {sys.argv[0]} <caminho_arquivo> <origem_nome> [descricao] [tipo_chat]")
        print(f"Exemplo: python {sys.argv[0]} 'c:/chats/keyla.txt' 'keyla_usa' 'Chat cliente EUA' 'individual'")
        sys.exit(1)

    caminho = sys.argv[1]
    origem = sys.argv[2]
    descricao = sys.argv[3] if len(sys.argv) > 3 else ""
    tipo = sys.argv[4] if len(sys.argv) > 4 else "grupo"

    cmd_processar_exportacao(caminho, origem, descricao, tipo)
