#!/usr/bin/env python3
"""
Consulta de Processos via DataJud API - De Brito Advocacia
Consulta os processos T002 e T007 via API pública do CNJ

Uso:
    python3 consultar_processos_datajud.py YOUR_API_KEY

Onde YOUR_API_KEY é a chave obtida em: https://www.cnj.jus.br/sistemas/datajud/api-publica/
"""

import requests
import json
import sys
from datetime import datetime

# Configuração dos processos a consultar
PROCESSOS = {
    "T002": {
        "numero": "0611311-40.2023.8.04.4400",
        "tribunal": "tjam",  # TJAM - Tribunal de Justiça do Amazonas
        "cliente": "Alexandre Marques de Campos",
        "descricao": "PROTOCOLAR PETIÇÃO RESCISÓRIA",
    },
    "T007": {
        "numero": "7026053-67.2024.8.22.0001",
        "tribunal": "tjro",  # TJRO - Tribunal de Justiça de Rondônia
        "cliente": "Leandro Pereira Cardoso",
        "descricao": "CHECAR ACOMPANHAMENTO MANDADO PRISÃO",
    }
}

# Endpoint da API DataJud
API_BASE = "https://api-publica.datajud.cnj.jus.br"


def consultar_processo(numero_processo, tribunal, api_key):
    """Consulta um processo via DataJud API"""

    # Formatar número do processo (remover caracteres especiais se necessário)
    numero_limpo = numero_processo.replace(".", "").replace("-", "")

    # Construir URL do endpoint
    url = f"{API_BASE}/{tribunal}/asc/{numero_limpo}"

    # Headers com autenticação
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        print(f"  📡 Consultando: {numero_processo} no {tribunal.upper()}...")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {"erro": "Chave API inválida ou expirada"}
        elif response.status_code == 404:
            return {"erro": "Processo não encontrado"}
        else:
            return {"erro": f"HTTP {response.status_code}: {response.reason}"}

    except requests.exceptions.Timeout:
        return {"erro": "Timeout na consulta à API"}
    except requests.exceptions.ConnectionError:
        return {"erro": "Erro de conexão com API DataJud"}
    except Exception as e:
        return {"erro": f"Erro ao consultar: {str(e)}"}


def extrair_movimentacao(dados_processo):
    """Extrai a última movimentação do processo"""

    if "erro" in dados_processo:
        return {
            "status": "ERRO",
            "mensagem": dados_processo["erro"]
        }

    try:
        # Estrutura típica da resposta DataJud
        if "movimentacoes" in dados_processo and len(dados_processo["movimentacoes"]) > 0:
            # Última movimentação é geralmente a primeira da lista
            ultima_mov = dados_processo["movimentacoes"][0]

            return {
                "status": "OK",
                "data": ultima_mov.get("dataMovimentacao", "N/A"),
                "descricao": ultima_mov.get("descricao", "N/A"),
                "tipo": ultima_mov.get("tipo", "N/A"),
                "andamento": dados_processo.get("andamento", "N/A"),
                "classe": dados_processo.get("classe", "N/A"),
                "assunto": dados_processo.get("assunto", "N/A"),
            }
        else:
            return {
                "status": "OK",
                "andamento": dados_processo.get("andamento", "SEM MOVIMENTAÇÃO"),
                "classe": dados_processo.get("classe", "N/A"),
                "assunto": dados_processo.get("assunto", "N/A"),
                "mensagem": "Nenhuma movimentação registrada"
            }

    except KeyError as e:
        return {
            "status": "ERRO",
            "mensagem": f"Erro ao extrair dados: {str(e)}"
        }


def gerar_relatorio(resultados):
    """Gera relatório estruturado dos resultados"""

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    relatorio = {
        "timestamp": timestamp,
        "sistema": "De Brito Advocacia - Consulta DataJud API",
        "processos": {}
    }

    for tarefa, resultado in resultados.items():
        relatorio["processos"][tarefa] = resultado

    return relatorio


def salvar_relatorio(relatorio, nome_arquivo="CONSULTA_PROCESSOS_RESULTADO.json"):
    """Salva o relatório em arquivo JSON"""

    caminho = f"/root/MABIOS/import/{nome_arquivo}"

    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=2)

        return True, caminho
    except Exception as e:
        return False, str(e)


def main():
    """Função principal"""

    if len(sys.argv) < 2:
        print("❌ ERRO: Chave API não fornecida")
        print("\nUso:")
        print("  python3 consultar_processos_datajud.py YOUR_API_KEY")
        print("\nObtém chave em: https://www.cnj.jus.br/sistemas/datajud/api-publica/")
        sys.exit(1)

    api_key = sys.argv[1]

    print("\n" + "="*60)
    print("🔍 CONSULTA DE PROCESSOS - De Brito Advocacia")
    print("   Via DataJud API (CNJ)")
    print("="*60)

    resultados = {}

    # Consultar cada processo
    for tarefa, info in PROCESSOS.items():
        print(f"\n📋 {tarefa} — {info['descricao']}")
        print(f"   Cliente: {info['cliente']}")
        print(f"   Processo: {info['numero']}")

        # Consultar API
        dados = consultar_processo(
            info["numero"],
            info["tribunal"],
            api_key
        )

        # Extrair movimentação
        movimentacao = extrair_movimentacao(dados)

        resultados[tarefa] = {
            "numero": info["numero"],
            "cliente": info["cliente"],
            "descricao": info["descricao"],
            "tribunal": info["tribunal"],
            "movimentacao": movimentacao,
            "dados_completos": dados  # Para referência
        }

        # Exibir resultado
        if movimentacao["status"] == "OK":
            print(f"   ✅ Status: {movimentacao.get('andamento', 'N/A')}")
            if "data" in movimentacao:
                print(f"   📅 Última mov: {movimentacao['data']}")
                print(f"   📝 Descrição: {movimentacao['descricao']}")
        else:
            print(f"   ❌ Erro: {movimentacao['mensagem']}")

    # Gerar e salvar relatório
    print("\n" + "="*60)
    print("📊 Gerando Relatório...")

    relatorio = gerar_relatorio(resultados)
    sucesso, caminho = salvar_relatorio(relatorio)

    if sucesso:
        print(f"✅ Relatório salvo em: {caminho}")
    else:
        print(f"❌ Erro ao salvar: {caminho}")

    # Exibir resumo JSON
    print("\n" + "="*60)
    print("📋 RESULTADO (JSON)")
    print("="*60)
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))

    print("\n" + "="*60)
    print("✅ CONSULTA CONCLUÍDA")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
