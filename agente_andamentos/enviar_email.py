import sys, io, smtplib, ssl, json
from datetime import datetime, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

EMAIL = 'flamesinberlim@gmail.com'
SENHA = 'ezaxgwekapoiewpm'

from pathlib import Path
PASTA_RAIZ = Path(__file__).resolve().parent.parent
with open(PASTA_RAIZ / 'documentos' / 'processos.json', encoding='utf-8') as f:
    processos = json.load(f)

hoje  = date.today().strftime('%d/%m/%Y')
hora  = datetime.now().strftime('%H:%M')

def data_key(p):
    d = p.get('ultima_mov', '01/01/1900')
    try:
        return datetime.strptime(d, '%d/%m/%Y')
    except:
        return datetime(1900, 1, 1)

urgentes  = sorted([p for p in processos if p.get('prazo','') == 'urgente'],  key=data_key, reverse=True)
atencao   = sorted([p for p in processos if p.get('prazo','') == 'atencao'],  key=data_key, reverse=True)
verificar = sorted([p for p in processos if p.get('prazo','') == 'verificar'], key=data_key, reverse=True)
normais   = sorted([p for p in processos if p.get('prazo','') not in ('urgente','atencao','verificar')], key=data_key, reverse=True)
tjro      = [p for p in processos if p.get('tribunal','') == 'TJRO']
tjam      = [p for p in processos if p.get('tribunal','') == 'TJAM']

COR   = {'urgente':'#cc2222','atencao':'#cc7700','verificar':'#aa9900','ok':'#226622'}
BG    = {'urgente':'#200000','atencao':'#1a0d00','verificar':'#191600','ok':'#001a08'}
LBL   = {'urgente':'URGENTE','atencao':'ATENCAO','verificar':'VERIFICAR','ok':'NORMAL'}
ICO   = {'urgente':'&#9888;','atencao':'&#9888;','verificar':'&#9998;','ok':'&#10003;'}
TCOR  = {'TJRO':'#c9a84c','TJAM':'#4ca87c','TRF1':'#4c8ac9'}


def linha(label, valor, cor_val='#c0b88a'):
    if not valor or valor in ('—',''):
        return ''
    return (
        f'<tr>'
        f'<td style="padding:5px 14px;font-size:11px;color:#5a5030;width:110px;vertical-align:top;white-space:nowrap">{label}</td>'
        f'<td style="padding:5px 14px;font-size:12px;color:{cor_val};line-height:1.4">{valor}</td>'
        f'</tr>'
    )


def sep():
    return '<tr><td colspan="2" style="height:1px;background:#1e1a08"></td></tr>'


