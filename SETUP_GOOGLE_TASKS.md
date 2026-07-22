# 🚀 SETUP COMPLETO — GOOGLE TASKS + MABIOS v4

**Data**: 2026-07-22  
**Sistema**: MABIOS v4 (Multi-Agent Basic Input/Output System)  
**Objetivo**: Unificar gerenciamento de tarefas jurídicas com alertas automáticos de prazo

---

## 📋 O QUE VOCÊ RECEBERÁ

### 1️⃣ **Gerenciador de Tarefas Google Tasks**
- ✅ 7 tarefas críticas (T001-T007) prontas para importar
- ✅ Integração com Google Calendar (datas automáticas)
- ✅ Sincronização desktop ↔ mobile
- ✅ Notificações automáticas 1 dia antes do prazo

### 2️⃣ **Sistema de Alertas MABIOS v4**
- ✅ Monitoramento diário de prazos (<3 dias = crítico)
- ✅ Alertas automáticos quando prazo vencer
- ✅ Histórico de tarefas em `sync_history.log`
- ✅ Integração com Trans-LLM para avisos

### 3️⃣ **Rastreamento de Tarefas Críticas**
- ✅ Documentação de T001, T002, T003 com checklists
- ✅ Status em tempo real de execução
- ✅ Próximas ações identificadas

---

## 🎯 PASSO A PASSO — IMPORTAÇÃO IMEDIATA

### **HOJE (22/07/2026) — 15 minutos**

```
1. Acesse: https://tasks.google.com
2. Clique em [+] para criar nova lista
3. Nomeie: "De Brito Advocacia — OAB/RO 2952"
4. Abra: tarefas_pronto_importacao/CHECKLIST_IMPORTACAO.md
5. Copie cada tarefa crítica e crie em Google Tasks:

   ☐ T001 — VIAGEM HUMAITÁ (31/07/2026)
   ☐ T002 — PROTOCOLAR PETIÇÃO RESCISÓRIA (25/07/2026)
   ☐ T003 — REUNIÃO COM CLIENTE BERNADETE (26/07/2026)
   ☐ T007 — CHECAR MANDADO PRISÃO (25/07/2026)

6. Para cada tarefa, configure:
   - Data vencimento (deadline)
   - Prioridade (High/Medium/Low)
   - Descrição (copiar do arquivo)
   - Notificação: 1 dia antes

7. ✅ PRONTO! Sistema sincronizado
```

---

## 🔧 INFRAESTRUTURA TÉCNICA

### **Arquivos Criados**

```
📁 agentes-de-advocacia-com-publicidade-em-grupos/
│
├── monitorar_google_tasks_mabios.py
│   └─ Script de monitoramento diário de prazos
│   └─ Envia alertas quando <3 dias
│   └─ Salva avisos em Inbox_Claude
│
├── importar_tarefas_google_tasks.py
│   └─ Gera CSV para importação em lote
│   └─ Exporta JSON com dados estruturados
│   └─ Cria checklist de verificação
│
├── ACOMPANHAMENTO_TAREFAS_CRITICAS.md
│   └─ Rastreamento de T001, T002, T003
│   └─ Checklists de execução por fase
│   └─ Notas e observações
│
├── SETUP_GOOGLE_TASKS.md ← Este arquivo
│   └─ Guia completo de implementação
│
└── tarefas_pronto_importacao/
    ├── CHECKLIST_IMPORTACAO.md
    ├── tarefas_google_tasks.csv
    └── tarefas_google_tasks.json
```

### **Como Funciona o Monitoramento**

```
Diariamente (05:00 UTC):
  ↓
loop_monitor.py ativa
  ↓
monitorar_google_tasks_mabios.py executa
  ↓
Verifica Google Tasks API
  ↓
Se prazo <3 dias → CRÍTICO
Se prazo <0 dias → VENCIDO
  ↓
Cria arquivo em Inbox_Claude
  ↓
Trans-LLM processa
  ↓
Aviso chega ao Dr. Jefferson
```

---

## 📊 TAREFAS CRÍTICAS — RESUMO EXECUTIVO

### **T001 — VIAGEM HUMAITÁ** 🚨
- **Prazo**: 31/07/2026 (9 dias)
- **Cliente**: Alexandre Marques de Campos
- **Processo**: 0609455-41.2023.8.04.4400
- **Ação Imediata**: Confirmar data com cliente
- **Checklist**: ACOMPANHAMENTO_TAREFAS_CRITICAS.md → T001

### **T002 — PROTOCOLAR PETIÇÃO RESCISÓRIA** 🚨⚠️
- **Prazo**: 25/07/2026 (3 DIAS - ULTRA URGENTE!)
- **Cliente**: Alexandre Marques de Campos  
- **Processo**: 0611311-40.2023.8.04.4400
- **Ação Imediata**: **PROTOCOLAR HOJE** no PJe
- **Checklist**: ACOMPANHAMENTO_TAREFAS_CRITICAS.md → T002

