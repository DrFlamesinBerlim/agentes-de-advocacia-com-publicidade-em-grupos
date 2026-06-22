"""
AGENTE DE ANDAMENTOS — DE BRITO ADVOCACIA
Dr. Jefferson Silva de Brito | OAB/RO 2952

1. Consulta CNJ DataJud para cada processo
2. Detecta movimentos novos (compara com andamentos salvos)
3. Calcula prazos processuais para movimentos novos (modulo_prazos)
4. Cria marcos no Google Calendar (modulo_calendar)
5. Atualiza processos.json

Executado pelo executar_agente.bat via Agendador de Tarefas (07h00 diario).
"""

import sys
import os
import io
import json
import requests
from datetime import datetime, date
from collections import OrderedDict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modulo_prazos import detectar_tipo_prazo, calcular_prazo_final, gerar_4_marcos, TABELA_PRAZOS
from modulo_calendar import autenticar_calendar, criar_todos_marcos
from modulo_prazos import gerar_eventos_calendar

PASTA   = Path(__file__).parent
ARQUIVO = PASTA / 'processos.json'

API_KEY = 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='
HEADERS = {'Authorization': f'ApiKey {API_KEY}', 'Content-Type': 'application/json'}
URLS = {
    'TJRO':  'https://api-publica.datajud.cnj.jus.br/api_publica_tjro/_search',
    'TJAM':  'https://api-publica.datajud.cnj.jus.br/api_publica_tjam/_search',
    'TRT14': 'https://api-publica.datajud.cnj.jus.br/api_publica_trt14/_search',
    'TRF1':  'https://api-publica.datajud.cnj.jus.br/api_publica_trf1/_search',
    'STJ':   'https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search',
    'STF':   'https://api-publica.datajud.cnj.jus.br/api_publica_stf/_search',
    'TST':   'https://api-publica.datajud.cnj.jus.br/api_publica_tst/_search',
}


def fmt_data(dh):
    try:
        return datetime.fromisoformat(dh.replace('Z', '+00:00')).strftime('%d/%m/%Y')
    except Exception:
        return dh[:10] if dh else '—'


def parse_data(dh):
    """Retorna objeto date a partir de string ISO do DataJud."""
    try:
        return datetime.fromisoformat(dh.replace('Z', '+00:00')).date()
    except Exception:
        return date.today()


def ultimos3_agrupados(movimentos):
    """
    DataJud retorna movimentos em ordem crescente (mais antigo primeiro).
    Inverte, agrupa por data, retorna 3 dias mais recentes com descricoes concatenadas.
    """
    grupos = OrderedDict()
    for m in reversed(movimentos):
        data = fmt_data(m.get('dataHora', ''))
        nome = m.get('nome', '?')
        if data not in grupos:
            grupos[data] = []
        if nome not in grupos[data]:
            grupos[data].append(nome)

    resultado = []
    for data, nomes in list(grupos.items())[:3]:
        resultado.append({'data': data, 'descricao': ' | '.join(nomes)})
    return resultado


def consultar_datajud(numero, tribunal):
    url = URLS.get(tribunal.upper(), URLS['TJRO'])
    n20 = numero.replace('-', '').replace('.', '')
    payload = {'size': 1, 'query': {'match': {'numeroProcesso': n20}}}
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=15)
        hits = r.json().get('hits', {}).get('hits', [])
        if hits:
            src = hits[0].get('_source', {})
            return src.get('movimentos', [])
    except Exception as e:
        print(f'  [ERRO DataJud] {e}')
    return []


def calcular_e_criar_marcos(processo, mov_nome, mov_data_obj, service_calendar):
    """
    Detecta tipo de prazo no movimento, calcula marcos e cria no Google Calendar.
    Retorna dict com info do prazo calculado, ou None se nao detectado.
    """
    tipo = detectar_tipo_prazo(mov_nome)
    if not tipo:
        return None

    prazo_info = TABELA_PRAZOS.get(tipo)
    if not prazo_info:
        return None

    data_final = calcular_prazo_final(mov_data_obj, prazo_info)
    marcos_datas = gerar_4_marcos(mov_data_obj, data_final)

    prazo_resumo = {
        'tipo': tipo,
        'descricao': prazo_info['descricao'],
        'fundamento': prazo_info['fundamento'],
        'dias': prazo_info['dias'],
        'tipo_contagem': prazo_info['tipo_contagem'],
        'data_publicacao': mov_data_obj.strftime('%d/%m/%Y'),
        'data_prazo_final': data_final.strftime('%d/%m/%Y') if data_final else None,
        'urgente': prazo_info.get('urgente', False),
    }

    print(f'  [PRAZO] {prazo_info["descricao"]} — vence {prazo_resumo["data_prazo_final"]}')

    if service_calendar:
        eventos = gerar_eventos_calendar(
            processo_info={
                'numero': processo['numero'],
                'cliente': processo.get('cliente', processo['numero']),
                'tipo': processo.get('tipo', ''),
                'tribunal': processo.get('tribunal', 'TJRO'),
            },
            movimento=mov_nome,
            data_publicacao=mov_data_obj,
        )
        criados = criar_todos_marcos(service_calendar, eventos)
        print(f'  [CALENDAR] {criados} marcos criados no Google Calendar')
        prazo_resumo['marcos_calendar'] = criados
        prazo_resumo['calendar_ok'] = True
    else:
        # Salva prazo pendente para criação manual via MCP ou futura autenticação
        prazo_resumo['calendar_ok'] = False
        print(f'  [CALENDAR] Prazo salvo em prazos_pendentes.json para criacao manual')

    return prazo_resumo