def card(p, num):
    pr   = p.get('prazo', 'ok')
    cor  = COR.get(pr, '#226622')
    bg   = BG.get(pr, '#001a08')
    lbl  = LBL.get(pr, 'NORMAL')
    ico  = ICO.get(pr, '&#10003;')
    trib = p.get('tribunal', '?')
    tcor = TCOR.get(trib, '#c9a84c')

    numero   = p.get('numero', '?')
    ativo    = p.get('polo_ativo', '—')
    passivo  = p.get('polo_passivo', '—')
    classe   = p.get('classe', p.get('tipo', '?'))
    orgao    = p.get('orgao', '—')
    assunto  = p.get('assunto', '—')
    andamentos = p.get('andamentos', [])
    if not andamentos:
        andamentos = [{'data': p.get('ultima_mov', '—'), 'descricao': p.get('mov_desc', '—')}]

    linhas = ''
    for i, mov in enumerate(andamentos[:3]):
        mov_data = mov.get('data', '—')
        mov_desc = mov.get('descricao', '—')
        label = 'Último andamento' if i == 0 else f'{i+1}º anterior'
        cor_data = '#c9a84c' if i == 0 else '#7a6a30'
        cor_desc = '#9a9060' if i == 0 else '#5a5030'
        linhas += sep()
        linhas += (
            f'<tr><td style="padding:6px 14px;font-size:11px;color:#5a5030;vertical-align:top;white-space:nowrap">{label}</td>'
            f'<td style="padding:6px 14px">'
            f'<span style="font-size:11px;font-weight:bold;color:{cor_data}">{mov_data}</span>'
            f'<span style="display:block;font-size:11px;color:{cor_desc};margin-top:1px">{mov_desc}</span>'
            f'</td></tr>'
        )

    # Bloco de prazo calculado (se existir)
    prazo_calc = p.get('prazo_calculado')
    linhas_prazo = ''
    if prazo_calc and prazo_calc.get('data_prazo_final'):
        linhas_prazo += (
            f'<tr><td colspan="2" style="background:#1a0000;padding:0">'
            f'<table width="100%" cellpadding="0" cellspacing="0">'
            f'<tr><td colspan="2" style="height:1px;background:#440000"></td></tr>'
            f'<tr>'
            f'<td style="padding:7px 14px;font-size:11px;color:#884444;vertical-align:top;white-space:nowrap">&#9873; Prazo</td>'
            f'<td style="padding:7px 14px">'
            f'<span style="font-size:12px;font-weight:bold;color:#ff6666">{prazo_calc["data_prazo_final"]}</span>'
            f'<span style="display:block;font-size:10px;color:#884444;margin-top:1px">'
            f'{prazo_calc["descricao"]} &mdash; {prazo_calc["dias"]} dias {prazo_calc["tipo_contagem"]}'
            f'</span>'
            f'<span style="display:block;font-size:10px;color:#553333;margin-top:1px">{prazo_calc["fundamento"]}</span>'
            f'</td></tr>'
            f'<tr><td colspan="2" style="height:1px;background:#440000"></td></tr>'
            f'</table></td></tr>'
        )

    linhas_info = ''
    if ativo and ativo not in ('—', ''):
        linhas_info += sep() + linha('Polo Ativo', ativo, '#e0d8a0')
    if passivo and passivo not in ('—', ''):
        linhas_info += sep() + linha('Polo Passivo', passivo, '#e0d8a0')
    linhas_info += sep() + linha('Classe', classe, '#b0a878')
    linhas_info += sep() + linha('Assunto', assunto, '#a09060')
    linhas_info += sep() + linha('Vara / Órgão', orgao, '#a09060')
    linhas = linhas_prazo + linhas + linhas_info

    return (
        f'<div style="margin-bottom:10px;border-left:4px solid {cor};border-radius:3px;overflow:hidden;background:#0d0d02">'

        f'<table width="100%" cellpadding="0" cellspacing="0" style="background:#111104;border-bottom:1px solid #1e1a08">'
        f'<tr>'
        f'<td style="padding:8px 14px">'
        f'<span style="font-size:9px;font-weight:bold;color:{tcor};letter-spacing:1.5px">{trib}</span>'
        f'&nbsp;<span style="font-size:9px;color:#333210">|</span>&nbsp;'
        f'<span style="font-size:9px;color:#5a5030">{p.get("comarca","")}</span>'
        f'&nbsp;&nbsp;<span style="font-size:9px;color:#2a2508">#{num}</span>'
        f'</td>'
        f'<td style="padding:8px 14px;text-align:right">'
        f'<span style="background:{bg};color:{cor};font-size:9px;font-weight:bold;padding:3px 9px;border-radius:2px;border:1px solid {cor}">{ico} {lbl}</span>'
        f'</td>'
        f'</tr>'
        f'</table>'

        f'<div style="padding:8px 14px 4px;background:#0a0a00;border-bottom:1px solid #1e1a08">'
        f'<span style="font-size:9px;color:#5a5030;text-transform:uppercase;letter-spacing:.8px">Processo</span><br>'
        f'<span style="font-family:monospace;font-size:13px;font-weight:bold;color:#c9a84c;letter-spacing:.3px">{numero}</span>'
        f'</div>'

        f'<table width="100%" cellpadding="0" cellspacing="0">{linhas}</table>'
        f'</div>'
    )


def secao(titulo, lista, cor, start=1):
    if not lista:
        return '', start
    cards = ''
    for i, p in enumerate(lista):
        cards += card(p, start + i)
    h = (
        f'<div style="margin:18px 0 8px;padding-bottom:6px;border-bottom:2px solid {cor}">'
        f'<span style="font-size:10px;font-weight:bold;color:{cor};text-transform:uppercase;letter-spacing:1.5px">{titulo}</span>'
        f'&nbsp;<span style="font-size:10px;color:#2a2508">({len(lista)})</span>'
        f'</div>'
    )
    return h + cards, start + len(lista)


alerta = ''
if urgentes:
    alerta = (
        f'<div style="background:#200000;border:1px solid #660000;border-radius:3px;padding:12px 14px;margin-bottom:16px">'
        f'<span style="color:#ff5555;font-weight:bold;font-size:12px">&#9888; {len(urgentes)} processo(s) com prazo urgente</span><br>'
        f'<span style="color:#774444;font-size:10px">Verifique imediatamente no PJe TJRO.</span>'
        f'</div>'
    )

