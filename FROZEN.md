# FROZEN — Módulos Estáveis | De Brito Advocacia MABIOS V3

> Última revisão: 28/06/2026  
> Critério: testado + aprovado + não requer mudança imediata

---

## 🧊 CONGELADOS — Não modificar sem autorização explícita

| Módulo | Versão | Congelado em | Motivo |
|--------|--------|-------------|--------|
| `agente_andamentos/modulo_prazos.py` | original | sempre | Cálculo de prazos — lógica jurídica validada |
| `agente_andamentos/agente_whatsapp.py` | original | sempre | Processamento WhatsApp — núcleo crítico |
| `agente_andamentos/modulo_mabios_email.py` | v1.0 | 28/06/2026 | Rascunhos MABIOS via OAuth — testado |
| `agente_andamentos/modulo_relatorios.py` | v1.0 | 28/06/2026 | Relatórios elásticos — filtros validados |
| `agente_andamentos/sync_github.py` | v1.0 | 28/06/2026 | Sync GitHub — REPO_DIR=BASE confirmado |
| `loop_monitor.py` | v1.0 | 28/06/2026 | Daemon principal — ciclos 30s/15min/120min |
| `.claude/commands/powershell.md` | v1.0 | 28/06/2026 | Skill comandos PowerShell |
| `.claude/commands/mabios.md` | v1.0 | 28/06/2026 | Skill ações MABIOS |
| `.claude/commands/relatorio.md` | v1.0 | 28/06/2026 | Skill relatório elástico |
| `.claude/commands/status.md` | v1.0 | 28/06/2026 | Skill painel status |
| `.claude/commands/sync.md` | v1.0 | 28/06/2026 | Skill sync GitHub |
| `.claude/commands/andamentos.md` | v1.0 | 28/06/2026 | Skill andamentos via email |

---

## 🔧 ATIVOS — Em desenvolvimento ou dados vivos

| Módulo | Status | Observação |
|--------|--------|-----------|
| `agente_andamentos/modulo_emails.py` | v2.0 ativo | Gmail inbox + andamentos — amadurecendo |
| `agente_andamentos/atualizar_processos.py` | ativo | Pipeline DataJud |
| `agente_andamentos/modulo_partes_datajud.py` | ativo | Enriquecimento de partes |
| `agente_andamentos/modulo_calendar.py` | ativo | Sync Google Calendar |
| `documentos/processos.json` | dados vivos | Sempre atualizar — 54 processos (28/06) |
| `documentos/tarefas.json` | dados vivos | Tarefas abertas |
| `documentos/prazos_pendentes.json` | dados vivos | Prazos calculados |

---

## 📋 Regras de congelamento

1. **FROZEN ≠ perfeito** — significa estável o suficiente para não mexer agora
2. **Para melhorar um FROZEN:** descongelar aqui, editar no lugar, recongelar
3. **Nunca criar** `modulo_emails_v2.py` — editar o original
4. **Nunca duplicar** `loop_monitor_novo.py` — editar o original
5. **Dr. Jefferson pode pedir congelamento** a qualquer momento: "congela X"
6. **Dr. Jefferson pode pedir descongelamento:** "descongela X para melhorar Y"

---

## 🔁 Trans-LLM — Canal Claude ↔ Antigravity

| Arquivo | Direção | Uso |
|---------|---------|-----|
| `claude_output.txt` | Claude → Antigravity | Instruções, comandos, pings |
| `antigravity_output.txt` | Antigravity → Claude | Logs, respostas, status |

Antigravity verifica `claude_output.txt` a cada **30 segundos** via `loop_monitor.py`.
