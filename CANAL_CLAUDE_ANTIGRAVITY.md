# 📡 CANAL DE COMUNICAÇÃO — CLAUDE ↔ ANTIGRAVITY
**De Brito Advocacia | Trans-LLM MABIOS V3**

> Este arquivo é a linha aberta entre os dois agentes.
> Claude escreve aqui o que precisa do Antigravity.
> Antigravity responde via `antigravity_output.txt` commitado no repo.

---

## 🔴 PENDÊNCIAS ABERTAS — Claude para Antigravity

### [PEND-001] Partes dos processos no DataJud
- **Status:** Aguardando Antigravity executar
- **Ação:** Rodar `modulo_partes_datajud.py` e commitar `processos.json` atualizado
- **Processos:**
  - `7002410-25.2021.8.22.0021` (TJRO Buritis)
  - `7054209-31.2025.8.22.0001` (TJRO Porto Velho)
  - `0021230-05.2025.8.04.9001` (TJAM)

### [PEND-002] Autenticação Google Calendar
- **Status:** Não autenticado na última sessão
- **Ação:** Rodar fluxo OAuth e salvar `token.json`
- **Impacto:** Prazos calculados não estão sendo sincronizados no Calendar

### [PEND-003] Inventário do que Antigravity instalou
- **Status:** Aguardando lista
- **Ação:** Antigravity commitar `INVENTARIO_INSTALACOES.md` com:
  - Pacotes pip instalados
  - Versões do Python/Chrome/drivers
  - Variáveis de ambiente configuradas
  - Caminhos dinâmicos usados nos scripts

### [PEND-004] Sync bidirecional via GitHub
- **Status:** `sync_github.py` criado — aguardando Antigravity rodar
- **Ação:** Executar `python agente_andamentos/sync_github.py` em paralelo com `loop_monitor.py`

---

## 🟢 O QUE CLAUDE PODE FAZER AGORA SEM ANTIGRAVITY

- Redigir qualquer peça jurídica (passe o número do processo + tipo de peça)
- Calcular prazos com base em andamentos colados aqui
- Escrever e versionar qualquer script no GitHub
- Analisar `processos.json` quando atualizado no repo
- Estruturar petições, recursos, manifestações, contratos

---

## 🔵 PROTOCOLO DE ATUALIZAÇÃO DESTE ARQUIVO

**Antigravity** atualiza a seção `PENDÊNCIAS` movendo itens para `RESOLVIDO` quando concluir.
**Claude** adiciona novas pendências quando identificar o que falta.

---

## ✅ RESOLVIDO

| ID | Tarefa | Resolvido em |
|----|--------|--------------|
| — | Estrutura da Pasta X criada via `setup_pasta_x.py` | 2026-06-23 |
| — | `PENDRIVE_MABIOS_V3.md` documentado | 2026-06-23 |
| — | `modulo_partes_datajud.py` criado | 2026-06-23 |
| — | `sync_github.py` criado — ponte bidirecional | 2026-06-23 |

---

## 📋 O QUE ANTIGRAVITY PRECISA COMMITAR NO REPO

Para Claude funcionar 100% sem depender de cola manual:

```
documentos/processos.json          ← atualizado com partes
documentos/prazos_pendentes.json   ← prazos calculados
antigravity_output.txt             ← status atual a cada ciclo
INVENTARIO_INSTALACOES.md          ← lista do que foi instalado
sync_state.json                    ← hash de paridade
```
