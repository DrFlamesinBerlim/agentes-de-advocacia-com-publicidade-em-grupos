# 🎯 CONTROLE DE MISSÕES — De Brito Advocacia
**Trans-LLM MABIOS V3 | Atualizado por: Claude_Síntese**

> Toda tarefa recebida entra aqui. Nenhuma missão se perde.
> Claude atualiza ao receber. Antigravity atualiza ao executar.

---

## 🔴 PENDENTE

| ID | Missão | Origem | Prioridade | Observações |
|----|--------|--------|------------|-------------|
| M-001 | Preencher partes dos 3 processos no DataJud | Antigravity | 🔴 URGENTE | Aguardando `modulo_partes_datajud.py` rodar |
| M-002 | Autenticar Google Calendar (OAuth) | Dr. Jefferson | 🔴 URGENTE | Prazos não estão sendo sincronizados |
| M-003 | Antigravity rodar `sync_github.py` | Dr. Jefferson | 🔴 URGENTE | Canal Claude↔Antigravity ainda não fechado |
| M-004 | Verificar emails que Antigravity está processando | Antigravity | 🟡 ALTA | Antigravity mencionou estar buscando emails |
| M-005 | Commitar inventário do que Antigravity instalou | Antigravity | 🟡 ALTA | `INVENTARIO_INSTALACOES.md` ausente no repo |
| M-006 | Manifestação TJAM 0021230-05.2025.8.04.9001 | Dr. Jefferson | 🔴 URGENTE | Prazo VENCE HOJE 23/06/2026 |

---

## 🟡 EM ANDAMENTO

| ID | Missão | Quem | Iniciado em | Status |
|----|--------|------|-------------|--------|
| M-007 | Sync bidirecional GitHub (sync_github.py) | Antigravity | 2026-06-23 | Processando... |

---

## ✅ CONCLUÍDO

| ID | Missão | Concluído em | Resultado |
|----|--------|-------------|-----------|
| C-001 | Criar `setup_pasta_x.py` | 2026-06-23 | ✅ No repo |
| C-002 | Criar `PENDRIVE_MABIOS_V3.md` | 2026-06-23 | ✅ No repo |
| C-003 | Criar `processos.json` com schema de partes | 2026-06-23 | ✅ No repo |
| C-004 | Criar `modulo_partes_datajud.py` | 2026-06-23 | ✅ No repo |
| C-005 | Criar `sync_github.py` (ponte bidirecional) | 2026-06-23 | ✅ No repo |
| C-006 | Criar `CANAL_CLAUDE_ANTIGRAVITY.md` | 2026-06-23 | ✅ No repo |
| C-007 | Criar `agente_andamentos.py` (orquestrador) | 2026-06-23 | ✅ No repo |
| C-008 | Criar `atualizar_processos.py` (pipeline) | 2026-06-23 | ✅ No repo |
| C-009 | Criar `modulo_prazos.py` | 2026-06-23 | ✅ No repo |
| C-010 | Criar `modulo_calendar.py` | 2026-06-23 | ✅ No repo |
| C-011 | Criar `prazos_pendentes.json` | 2026-06-23 | ✅ No repo |

---

## 📋 PROTOCOLO DE USO

- **Claude** adiciona missão quando recebe instrução do Dr. Jefferson
- **Antigravity** move para `EM ANDAMENTO` quando começa, e para `CONCLUÍDO` quando termina
- **ID format:** `M-XXX` (pendente/andamento) | `C-XXX` (concluído)
- **Prioridades:** 🔴 URGENTE | 🟡 ALTA | 🟢 NORMAL | ⚪ BAIXA
