# Sugestões para Antigravity — Próximas Fases

**Data**: 2026-07-04  
**Ramo**: `claude/automated-task-inventory-9zmzt8`  
**Contexto**: Importação de agente-dra-julia-advocacia do Drive; inventário de automações em produção

---

## 1. SEGURANÇA — Prioridade CRÍTICA

### 1.1 Credenciais Expostas em Plaintext
- **Arquivo**: `X/agente_andamentos/enviar_email.py` (linha 33)
  - Exposto: `SENHA = 'ezaxgwekapoiewpm'` (Gmail app password)
  - **Ação**: Revogar senha na [Google Account Security](https://myaccount.google.com/apppasswords), gerar nova, mover para `.env`

- **Arquivo**: `X/agente_andamentos/agente_andamentos.py`
  - Exposto: CNJ DataJud API keys (base64)
  - **Ação**: Rotacionar chaves no painel da API, armazenar em `.env` ou secrets manager

### 1.2 Auto-Execução de Código IA (Risco Arquitetural)
- **Arquivo**: `X/loop_monitor.py`
  - Comportamento: Monitora arquivos em busca de `[MABIOS]_ACTION:`, extrai `<commands>` e `<write_file>`, executa via `subprocess.run()`
  - Risco: Agentes IA podem ser manipulados (prompt injection) para gerar código malicioso que é auto-executado
  - **Mitigações Sugeridas**:
    1. Exigir validação humana antes de executar comandos (implementar fila de aprovação)
    2. Restringir `subprocess.run()` a whitelist de binários permitidos
    3. Executar em containerização isolada (Docker) com privilégios mínimos
    4. Adicionar logging detalhado e alertas para todo comando executado

---

## 2. ADAPTAÇÃO PARA "PUBLICIDADE EM GRUPOS"

### 2.1 Scope Original vs. Nova Proposta
- **Dra. Julia (atual)**: Chatbot 1:1 via WhatsApp Business API → responde consultas individuais
- **Nova proposta**: Postagem em grupos → múltiplas pessoas, conteúdo programado, sem resposta individual

### 2.2 Mudanças Arquiteturais Necessárias

#### a) Entrada de Dados
- **Atual**: Webhook WhatsApp recebe mensagens individuais → lógica de triagem
- **Novo**: Agendar postagens em grupos (horários, conteúdo, público-alvo)
  - Tabela SQL: `agendamentos_grupos` (grupo_id, conteúdo, horario_postagem, status)
  - Endpoint N8N: POST `/agendar-grupo` → valida conteúdo, agenda no banco

#### b) Processamento de Conteúdo
- **Atual**: Whisper + GPT-4o response individual
- **Novo**: Geração de conteúdo em batch:
  - Copilot marketing para resumir/reescrever posts (cabeça de vara, jurisprudência)
  - Verificação de compliance (ABNT, CPC, Lei de Publicidade)
  - Imagem/design via Canva (já integrado)

#### c) Publicação
- **Atual**: Resposta síncrona via WhatsApp
- **Novo**: Batch job (3x/dia?) postando em múltiplos grupos
  - Integration: Evolution API / Baileys para múltiplos números
  - Tracking: Reações, compartilhamentos, links clicados

### 2.3 Arquivo de Configuração Sugerido
```yaml
# config/grupos-publicidade.md
GRUPOS:
  - nome: "Advogados Rondônia"
    grupo_id: "120363xxx"
    horario_postagem: "09:00"
    categorias: ["trabalhista", "previdenciario"]
    
  - nome: "Coletivo Legal"
    grupo_id: "120363yyy"
    horario_postagem: "14:30"
    categorias: ["consumerista", "familia"]

TEMPLATES:
  - tipo: "jurisprudencia_semanal"
    frequencia: "segunda-feira"
    prompt: "Resuma 3 decisões importantes de..."
```

---

## 3. WORKFLOW N8N — Obter Versão Completa

### 3.1 Problema Atual
- Drive contém: `workflows/dra-julia-agente-ia-advocacia.json` (2 de 35 nós = resumo estrutural)
- Completo: [JeffersonMFti/agente-dra-julia-advocacia](https://github.com/JeffersonMFti/agente-dra-julia-advocacia)

### 3.2 Ação Necessária
1. Clonar repositório GitHub (ou fazer fork) → obter workflow .json de 35 nós
2. Extrair diferenciais:
   - Esquema de guardrails no webhook (está no resumo de 2 nós)
   - Fluxo completo de GPT-4o + Whisper + scheduling
   - Integração com Google Sheets/Calendar
3. Documentar deltas entre versão Drive (v1.0 bak) e GitHub (v2.0 atual)
4. Atualizar `ORIGEM-IMPORTACAO.md` com URL correta do workflow completo

### 3.3 Scripts Úteis
- `scripts/build_workflow_v2.py` — regenera JSON a partir de definições Python
- Usar como base para adaptar fluxo para "grupos" vs. "1:1"

---

## 4. INTEGRAÇÃO ARQUITETURAL

### 4.1 Três Sistemas em Paralelo
```
┌─────────────────────────────────────────────────────┐
│ X (Pasta de Produção)                               │
│ - economia.db (ledger, tarefas, vector_store)       │
│ - api_economia.py (FastAPI, CC-001 endpoints)       │
│ - agente_andamentos/ (CNJ DataJud, 7am daily job)  │
│ - loop_monitor.py (auto-executa comandos IA)        │
└─────────────────────────────────────────────────────┘
                        ↕ (sincronizam?)
┌─────────────────────────────────────────────────────┐
│ TESTE (Knowledge Base)                              │
│ - 2_brito_advocacia_triagem_e_precificacao/         │
│ - agente-dra-julia-advocacia/ (importado)           │
│ - Prompts, marketing_agent.py                       │
└─────────────────────────────────────────────────────┘
                        ↕ (herança?)
┌─────────────────────────────────────────────────────┐
│ agentes-de-advocacia-com-publicidade-em-grupos      │
│ (THIS REPO)                                         │
│ - Será a unificação: código + documentação          │
│ - Adaptado para GRUPOS (não 1:1)                   │
└─────────────────────────────────────────────────────┘
```

### 4.2 Perguntas para Elucidar
1. **Dados produção**: X/economia.db é a fonte de verdade? Sincroniza com TESTE?
2. **Agentes IA**: CC-001 (Claude), GA-002 (Gemini), WA-003 (WhatsApp) — rodam onde?
3. **Publicidade**: Deve herdar de TESTE/marketing_agent.py ou é nova?
4. **Deprecação**: X e TESTE são temporários enquanto este repo é expandido?

### 4.3 Sugestão de Estrutura Final
```
agentes-de-advocacia-com-publicidade-em-grupos/
├── agente-dra-julia-advocacia/        (template 1:1 — deprecado?)
├── agentes/                           (novos agentes IA)
│   ├── cc_001_claude.py               (heredado de X)
│   ├── ga_002_gemini.py               (heredado de X)
│   └── marketing_grupos.py            (nova adaptação)
├── integradores/                      (conectores)
│   ├── cnj_datajud.py                 (heredado)
│   ├── whatsapp_grupos.py             (novo)
│   └── google_sheets_sync.py          (heredado)
├── database/
│   ├── schema.sql                     (definição)
│   └── migrations/                    (histórico)
├── config/
│   ├── .env.example                   (credenciais seguras)
│   └── grupos-publicidade.yaml        (configuração grupos)
├── tests/                             (cobertura)
└── docs/
    ├── ARQUITETURA.md                 (diagrama completo)
    └── GUIA-MIGRACAO.md               (de X + TESTE para este repo)
```

---

## 5. TAREFAS IMEDIATAS (Orden de Prioridade)

### Fase 1: Segurança (Semana 1)
- [ ] Revogar Gmail app password `ezaxgwekapoiewpm`
- [ ] Rotacionar CNJ DataJud API keys
- [ ] Criar `.env.example` e migrar todas as credenciais
- [ ] Audit: grep -r "SENHA\|password\|api_key" em X/ para encontrar outras exposições

### Fase 2: Completude (Semana 1-2)
- [ ] Obter workflow N8N de 35 nós do GitHub JeffersonMFti
- [ ] Atualizar `workflows/dra-julia-agente-ia-advocacia.json` com versão completa
- [ ] Documentar deltas (v1.0 bak vs. v2.0)

### Fase 3: Adaptação (Semana 2-3)
- [ ] Desenhar arquitetura "publicidade em grupos" (novo diagrama)
- [ ] Criar tabelas SQL para agendamentos_grupos, tracking
- [ ] Novo endpoint N8N: POST `/agendar-grupo`
- [ ] Adaptar prompts de GPT-4o para conteúdo público (vs. consultório)

### Fase 4: Integração (Semana 3-4)
- [ ] Entender sincronização X ↔ TESTE ↔ agentes-de-advocacia
- [ ] Consolidar `economia.db` schema aqui
- [ ] Migrar agentes (CC-001, GA-002, marketing) para este repo

### Fase 5: Governança (Semana 4)
- [ ] Patch loop_monitor.py com validação humana + whitelist
- [ ] CI/CD: testes, linting, secret scanning
- [ ] CONTRIBUTING.md: padrão de commits, PRs, reviews

---

## 6. RISCOS E MITIGAÇÕES

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Credenciais ainda expostas em histórico git | Crítico | Force-push é risky; melhor: renovar senhas, adicionar ao `.gitignore`, usar secret scanning |
| Loop_monitor auto-executa código sem aprovação | Alto | Implementar fila + human-in-the-loop; whitelist de comandos |
| Workflow N8N de 2 nós não funciona isolado | Médio | Obter 35-node version; testar end-to-end em staging |
| Confusão de dados entre X, TESTE, repo | Médio | Documentar sincronização explícita; migrar único banco de dados |
| "Publicidade em grupos" é subespeificado | Alto | Entrevista: quantos grupos? conteúdo diário? monitoramento? |
| Escalabilidade de múltiplas postagens simultâneas | Médio | Use celery/RQ para fila; rate-limit WhatsApp API |

---

## 7. NOTAS PARA TRANSLLM

Quando passar contexto:
- Incluir este documento (`SUGESTOES-ANTIGRAVITY.md`)
- Incluir `INVENTARIO-AUTOMACOES.md` (visão geral de conectores)
- Incluir `ORIGEM-IMPORTACAO.md` (status de importação)
- Incluir este sumário de contexto (arquivo `.jsonl`)
- Credenciais expostas: `ezaxgwekapoiewpm` (Gmail) e CNJ keys (base64) — **REVOGUE IMEDIATAMENTE**
- Próximo agente: Focar em segurança primeiro (Fase 1), depois completude, depois design de "grupos"

---

**Fim de sugestões**

Documentação completa dos três sistemas (X, TESTE, repo) está pronta para exploração. Loop_monitor.py é a maior superficie de risco. Publicidade em grupos requer clarificação de requisitos antes de arquitetar.

Boa sorte! 🚀
