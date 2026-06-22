"""
INTEGRAÇÃO GOOGLE CALENDAR — DE BRITO ADVOCACIA
Dr. Jefferson Silva de Brito | OAB/RO 2952

Autenticação via SERVICE ACCOUNT (recomendado para automação sem interação humana).
Sem expiração de token, sem necessidade de navegador.

CONFIGURAÇÃO (uma única vez):
1. Acesse console.cloud.google.com
2. Crie projeto > Ative a Google Calendar API
3. Credenciais > Conta de Serviço > crie > baixe JSON como "service_account.json"
4. No Google Calendar > Configurações do Calendário > Compartilhar com email da conta de serviço
   (email formato: nome@projeto.iam.gserviceaccount.com) com permissão "Fazer alterações em eventos"
5. Coloque service_account.json nesta mesma pasta
"""

import json
from datetime import datetime, timedelta, date
from pathlib import Path

SERVICE_ACCOUNT_FILE = Path(__file__).parent / 'service_account.json'
CALENDAR_ID = 'primary'  # ou ID do calendário específico

# Cores Google Calendar
# 11=Tomate(urgente), 6=Tangerina(atenção), 5=Banana(50%), 2=Sálvia(marco inicial)
COR_PRAZO_FINAL   = '11'
COR_MARCO_75      = '6'
COR_MARCO_50      = '5'
COR_MARCO_25      = '2'
COR_PUBLICACAO    = '2'

try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GOOGLE_DISPONIVEL = True
except ImportError:
    GOOGLE_DISPONIVEL = False

TOKEN_FILE       = Path(__file__).parent / 'token_calendar.pickle'
OAUTH_CREDS_FILE = Path(__file__).parent / 'credentials_calendar.json'


def autenticar_calendar():
    """
    Tenta autenticar via Service Account (ideal para automação).
    Se não houver service_account.json, usa OAuth2 com token salvo em pickle.
    Na primeira vez com OAuth2, abre o navegador para login — depois é automático.
    """
    if not GOOGLE_DISPONIVEL:
        print('[CALENDAR] Instale: pip install google-auth google-auth-oauthlib google-api-python-client')
        return None

    # ── 1. Tenta Service Account ────────────────────────────────
    if SERVICE_ACCOUNT_FILE.exists():
        try:
            creds = service_account.Credentials.from_service_account_file(
                str(SERVICE_ACCOUNT_FILE),
                scopes=['https://www.googleapis.com/auth/calendar'],
            )
            service = build('calendar', 'v3', credentials=creds)
            service.calendarList().list(maxResults=1).execute()
            print('[CALENDAR] Autenticado via Service Account.')
            return service
        except Exception as e:
            print(f'[CALENDAR] Service Account falhou: {e}')

    # ── 2. Tenta OAuth2 com token salvo (pickle) ────────────────
    import pickle
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)

    if creds and creds.valid:
        pass  # token ok
    elif creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'wb') as f:
                pickle.dump(creds, f)
            print('[CALENDAR] Token OAuth2 renovado automaticamente.')
        except Exception as e:
            print(f'[CALENDAR] Falha ao renovar token: {e}')
            creds = None
    else:
        # Primeira vez — precisa de credentials_calendar.json e abre navegador
        if not OAUTH_CREDS_FILE.exists():
            print('[CALENDAR] Nenhum método de autenticação disponível.')
            print('           Opção A: coloque service_account.json nesta pasta.')
            print('           Opção B: coloque credentials_calendar.json e rode uma vez interativamente.')
            return None
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(OAUTH_CREDS_FILE),
                scopes=['https://www.googleapis.com/auth/calendar'],
            )
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'wb') as f:
                pickle.dump(creds, f)
            print('[CALENDAR] Autenticado via OAuth2. Token salvo para uso futuro.')
        except Exception as e:
            print(f'[CALENDAR] Falha no OAuth2: {e}')
            return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        service.calendarList().list(maxResults=1).execute()
        print('[CALENDAR] Autenticado via OAuth2.')
        return service
    except Exception as e:
        print(f'[CALENDAR] Falha ao conectar: {e}')
        return None


def criar_evento(service, titulo, data_obj, descricao, cor=COR_MARCO_50,
                 minutos_antes=None, calendar_id=CALENDAR_ID):
    """
    Cria um evento de dia inteiro no Google Calendar.
    """
    if minutos_antes is None:
        minutos_antes = [480, 60]  # 8h e 1h antes

    data_iso = data_obj.isoformat() if hasattr(data_obj, 'isoformat') else str(data_obj)

    evento = {
        'summary': titulo,
        'description': descricao,
        'start': {'date': data_iso, 'timeZone': 'America/Porto_Velho'},
        'end':   {'date': data_iso, 'timeZone': 'America/Porto_Velho'},
        'colorId': str(cor),
        'reminders': {
            'useDefault': False,
            'overrides': (
                [{'method': 'popup', 'minutes': m} for m in minutos_antes] +
                [{'method': 'email', 'minutes': m} for m in minutos_antes]
            ),
        },
    }

    try:
        resultado = service.events().insert(calendarId=calendar_id, body=evento).execute()
        print(f'  [OK] {data_iso} — {titulo[:55]}')
        return resultado
    except Exception as e:
        print(f'  [ERRO] Falha ao criar evento: {e}')
        return None


