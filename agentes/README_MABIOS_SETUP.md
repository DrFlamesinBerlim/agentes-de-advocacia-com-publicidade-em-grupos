# 🏛️ MABIOS v3 — Setup Completo de Automações

**Dr. Jefferson Silva de Brito | OAB/RO 2952 | De Brito Advocacia**

---

## 📋 Componentes Implementados

### 1️⃣ **CC001_EmailMonitor.gs** — Relatórios + Alertas
- ✅ Relatório diário completo (7am)
- ✅ Alertas de alteração horários (quando há mudança em processos.json)
- ✅ Coluna de partes (autor/réu)
- ✅ Links clicáveis direto para PJe
- ✅ Resumo de saúde da carteira (críticos/altos/médios/baixos)

**Setup:**
```javascript
setupTriggers()  // Executar uma única vez
```

**Resultado:** 
- Email diário às 7h da manhã
- Alertas automáticos quando detecta mudanças

---

### 2️⃣ **CC001_PrazoAnalyzer.gs** — Análise de Prazos
- 🚨 Alerta de prazos críticos (≤3 dias)
- ⚠️ Alerta urgentes (≤7 dias)
- 🟠 Aviso de próximos (≤14 dias)
- Envia email apenas quando há críticos/urgentes

**Setup:**
```javascript
setupAnalisadorPrazos()  // Executar uma única vez
```

**Resultado:**
- Verifica prazos a cada hora
- Email com prazos em risco

---

### 3️⃣ **CC001_AgendaPlanner.gs** — Planejamento de Petições
- 📅 Sugere datas para protocolo (5 dias úteis antes do prazo)
- 📱 Cria eventos no Google Calendar
- Ordena por urgência

**Setup:**
```javascript
setupPlanificadorAgenda()  // Executar uma única vez
```

**Resultado:**
- Sugestões diárias de agenda (8h da manhã)
- Eventos criados no Google Calendar automaticamente

---

### 4️⃣ **CC001_PJeIngestor.gs** — Atualização de Andamentos (scraping, fallback)
- 🔄 Consulta PJe a cada 30 minutos
- Busca últimos andamentos de cada processo
- Atualiza processos.json no Google Drive
- Multi-estratégia (tentativa com fallback)

**Setup:**
```javascript
setupPJeIngestor()  // Executar uma única vez
```

**Limitações:** 
- PJe é uma SPA (React/Angular) — scraping por regex em HTML estático não captura a maioria dos processos
- Login com certificado digital + 2FA (app) não pode ser automatizado — é proposital, protege o sistema
- Recomendado usar **CC001_DataJudIntegration.gs** abaixo como fonte principal

---

### 5️⃣ **CC001_DataJudIntegration.gs** — Consulta Oficial CNJ (recomendado) ⭐
- 🏛️ Usa a **API pública DataJud do CNJ** — dados oficiais, sem login, sem certificado, sem 2FA
- Cobre processos **não sigilosos** do TJRO (e outros tribunais, trocando o alias)
- Atualiza `ultima_mov` e `mov_desc` automaticamente a cada 30 minutos
- Processos em segredo de justiça continuam exigindo consulta manual (esperado — é a lei)

**Obter API Key (gratuita, 2 minutos):**
1. Acesse https://datajud-wiki.cnj.jus.br/api-publica/acesso
2. Copie a APIKey pública divulgada pelo CNJ
3. No Apps Script, rode uma vez:
```javascript
setDataJudApiKey('SUA_CHAVE_AQUI')
```

**Setup:**
```javascript
setupDataJudIngestor()   // Executar uma única vez
```

**Teste:**
```javascript
testarDataJudIngestor()                          // Roda ingestão completa
testarConsultaUnicaDataJud('7070726-82.2023.8.22.0001')  // Testa 1 processo
```

---

## 🚀 Instalação Rápida (4 passos)

