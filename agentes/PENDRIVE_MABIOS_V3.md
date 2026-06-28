# PENDRIVE MABIOS V3 — Manual de Instalação e Protocolo
**De Brito Advocacia | Ecossistema Trans-LLM**
*Versão: 3.1 | Última revisão: 2026-06-28*

---

## O QUE É O PENDRIVE MABIOS

O Pendrive MABIOS (Multi-Agent Bridge I/O System) é o kit de bootstrap portátil que inicializa o ecossistema Trans-LLM em qualquer máquina do escritório. Ele contém todos os scripts, dependências e configurações necessárias para que o **Antigravity (Agente Local)** entre em operação em minutos.

---

## ESTRUTURA DO PENDRIVE / REPOSITÓRIO

```
MABIOS_V3/
├── install.bat                     ← Instalador principal (rodar como Admin)
├── requirements.txt                ← Dependências Python
├── setup_pasta_x.py                ← Cria estrutura da Pasta X (roda UMA vez)
├── loop_monitor.py                 ← Watchdog principal (daemon permanente)
├── claude_output.txt               ← Canal Claude → Antigravity (não editar manualmente)
├── antigravity_output.txt          ← Canal Antigravity → Claude (não editar manualmente)
├── .env.template                   ← Template de variáveis (copiar para .env local)
│
├── agente_andamentos/              ← Todos os módulos do agente
│   ├── agente_andamentos.py        ← ORQUESTRADOR — ponto de entrada principal
│   ├── atualizar_processos.py      ← Pipeline: DataJud → prazos → partes → calendar
│   ├── modulo_prazos.py            ← Cálculo de prazos CPC (CONGELADO — não modificar)
│   ├── modulo_calendar.py          ← Sincronização com Google Calendar
│   ├── modulo_partes_datajud.py    ← Consulta partes no DataJud CNJ
│   ├── modulo_emails.py            ← Extração de e-mails jurídicos (IMAP Hotmail)
│   ├── modulo_mabios_email.py      ← Processador de rascunhos MABIOS_ACTION
│   ├── modulo_tarefas.py           ← Gestão de tarefas jurídicas (ciclo de vida)
│   ├── sync_github.py              ← Ponte GitHub: push/pull automático
│   ├── agente_whatsapp.py          ← Exportador WhatsApp (CONGELADO — não modificar)
│   └── __init__.py
│
├── documentos/                     ← Dados persistentes (sincronizados via GitHub)
│   ├── processos.json              ← Cadastro de processos (status: ATIVO/CONFERIDO/ARQUIVADO)
│   ├── prazos_pendentes.json       ← Prazos calculados aguardando ação/calendar
│   └── tarefas.json                ← Tarefas jurídicas abertas e em andamento
│
├── config/                         ← Credenciais LOCAIS (nunca no git)
│   ├── credentials.json            ← OAuth Google (nunca commitar)
│   ├── token.json                  ← Token Google gerado (nunca commitar)
│   └── credenciais_pje.enc         ← Credenciais PJe AES-256
│
└── agentes/
    └── PENDRIVE_MABIOS_V3.md       ← Este arquivo (manifesto do sistema)
```

---

## MÓDULOS — RESPONSABILIDADES

| Arquivo | Responsabilidade | Alterar? |
|---|---|---|
| `agente_andamentos.py` | Orquestrador: chama todos os módulos | Sim |
| `atualizar_processos.py` | Pipeline DataJud + prazos | Sim |
| `modulo_prazos.py` | Cálculo CPC art. 218 | **NÃO — CONGELADO** |
| `modulo_calendar.py` | Google Calendar sync | Sim |
| `modulo_partes_datajud.py` | Busca partes no DataJud | Sim |
| `modulo_emails.py` | IMAP Hotmail + extração jurídica | Sim |
| `modulo_mabios_email.py` | Rascunhos MABIOS_ACTION → processos.json | Sim |
| `modulo_tarefas.py` | CRUD de tarefas jurídicas | Sim |
| `sync_github.py` | Push/pull GitHub automático | Sim |
| `agente_whatsapp.py` | WhatsApp export/PTT | **NÃO — CONGELADO** |
| `setup_pasta_x.py` | Setup inicial (roda uma vez) | Não necessário |

**Regra:** se a funcionalidade já tem um módulo, melhore o módulo existente. Não crie `modulo_emails_v2.py` nem `modulo_mabios_novo.py`.

---

## COMANDOS DO ORQUESTRADOR

```powershell
cd "C:\Users\advog\Meu Drive\X"

python agente_andamentos\agente_andamentos.py status     # resumo geral
python agente_andamentos\agente_andamentos.py tudo       # ciclo completo
python agente_andamentos\agente_andamentos.py mabios     # processar rascunhos MABIOS
python agente_andamentos\agente_andamentos.py urgentes   # tarefas urgentes
python agente_andamentos\agente_andamentos.py atualizar  # DataJud + prazos
python agente_andamentos\agente_andamentos.py emails     # varrer e-mails
python agente_andamentos\agente_andamentos.py calendar   # sync calendar
python agente_andamentos\agente_andamentos.py partes     # partes DataJud
python agente_andamentos\agente_andamentos.py tarefas    # painel de tarefas
```

