# 🔌 PENDRIVE MABIOS V3 — Manual de Instalação e Protocolo
**De Brito Advocacia | Ecossistema Trans-LLM**
*Versão: 3.0 | Última revisão: 2026-06-23*

---

## 📦 O QUE É O PENDRIVE MABIOS

O Pendrive MABIOS (Multi-Agent Bridge I/O System) é o kit de bootstrap portátil que inicializa o ecossistema Trans-LLM em qualquer máquina do escritório. Ele contém todos os scripts, dependências e configurações necessárias para que o **Antigravity (Agente Local)** entre em operação em minutos.

---

## 🗂️ ESTRUTURA DO PENDRIVE

```
MABIOS_V3/
├── install.bat                  ← Instalador principal (rodar como Admin)
├── requirements.txt             ← Dependências Python
├── setup_pasta_x.py             ← Cria estrutura da Pasta X no Drive
├── loop_monitor.py              ← Watchdog principal (daemon)
├── agente_andamentos/
│   ├── agente_andamentos.py
│   ├── atualizar_processos.py
│   ├── modulo_prazos.py
│   └── modulo_calendar.py
├── config/
│   ├── config.json              ← Configurações do ambiente
│   └── credenciais_pje.enc      ← Credenciais criptografadas (AES-256)
└── docs/
    └── PENDRIVE_MABIOS_V3.md    ← Este arquivo
```

---

## ⚙️ INSTALAÇÕES NECESSÁRIAS (PRÉ-REQUISITOS)

### 1. Python 3.11+
```powershell
# Verificar se já está instalado
python --version

# Se não estiver: baixar em https://www.python.org/downloads/
# IMPORTANTE: marcar "Add Python to PATH" durante a instalação
```

### 2. Dependências Python
```powershell
cd "MABIOS_V3"
pip install -r requirements.txt
```

**`requirements.txt` completo:**
```
watchdog>=4.0.0        # Monitor de arquivos em tempo real
requests>=2.31.0       # Requisições HTTP para PJe/APIs
python-dotenv>=1.0.0   # Variáveis de ambiente
schedule>=1.2.0        # Agendamento de tarefas
cryptography>=41.0.0   # Criptografia de credenciais
google-auth>=2.23.0    # Autenticação Google Drive
google-auth-oauthlib>=1.1.0
google-api-python-client>=2.100.0
pywin32>=306           # Integração Windows (notificações, serviços)
psutil>=5.9.0          # Monitoramento de processos do sistema
```

### 3. Google Drive (credenciais OAuth)
```powershell
# Colocar o arquivo credentials.json do Google Cloud Console em:
# C:\Users\advog\Meu Drive\X\config\credentials.json
#
# Na primeira execução, abrirá o browser para autenticação.
# O token será salvo em token.json automaticamente.
```

### 4. Variáveis de Ambiente (`.env`)
Criar o arquivo `C:\Users\advog\Meu Drive\X\.env`:
```env
PJE_LOGIN=seu_cpf_ou_login
PJE_SENHA=sua_senha_pje
GOOGLE_CREDENTIALS_PATH=C:/Users/advog/Meu Drive/X/config/credentials.json
BASE_PATH=C:/Users/advog/Meu Drive/X
LOG_LEVEL=INFO
MONITOR_INTERVAL=5
```

---

## 🚀 INSTALAÇÃO RÁPIDA (PASSO A PASSO)

```powershell
# PASSO 1 — Abrir PowerShell como Administrador

# PASSO 2 — Navegar até o pendrive (ajuste a letra do drive)
cd "E:\MABIOS_V3"

# PASSO 3 — Rodar o instalador automático
.\install.bat

# PASSO 4 — Inicializar a Pasta X (apenas na primeira vez)
python setup_pasta_x.py

# PASSO 5 — Iniciar o monitor em segundo plano
python loop_monitor.py
```

---

## 🔄 PROTOCOLO DE COMUNICAÇÃO MABIOS

### Fluxo de dados:
```
Dr. Jefferson (VSI)
       │
       ▼
   Claude (Web)
       │  escreve instruções XML em
       ▼
 claude_output.txt
       │  watchdog detecta mudança
       ▼
 loop_monitor.py (Antigravity)
       │  executa e reporta em
       ▼
 antigravity_output.txt
       │  Claude lê no próximo turno
       ▼
   Claude (Web)
```

### Tags XML suportadas pelo Antigravity:

#### Gravar arquivo:
```xml
<write_file path="C:/Users/advog/Meu Drive/X/caminho/arquivo.ext">
conteúdo completo do arquivo aqui
</write_file>
```

#### Executar comando PowerShell:
```xml
<commands>
python agente_andamentos/atualizar_processos.py
</commands>
```

#### Ler arquivo e retornar conteúdo:
```xml
<read_file path="C:/Users/advog/Meu Drive/X/documentos/processos.json"/>
```

#### Notificação de status:
```xml
<status>
[ANTIGRAVITY:READY] Sistema operacional. Aguardando instruções.
</status>
```

---

## 🔐 SEGURANÇA

| Item | Padrão |
|------|--------|
| Credenciais PJe | AES-256 criptografado em `credenciais_pje.enc` |
| Token Google | OAuth 2.0, salvo localmente em `token.json` |
| Arquivo `.env` | Nunca commitar no Git (está no `.gitignore`) |
| Logs | Rotação automática a cada 7 dias |
| Acesso remoto | Somente via chave SSH autorizada pelo VSI |

---

## 🩺 DIAGNÓSTICO RÁPIDO

```powershell
# Verificar se o monitor está rodando
Get-Process python | Where-Object {$_.MainWindowTitle -like "*monitor*"}

# Ver últimas linhas do log
Get-Content "C:\Users\advog\Meu Drive\X\antigravity_output.txt" -Tail 20

# Verificar se a Pasta X está íntegra
python -c "
from pathlib import Path
base = Path(r'C:/Users/advog/Meu Drive/X')
arquivos = ['antigravity_output.txt','claude_output.txt','STATUS_OFFICE.md','documentos/processos.json']
for a in arquivos:
    p = base / a
    print('OK' if p.exists() else 'FALTANDO', a)
"
```

---

## 🔁 REINICIAR O SISTEMA

```powershell
# Parar o monitor
Stop-Process -Name python -Force

# Reiniciar
cd "C:\Users\advog\Meu Drive\X"
Start-Process python -ArgumentList "loop_monitor.py" -WindowStyle Hidden
```

---

## 📞 SUPORTE

| Agente | Canal | Função |
|--------|-------|--------|
| Dr. Jefferson (VSI) | Presencial | Orquestrador e tomador de decisão |
| Antigravity | `antigravity_output.txt` | Executor local |
| Claude | `claude_output.txt` | Síntese, redação, análise |

---

*MABIOS V3 — De Brito Advocacia © 2026*