idx = 1
s1, idx = secao('Urgente &mdash; verificar imediatamente', urgentes, '#cc2222', idx)
s2, idx = secao('Atencao &mdash; prazo proximo',           atencao,  '#cc7700', idx)
s3, idx = secao('Verificar prazo',                         verificar,'#aa9900', idx)
s4, idx = secao('Processos ativos &mdash; sem prazo imediato', normais, '#336622', idx)

html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{margin:0;padding:0;background:#040400;font-family:Arial,sans-serif;-webkit-text-size-adjust:100%}}
@media(max-width:600px){{
  .wrap{{padding:0 !important}}
  .stat-val{{font-size:20px !important}}
  .num-proc{{font-size:12px !important}}
}}
</style>
</head>
<body>
<div class="wrap" style="max-width:640px;margin:0 auto">

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#060600;border-bottom:2px solid #c9a84c">
    <tr>
      <td width="48" style="padding:14px 0 14px 16px">
        <div style="width:40px;height:40px;border-radius:50%;background:#c9a84c;text-align:center;line-height:40px;font-weight:900;font-size:14px;color:#000">DB</div>
      </td>
      <td style="padding:14px 16px">
        <div style="font-size:15px;font-weight:bold;color:#c9a84c;letter-spacing:.5px">DE BRITO ADVOCACIA</div>
        <div style="font-size:10px;color:#7a6030;margin-top:2px">Dr. Jefferson Silva de Brito &nbsp;|&nbsp; OAB/RO 2952 &nbsp;|&nbsp; {hoje} {hora}</div>
      </td>
    </tr>
  </table>

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#080800;border-bottom:1px solid #1e1a08">
    <tr>
      <td width="25%" style="padding:12px 8px 12px 16px">
        <div style="font-size:9px;color:#5a5030;text-transform:uppercase;letter-spacing:.8px">Total</div>
        <div class="stat-val" style="font-size:22px;font-weight:bold;color:#c9a84c">{len(processos)}</div>
        <div style="font-size:9px;color:#333210">processos</div>
      </td>
      <td width="25%" style="padding:12px 8px">
        <div style="font-size:9px;color:#5a5030;text-transform:uppercase;letter-spacing:.8px">Urgentes</div>
        <div class="stat-val" style="font-size:22px;font-weight:bold;color:#ff4444">{len(urgentes)}</div>
        <div style="font-size:9px;color:#333210">hoje</div>
      </td>
      <td width="25%" style="padding:12px 8px">
        <div style="font-size:9px;color:#5a5030;text-transform:uppercase;letter-spacing:.8px">Atencao</div>
        <div class="stat-val" style="font-size:22px;font-weight:bold;color:#ffaa22">{len(atencao)}</div>
        <div style="font-size:9px;color:#333210">prazo prox.</div>
      </td>
      <td width="25%" style="padding:12px 16px 12px 8px">
        <div style="font-size:9px;color:#5a5030;text-transform:uppercase;letter-spacing:.8px">TJRO/TJAM</div>
        <div class="stat-val" style="font-size:22px;font-weight:bold;color:#44aa44">{len(tjro)}/{len(tjam)}</div>
        <div style="font-size:9px;color:#333210">tribunais</div>
      </td>
    </tr>
  </table>

  <div style="padding:12px 16px 20px">
    {alerta}
    {s1}{s2}{s3}{s4}
  </div>

  <div style="background:#040400;border-top:1px solid #1e1a08;padding:10px 16px">
    <span style="font-size:9px;color:#2a2508">Relatorio automatico &mdash; {hoje} {hora} &nbsp;|&nbsp; Agente De Brito Advocacia &nbsp;|&nbsp; OAB/RO 2952</span>
  </div>

</div>
</body></html>"""

msg = MIMEMultipart('alternative')
assunto = f'[DE BRITO ADV] {hoje} | {len(urgentes)} urgente(s) | {len(processos)} processos'
msg['Subject'] = assunto
msg['From']    = EMAIL
msg['To']      = EMAIL
msg.attach(MIMEText(html, 'html', 'utf-8'))

print(f'Enviando para {EMAIL}...')
ctx = ssl.create_default_context()
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ctx) as s:
    s.login(EMAIL, SENHA)
    s.sendmail(EMAIL, EMAIL, msg.as_bytes())

print('EMAIL ENVIADO!')
print(f'Assunto: {assunto}')