### **T003 — REUNIÃO BERNADETE** 🚨
- **Prazo**: 26/07/2026 (4 dias)
- **Cliente**: Bernadete da Silva Goveia
- **Processo**: 7012658-71.2025.8.22.0001 (Segredo de Justiça)
- **Ação Imediata**: Agendar reunião hoje
- **Checklist**: ACOMPANHAMENTO_TAREFAS_CRITICAS.md → T003

### **T007 — CHECAR MANDADO PRISÃO** 🚨
- **Prazo**: 25/07/2026 (3 dias)
- **Cliente**: Leandro Pereira Cardoso
- **Processo**: 7026053-67.2024.8.22.0001
- **Status**: DESATUALIZADO desde 23/05/2024
- **Ação Imediata**: Consultar hoje no PJe

---

## ✅ VERIFICAÇÃO PÓS-SETUP

Após importar as tarefas, verifique:

- [ ] Google Tasks acessível em https://tasks.google.com
- [ ] Lista "De Brito Advocacia — OAB/RO 2952" criada
- [ ] 7 tarefas críticas visíveis em Google Tasks
- [ ] Datas de vencimento aparecem em Google Calendar
- [ ] Notificações configuradas (1 dia antes)
- [ ] Acesso funciona em desktop + mobile
- [ ] Loop monitor rodando (verificar sync_history.log)
- [ ] Avisos chegando em Inbox_Claude

---

## 🔔 COMO RECEBER ALERTAS

### **Opção 1: Email (Recomendado)**
1. Configure notificações do Google Tasks para email
2. Alertas chegam automaticamente 1 dia antes

### **Opção 2: Desktop (Google Tasks app)**
1. Instale Google Tasks no seu computador
2. Ative notificações no Chrome/Edge

### **Opção 3: Mobile (Android/iOS)**
1. Instale Google Tasks
2. Sincroniza automaticamente com tarefas de desktop
3. Recebe push notifications

### **Opção 4: MABIOS v4 (Automático)**
1. Ativa monitoramento diário via loop_monitor.py
2. Envia avisos estruturados para Inbox_Claude
3. Gera histórico em sync_history.log

---

## 🚀 PRÓXIMAS FASES

### **Fase 1: HOJE (22/07)**
- [x] Criar Google Tasks
- [x] Importar 7 tarefas críticas
- [ ] **VOCÊ FAZER**: Acessar tasks.google.com e criar tarefas

### **Fase 2: SEMANA 1 (23-26/07)**
- [ ] T002: Protocolar petição (25/07)
- [ ] T007: Checar mandado (25/07)
- [ ] T003: Reunião Bernadete (26/07)
- [ ] T001: Viagem Humaitá (confirmação)

### **Fase 3: SEMANA 2 (27-31/07)**
- [ ] T004: Juntar custas Lilian (29/07)
- [ ] T005: Juntar termo revogação (29/07)
- [ ] T006: Verificar notas fiscais Aldemir (31/07)
- [ ] T001: Executar viagem Humaitá (se 31/07)

### **Fase 4: INTEGRAÇÃO COMPLETA**
- [ ] Sincronizar todos os 35 processos (não apenas críticos)
- [ ] Integrar email ↔ tarefas
- [ ] Configurar labels automáticos no Gmail
- [ ] Dashboard consolidado de andamentos

---

## 📞 SUPORTE

**Problemas Frequentes**:

❓ *Não consigo acessar tasks.google.com*
→ Verifique login Google, limpe cache do navegador

❓ *Datas não aparecem em Google Calendar*
→ Ative permissões do Google Tasks no Google Calendar

❓ *Não recebo notificações*
→ Verifique configurações de notificação em Conta Google → Segurança

❓ *Tarefas não sincronizam com mobile*
→ Force sincronização, desconecte/reconecte conta

**Contato Sistema**: Inbox_Claude (MABIOS v4)

---

## 📚 DOCUMENTAÇÃO RELACIONADA

- `ACOMPANHAMENTO_TAREFAS_CRITICAS.md` — Rastreamento de T001-T003
- `monitorar_google_tasks_mabios.py` — Script de monitoramento
- `importar_tarefas_google_tasks.py` — Script de importação
- `tarefas_pronto_importacao/` — Arquivos prontos para importar
- `/root/MABIOS/sync_history.log` — Histórico do watchdog

---

**Sistema Ativo**: ✅ MABIOS v4 Ready  
**Última Atualização**: 2026-07-22 22:50 UTC  
**Responsável**: Dr. Jefferson Silva de Brito + Claude CC-001