def movimento_eh_novo(processo, novo_andamento):
    """
    Compara o andamento mais recente novo com o salvo anteriormente.
    Retorna True se for diferente (nova movimentacao detectada).
    """
    andamentos_salvos = processo.get('andamentos', [])
    if not andamentos_salvos:
        return True
    salvo = andamentos_salvos[0]
    return salvo.get('data') != novo_andamento['data'] or salvo.get('descricao') != novo_andamento['descricao']


def main():
    print('=' * 60)
    print(f'AGENTE DE ANDAMENTOS — {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    print('De Brito Advocacia | Dr. Jefferson | OAB/RO 2952')
    print('=' * 60)

    with open(ARQUIVO, encoding='utf-8') as f:
        processos = json.load(f)

    # Tenta autenticar Google Calendar (falha silenciosa se nao configurado)
    print('\n[CALENDAR] Tentando autenticar Google Calendar...')
    service_calendar = None
    try:
        service_calendar = autenticar_calendar()
        if service_calendar:
            print('[CALENDAR] Autenticado com sucesso!')
        else:
            print('[CALENDAR] Nao autenticado — prazos serao calculados mas nao criados no Calendar')
    except Exception as e:
        print(f'[CALENDAR] Falha: {e}')

    atualizados   = 0
    novos_movs    = 0
    prazos_criados = 0

    print()
    for p in processos:
        numero   = p['numero']
        tribunal = p.get('tribunal', 'TJRO')
        print(f'[{tribunal}] {numero}')

        movimentos = consultar_datajud(numero, tribunal)

        if not movimentos:
            if 'andamentos' not in p:
                p['andamentos'] = [{'data': p.get('ultima_mov', '—'), 'descricao': p.get('mov_desc', '—')}]
            print(f'  [--] Sem dados no DataJud')
            continue

        andamentos = ultimos3_agrupados(movimentos)

        # Detecta se houve movimento novo desde a ultima atualizacao
        if movimento_eh_novo(p, andamentos[0]):
            novos_movs += 1
            mov_mais_recente = list(reversed(movimentos))[0]  # o mais recente individual
            mov_nome     = mov_mais_recente.get('nome', '')
            mov_data_obj = parse_data(mov_mais_recente.get('dataHora', ''))

            print(f'  [NOVO] {andamentos[0]["data"]} — {andamentos[0]["descricao"][:60]}')

            prazo = calcular_e_criar_marcos(p, mov_nome, mov_data_obj, service_calendar)
            if prazo:
                p['prazo_calculado'] = prazo
                prazos_criados += 1
                # Atualiza flag de prazo no processo baseado na urgencia
                if prazo.get('urgente'):
                    p['prazo'] = 'urgente'
            else:
                print(f'  [INFO] Movimento sem prazo mapeado: {mov_nome[:50]}')
        else:
            print(f'  [=] Sem novidades — ultimo: {andamentos[0]["data"]}')

        p['andamentos']  = andamentos
        p['ultima_mov']  = andamentos[0]['data']
        p['mov_desc']    = andamentos[0]['descricao']
        atualizados += 1

    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(processos, f, ensure_ascii=False, indent=2)

    # Salva prazos sem Calendar para criação posterior
    pendentes = [
        {
            'numero': p['numero'],
            'tribunal': p.get('tribunal', 'TJRO'),
            'cliente': p.get('cliente', p['numero']),
            'tipo': p.get('tipo', ''),
            'orgao': p.get('orgao', ''),
            'prazo_calculado': p['prazo_calculado'],
        }
        for p in processos
        if p.get('prazo_calculado') and not p['prazo_calculado'].get('calendar_ok')
    ]
    pendentes_arquivo = PASTA / 'prazos_pendentes.json'
    with open(pendentes_arquivo, 'w', encoding='utf-8') as f:
        json.dump(pendentes, f, ensure_ascii=False, indent=2)
    if pendentes:
        print(f'\n[PENDENTE] {len(pendentes)} prazo(s) aguardando criacao no Calendar')
        print(f'           Arquivo: prazos_pendentes.json')

    print()
    print('=' * 60)
    print(f'Processos atualizados : {atualizados}/{len(processos)}')
    print(f'Movimentos novos      : {novos_movs}')
    print(f'Prazos calculados     : {prazos_criados}')
    print('=' * 60)


if __name__ == '__main__':
    main()