---

## PROTOCOLO DE COMUNICAÇÃO MABIOS

### Fluxo de dados:

```
Dr. Jefferson (celular/Outlook)
       │  cria rascunho: MABIOS_ACTION:TIPO:NUMERO
       ▼
 flamesinberlim@gmail.com (Rascunhos)
       │  Claude lê via Gmail MCP
       ▼
   Claude (Web/Nuvem)
       │  escreve instruções XML em
       ▼
 claude_output.txt  →  GitHub  →  Pasta X local
       │  loop_monitor detecta mudança
       ▼
 loop_monitor.py (Antigravity)
       │  executa modulo_mabios_email.py processar
       ▼
 processos.json / tarefas.json atualizados
       │  Antigravity reporta resultado em
       ▼
 antigravity_output.txt  →  GitHub  →  Claude lê
```

### Protocolo MABIOS_ACTION (rascunhos Gmail):

```
Assunto: MABIOS_ACTION:TIPO:NUMERO_PROCESSO
Corpo:   observação livre (opcional)
```

| Tipo | Efeito |
|---|---|
| `CONFERIDO` | Processo some dos relatórios ativos |
| `ARQUIVAR` | Processo arquivado definitivamente |
| `ATIVO` | Reativa processo conferido/arquivado |
| `URGENTE` | Eleva todas as tarefas do processo para URGENTE |
| `NOTA` | Adiciona nota ao processo (corpo do rascunho) |
| `CONCLUIR` | Conclui tarefa (NUMERO = ID da tarefa, ex: T-001) |

### Tags XML no claude_output.txt:

```xml
<!-- Executar script -->
<commands>
python agente_andamentos\agente_andamentos.py tudo
</commands>

<!-- Gravar arquivo -->
<write_file path="C:/Users/advog/Meu Drive/X/documentos/processos.json">
{ ... }
</write_file>

<!-- Ler arquivo -->
<read_file path="C:/Users/advog/Meu Drive/X/antigravity_output.txt"/>

<!-- Status -->
<status>[ANTIGRAVITY:READY] Aguardando instruções.</status>
```

---

## INSTALAÇÃO RÁPIDA

```powershell
# 1. Abrir PowerShell como Administrador

# 2. Navegar até o pendrive (ajustar letra do drive)
cd "E:\MABIOS_V3"

# 3. Rodar instalador
.\install.bat

# 4. Inicializar Pasta X (apenas na primeira vez)
python setup_pasta_x.py

# 5. Iniciar o monitor em segundo plano
python loop_monitor.py
```

---

## VARIÁVEIS DE AMBIENTE (.env local — nunca no git)

```env
HOTMAIL_ADVO_EMAIL=advogadobrito@hotmail.com
HOTMAIL_ADVO_SENHA=PREENCHER_LOCALMENTE

HOTMAIL_JEFF_EMAIL=jeffersondebrito@hotmail.com
HOTMAIL_JEFF_SENHA=PREENCHER_LOCALMENTE

GMAIL_TRIBUNA=tribuna.livre.ro@gmail.com
GMAIL_FLAMES=flamesinberlim@gmail.com

DATAJUD_API_KEY=ApiKey cDZHYzlZa0JadVREZDJCendFbXNwWnA6MusICgs4R14wMWI1ZUp1ZmQ5djVncw==

GITHUB_BRANCH=claude/upbeat-fermat-0x6gd8
GITHUB_REPO=https://github.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos.git
```

---

## DEPENDÊNCIAS (requirements.txt)

```
watchdog>=4.0.0
requests>=2.31.0
python-dotenv>=1.0.0
schedule>=1.2.0
cryptography>=41.0.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-api-python-client>=2.100.0
pywin32>=306
psutil>=5.9.0
```

---

## SEGURANÇA

| Item | Padrão |
|---|---|
| Credenciais PJe | AES-256 em `credenciais_pje.enc` |
| Token Google | OAuth 2.0 local em `token.json` |
| Senhas e-mail | Apenas no `.env` local — nunca no git |
| Logs | `antigravity_output.txt` — rotação manual |

---

## DIAGNÓSTICO RÁPIDO

```powershell
# Ver últimas linhas do log
Get-Content "C:\Users\advog\Meu Drive\X\antigravity_output.txt" -Tail 20

# Status geral do sistema
python agente_andamentos\agente_andamentos.py status

# Verificar integridade da Pasta X
python -c "
from pathlib import Path
base = Path(r'C:/Users/advog/Meu Drive/X')
arquivos = ['antigravity_output.txt','claude_output.txt','documentos/processos.json','documentos/tarefas.json']
for a in arquivos:
    p = base / a
    print('OK' if p.exists() else 'FALTANDO', a)
"
```

---

## SUPORTE

| Agente | Canal | Função |
|---|---|---|
| Dr. Jefferson | Rascunhos Gmail (MABIOS_ACTION) | Orquestrador e tomador de decisão |
| Claude (nuvem) | `claude_output.txt` / GitHub | Síntese, redação, análise, MABIOS |
| Antigravity (local) | `antigravity_output.txt` | Executor local, DataJud, IMAP |

---

*MABIOS V3.1 — De Brito Advocacia © 2026*