def criar_marcos_prazo(service, processo, descricao_prazo, fundamento,
                       data_publicacao, data_prazo_final, calendar_id=CALENDAR_ID):
    """
    Cria 5 eventos no Google Calendar para um prazo:
    publicação + 25% + 50% + 75% + vencimento final
    """
    if not service or not data_prazo_final:
        return 0

    numero  = processo.get('numero', '?')
    cliente = processo.get('cliente', numero)
    trib    = processo.get('tribunal', 'TJRO')
    tipo    = processo.get('tipo', '')

    total_dias = (data_prazo_final - data_publicacao).days
    if total_dias <= 0:
        total_dias = 1

    def marco_data(frac):
        return data_publicacao + timedelta(days=int(total_dias * frac))

    def desc_base(extra=''):
        return (
            f'Processo: {numero}\n'
            f'Tribunal: {trib}\n'
            f'Tipo: {tipo}\n'
            f'Cliente: {cliente}\n\n'
            f'Prazo: {descricao_prazo}\n'
            f'Fundamento: {fundamento}\n'
            f'Publicação: {data_publicacao.strftime("%d/%m/%Y")}\n'
            f'Vencimento: {data_prazo_final.strftime("%d/%m/%Y")}\n'
            + (f'\n{extra}' if extra else '') +
            f'\n\nDr. Jefferson Silva de Brito | OAB/RO 2952\nDe Brito Advocacia'
        )

    criados = 0
    marcos = [
        (data_publicacao,       COR_PUBLICACAO, f'📌 Publicação | {numero} | {descricao_prazo}',
         'Início do prazo detectado.', [1440, 480]),
        (marco_data(0.25),      COR_MARCO_25,   f'⏳ 25% do prazo | {numero} | {descricao_prazo}',
         'Primeiro quarto do prazo. Iniciar preparação.', [480, 60]),
        (marco_data(0.50),      COR_MARCO_50,   f'⏳ 50% do prazo | {numero} | {descricao_prazo}',
         'Metade do prazo. Ação recomendada.', [480, 60]),
        (marco_data(0.75),      COR_MARCO_75,   f'⚡ 75% do prazo | {numero} | {descricao_prazo}',
         'Três quartos do prazo! Iniciar redação urgente.', [1440, 480, 60]),
        (data_prazo_final,      COR_PRAZO_FINAL, f'🚨 VENCIMENTO | {numero} | {descricao_prazo}',
         f'PRAZO FATAL — {fundamento}', [1440, 480, 120, 60]),
    ]

    for data_marco, cor, titulo, obs, notifs in marcos:
        r = criar_evento(service, titulo, data_marco, desc_base(obs), cor, notifs, calendar_id)
        if r:
            criados += 1

    return criados


def criar_todos_marcos(service, eventos_list, calendar_id=CALENDAR_ID):
    """
    Interface de compatibilidade com modulo_prazos.gerar_eventos_calendar().
    Recebe lista de dicts no formato antigo e cria no Calendar.
    """
    criados = 0
    for ev in eventos_list:
        data = ev.get('data')
        if isinstance(data, str):
            try:
                data = datetime.strptime(data, '%d/%m/%Y').date()
            except Exception:
                continue
        r = criar_evento(
            service,
            titulo=ev.get('titulo', 'Prazo'),
            data_obj=data,
            descricao=ev.get('descricao', ''),
            cor=ev.get('cor', COR_MARCO_50),
            minutos_antes=ev.get('notificacoes_minutos', [480, 60]),
            calendar_id=calendar_id,
        )
        if r:
            criados += 1
    return criados


def listar_proximos_prazos(service, dias=30, calendar_id=CALENDAR_ID):
    """Lista eventos de prazo nos próximos N dias."""
    agora  = datetime.utcnow().isoformat() + 'Z'
    limite = (datetime.utcnow() + timedelta(days=dias)).isoformat() + 'Z'
    try:
        r = service.events().list(
            calendarId=calendar_id,
            timeMin=agora, timeMax=limite,
            maxResults=50, singleEvents=True, orderBy='startTime',
            q='OAB/RO 2952',
        ).execute()
        return r.get('items', [])
    except Exception as e:
        print(f'[CALENDAR] Erro ao listar: {e}')
        return []


__all__ = [
    'autenticar_calendar',
    'criar_evento',
    'criar_marcos_prazo',
    'criar_todos_marcos',
    'listar_proximos_prazos',
]


if __name__ == '__main__':
    print('Testando autenticação Google Calendar (Service Account)...')
    svc = autenticar_calendar()
    if svc:
        print('[OK] Autenticado! Service Account funcionando.')
        proximos = listar_proximos_prazos(svc, dias=7)
        print(f'[INFO] {len(proximos)} evento(s) nos próximos 7 dias')
    else:
        print('[INFO] Configure service_account.json para ativar o Calendar automático.')
