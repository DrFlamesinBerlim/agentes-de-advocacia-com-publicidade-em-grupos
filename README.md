# MABIOS V3 — Sistema de Automação Jurídica Trans-LLM

**De Brito Advocacia | OAB/RO 2952 | Porto Velho, Rondônia**

> Sistema open-source de automação para escritórios de advocacia usando IA (Claude + Antigravity),
> sincronização via GitHub e integração com PJe, DataJud, Gmail, Google Calendar e WhatsApp.

---

## O que é isso?

Um escritório de advocacia real automatizando processos jurídicos usando:

- **Claude (Anthropic)** na nuvem como agente inteligente
- **Antigravity** — daemon Python rodando 24/7 no Windows local
- **GitHub** como canal de comunicação entre os dois (Trans-LLM)
- **DataJud/CNJ** para buscar andamentos processuais automaticamente
- **Gmail OAuth** para processar comandos por e-mail (protocolo MABIOS)

---

## Arquitetura

```
Dr. Jefferson (celular/PC)
       │
       │ cria rascunho Gmail
       │ Assunto: MABIOS_ACTION:CONFERIDO:7012345-00.2025.8.22.0001
       ▼
  Gmail (flamesinberlim@gmail.com)
       │
       ├──► Claude (nuvem) ──► lê rascunhos ──► atualiza processos.json ──► push GitHub
       │
       └──► Antigravity (local Windows)
                │  git pull (30s)
                │  lê claude_output.txt
                │  executa comandos XML
                │  consulta DataJud
                │  sincroniza Calendar
                └──► git push antigravity_output.txt
```

---

## Protocolo MABIOS

O advogado controla o sistema criando **rascunhos de e-mail** com assunto padronizado:

| Ação | Assunto do rascunho |
|------|---------------------|
| Marcar como conferido | `MABIOS_ACTION:CONFERIDO:NUMERO_PROCESSO` |
| Arquivar definitivamente | `MABIOS_ACTION:ARQUIVAR:NUMERO_PROCESSO` |
| Reativar processo | `MABIOS_ACTION:ATIVO:NUMERO_PROCESSO` |
| Marcar urgente | `MABIOS_ACTION:URGENTE:NUMERO_PROCESSO` |
| Adicionar nota | `MABIOS_ACTION:NOTA:NUMERO_PROCESSO` |
| Concluir tarefa | `MABIOS_ACTION:CONCLUIR:T-001` |
| Instrução livre | `MABIOS_ACTION:OUTRO:NUMERO_PROCESSO` (corpo = instrução) |

Claude lê os rascunhos via OAuth → aplica no `processos.json` → Antigravity sincroniza localmente.

---

## Estrutura de arquivos

```
/
├── agente_andamentos/
│   ├── loop_monitor.py          — daemon principal (30s pull, 15min MABIOS, 120min DataJud)
│   ├── modulo_mabios_email.py   — processa rascunhos MABIOS via Gmail OAuth
│   ├── modulo_emails.py         — varre inbox jurídico + registra andamentos
│   ├── modulo_relatorios.py     — relatórios elásticos por comarca/cliente/tribunal
│   ├── modulo_prazos.py         — cálculo de prazos processuais (FROZEN)
│   ├── modulo_partes_datajud.py — enriquece processos com partes do DataJud
│   ├── modulo_calendar.py       — sincroniza prazos com Google Calendar
│   ├── atualizar_processos.py   — pipeline DataJud completo
│   └── agente_andamentos.py     — orquestrador de comandos
│
├── documentos/
│   ├── processos.json           — base de processos (status, andamentos, partes)
│   ├── tarefas.json             — tarefas abertas por processo
│   └── prazos_pendentes.json    — prazos calculados pendentes
│
├── .claude/commands/            — skills (slash commands) para Claude Code
│   ├── andamentos.md            — /andamentos
│   ├── mabios.md                — /mabios
│   ├── relatorio.md             — /relatorio
│   ├── status.md                — /status
│   ├── sync.md                  — /sync
│   └── powershell.md            — /powershell
│
├── claude_output.txt            — canal Claude → Antigravity (instruções XML)
├── antigravity_output.txt       — canal Antigravity → Claude (logs, respostas)
├── FROZEN.md                    — registro de módulos estáveis
└── agentes/PENDRIVE_MABIOS_V3.md — documentação do protocolo
```

---

## Como rodar (Antigravity local)

**Pré-requisitos:**
- Python 3.11+
- `pip install google-auth google-auth-oauthlib google-api-python-client requests`
- `config/credentials.json` e `config/token.json` (Google OAuth — não incluídos no repo)
- `config/.env` com senhas Hotmail (não incluído no repo)

**Iniciar:**
```powershell
cd "C:\Users\advog\Meu Drive\X"
python agente_andamentos\loop_monitor.py
```

**Comandos avulsos:**
```powershell
# Processar rascunhos MABIOS
python agente_andamentos\modulo_mabios_email.py gmail

# Relatório de processos ativos
python agente_andamentos\modulo_relatorios.py

# Relatório por comarca
python agente_andamentos\modulo_relatorios.py --comarca Ariquemes

# Varrer emails jurídicos e registrar andamentos
python agente_andamentos\modulo_emails.py andamentos
```

---

## Skills no Claude Code

Se usar Claude Code com este repositório, os slash commands ficam disponíveis:

| Comando | O que faz |
|---------|-----------|
| `/andamentos` | Processa emails jurídicos e registra movimentações |
| `/mabios TIPO NUMERO` | Aplica ação MABIOS diretamente |
| `/relatorio [filtro]` | Relatório filtrado por comarca/cliente/tribunal |
| `/status` | Painel rápido do escritório |
| `/sync` | Verifica estado de sincronização GitHub |
| `/powershell` | Comandos prontos para colar no terminal |

---

## Status do projeto

- ✅ MABIOS via rascunhos Gmail (OAuth autônomo)
- ✅ Leitura de inbox jurídico (PJe TJRO, TRF-1, DJE)
- ✅ Registro automático de andamentos em processos.json
- ✅ Cálculo de prazos processuais
- ✅ Relatórios elásticos
- ✅ Sincronização GitHub bidirecional (Trans-LLM)
- ✅ Skills Claude Code (6 slash commands)
- 🔄 Integração DataJud (roda local via Antigravity)
- 🔄 Sync Google Calendar
- 🔄 Processamento WhatsApp (Whisper local)

---

## Contribuições e críticas

Este é um projeto real em produção num escritório de advocacia em Porto Velho/RO.
Feedbacks, issues e PRs são bem-vindos — especialmente sobre:

- Segurança (OAuth, credenciais, dados processuais)
- Arquitetura do canal Trans-LLM
- Integração com outros tribunais (TJAM, TRF-2, STJ)
- Melhorias no cálculo de prazos processuais brasileiros

**Atenção:** dados de processos reais foram anonimizados ou omitidos. Credenciais nunca são commitadas.

---

## Licença

MIT — use, adapte, contribua.

**Dr. Jefferson Silva de Brito | OAB/RO 2952**  
flamesinberlim@gmail.com