### Passo 1: Criar Projeto Apps Script
1. Acesse [script.google.com](https://script.google.com)
2. Novo projeto → Salve como "CC001_MABIOS"

### Passo 2: Colar Código
Cole **TODOS OS 7 SCRIPTS** neste único projeto (cada um em um arquivo `.gs` novo):
1. `CC001_EmailMonitor.gs`
2. `CC001_PrazoAnalyzer.gs`
3. `CC001_AgendaPlanner.gs`
4. `CC001_PJeIngestor.gs` (legado/fallback — scraping, limitado)
5. `CC001_DataJudIntegration.gs` ⭐ (recomendado — API oficial CNJ)
6. `CC001_ErrorHandler.gs` (alerta por email se alguma automação falhar)
7. `CC001_MasterSetup.gs` (instala/testa tudo com 2 chamadas)

### Passo 3: Configurar a API Key do DataJud
1. Copie a APIKey pública em https://datajud-wiki.cnj.jus.br/api-publica/acesso
2. No editor, selecione a função `setDataJudApiKey`, cole a chave no corpo temporariamente ou rode via console:
```javascript
setDataJudApiKey('SUA_CHAVE_AQUI')
```

### Passo 4: Instalar e Testar Tudo
Só duas funções — o `CC001_MasterSetup.gs` cuida do resto:
```javascript
instalarTudoMABIOS()   // Ativa todos os gatilhos permanentes de uma vez
testarTudoMABIOS()     // Dispara todos os testes agora — emails chegam na hora
```

**⚠️ IMPORTANTE:** Na primeira execução, o Google pedirá autorização para:
- Acessar Gmail (enviar relatórios)
- Acessar Google Drive (ler/gravar processos.json)
- Acessar Google Calendar (criar eventos)
- Fazer chamadas externas (UrlFetchApp, para consultar o DataJud)

Clique "Revisar permissões" → sua conta → "Avançado" → "Ir para CC001" → "Permitir"

Depois disso, se **qualquer** automação falhar no futuro (silenciosamente, num trigger agendado), você recebe um email `🔴 [CC-001] Falha em automação` explicando o que quebrou — nunca mais falha invisível.

---

## 📊 Como Funciona

```
FLUXO DIÁRIO:

08:00 → Planejador de Agenda gera sugestões → Email + Calendar
├─ Verifica prazos próximos
├─ Sugere datas para protocolo (5 dias úteis antes)
└─ Cria eventos no calendário

A cada 30 min → PJe Ingestor consulta andamentos
├─ Busca últimos movimentos
├─ Atualiza processos.json no Drive
└─ Se houver mudança → Email Monitor detecta

A cada 1 hora → Prazos Analyzer verifica criticalidade
├─ Se crítico/urgente → Email de alerta imediato
└─ Classifica risco (crítico/alto/médio/baixo)

19:00 → (ou horário configurado) Email Monitor envia relatório diário
├─ Listagem completa de todos os processos
├─ Agrupados por status (urgentes, ativos, paralisados, antigos)
├─ Com links diretos ao PJe
├─ Mostra partes (autor/réu)
└─ Resumo de saúde da carteira
```

---

## 🔧 Configurações Importantes

### Alterar horário do relatório diário
Em `CC001_EmailMonitor.gs`, procure:
```javascript
const CONFIG = {
  ...
  HORA_RELATORIO_DIARIO: 7,  // Mudar para 14 = 2pm, 19 = 7pm
  ...
}
```

### Alterar dias de alerta de prazo
Em `CC001_PrazoAnalyzer.gs`:
```javascript
const CONFIG_PRAZO = {
  DIAS_ALERTA_CRITICO: 3,    // Alertar 3 dias antes
  DIAS_ALERTA_URGENTE: 7,    // Alertar 7 dias antes
  DIAS_ALERTA_NORMAL: 14,    // Alertar 14 dias antes
}
```

### Alterar frequência de verificação do PJe
Em `CC001_PJeIngestor.gs`, função `setupPJeIngestor()`:
```javascript
.everyMinutes(30)  // Mudar para 15, 60, 180, etc.
```

---

## 📈 Qualidade de Dados

### Campo `processos.json` necessário:
```json
{
  "numero": "7070726-82.2023.8.22.0001",
  "cliente": "Nome do Cliente",
  "partes": "Autor vs Réu",
  "ultima_mov": "28/06/2026",
  "mov_desc": "Descrição da movimentação",
  "prioritario": true,
  "prazo_calculado": {
    "urgente": false,
    "data_prazo_final": "03/07/2026",
    "descricao": "Manifestação nos autos",
    "acao": "Protocolar resposta"
  }
}
```

Se algum campo faltar, os relatórios adaptam (mostram "—").

---

## 🧪 Testar Antes de Produção

```javascript
// Teste cada componente:

// 1. Email Monitor
testarRelatorioDiario()    // Envia relatório agora
testarMonitoramento()       // Força detecção de mudanças

// 2. Prazo Analyzer
testarAnalisadorPrazos()    // Verifica prazos agora

// 3. Agenda Planner
testarPlanificadorAgenda()  // Gera sugestões agora

// 4. PJe Ingestor
testarIngestor()            // Consulta PJe agora
testarLoginPJe()            // Testa autenticação
```

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Email não chega | Verificar spam, confirmar email em CONFIG |
| processos.json não atualiza | PJe pode estar protegido; tentar modo manual |
| Calendário não cria eventos | Verificar permissão de acesso ao Google Calendar |
| Relatório vazio | Verificar se processos.json tem dados válidos |
| Erro de autenticação | Executar setup novamente, revogar permissões, refazer |

---

## 📞 Logs & Debugging

Abra **Apps Script → Executar → Ver logs** para:
- Erros de conexão
- Dados sendo processados
- Status de cada função

Logs preservam últimas 24h de execução.

---

## ✅ Checklist de Instalação

- [ ] Projeto criado em script.google.com
- [ ] 4 scripts colados no projeto
- [ ] `setupTriggers()` executado
- [ ] `setupAnalisadorPrazos()` executado
- [ ] `setupPlanificadorAgenda()` executado
- [ ] `setupPJeIngestor()` executado
- [ ] Permissões OAuth autorizadas
- [ ] Testes manuais passaram
- [ ] Relatório chegou no email esperado
- [ ] Google Calendar conectado (opcional)

---

## 🎯 Próximas Melhorias

- [ ] Integração com API pública do tribunal (quando disponível)
- [ ] Dashboard web (Google Sheets/Data Studio)
- [ ] Webhooks para WhatsApp (WA-003)
- [ ] Machine learning para previsão de prazos
- [ ] Integração com Projuris/Astrea (se houver)

---

**Criado por: CC-001 (Claude Cowork) | MABIOS v3**
**Data: 28/06/2026 | Atualizado: Versão com ingestão + análise + agendamento**
