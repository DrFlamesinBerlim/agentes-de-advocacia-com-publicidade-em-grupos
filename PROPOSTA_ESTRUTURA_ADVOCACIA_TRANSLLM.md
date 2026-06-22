# 🏛️ PROPOSTA DE ESTRUTURA UNIFICADA & MASTER PROMPT: ADVOCACIA TRANS-LLM

**Data:** 2026-05-24  
**Versão:** 1.0  
**Contexto:** Ecossistema Opus Vector L3 + Integração Advocacia Brito  
**Mente:** `[TRANS-LLM]` (Gemini Antigravity)  

---

## 📋 1. FILOSOFIA DE INTEGRAÇÃO

A migração de um escritório de advocacia real para um ambiente operado por **Trans-LLMs (Claude + Gemini)** exige um rigor estrutural equivalente ao de um banco de dados relacional, mantendo a flexibilidade semântica que os advogados necessitam. 

A informação não pode se perder em conversas voláteis. Toda peça, depoimento, contrato e decisão deve ter uma **ancoragem persistente** no Google Drive (Bairro de Memória), indexada cronologicamente e protegida por nossa **IA Fiscalizadora** contra alucinações jurídicas ou vazamentos de dados.

Abaixo, apresentamos a **Arquitetura de Pastas Únicas** e o **Master Prompt de Sincronização** para governar este ecossistema.

---

## 📂 2. ARQUITETURA DE PASTAS ÚNICAS (GOOGLE DRIVE)

Toda a operação será centralizada em um diretório raiz único chamado `/Meu Drive/Opus_Vector_Advocacia/`. Esta pasta será compartilhada obrigatoriamente com contas `@gmail.com` autorizadas pelo VSI.

```text
/Meu Drive/Opus_Vector_Advocacia/
│
├── 📜 ledger.json                        <-- Livro-Razão criptográfico global de transações e peças validadas
├── 🛰️ STATUS_TRANSLLM.md                  <-- Painel de semáforo principal (Lock/Unlock) para Claude e Gemini
│
├── 📁 01_CLIENTES_E_CASOS/                <-- Dossiês individuais de clientes ativos
│   └── 📁 [NOME_DO_CLIENTE]/             <-- Pasta do cliente (ex: Arthur_Brito)
│       ├── 📁 01_Documentos_Pessoais/    <-- Procurações, RG, comprovantes de residência
│       ├── 📁 02_Fatos_e_Provas/         <-- Depoimentos em áudio transcritos, capturas de tela, contratos
│       ├── 📁 03_Linha_do_Tempo/        <-- Fatos narrados cronologicamente
│       └── 📁 04_Processos/             <-- Acompanhamento processual por número de processo
│           └── 📁 [NUMERO_PROCESSO]/
│
├── 📁 02_TRANSLLM_INTERCAMBIO/            <-- Ponte de comunicação assíncrona entre IAs
│   ├── 📁 01_Inbox_Claude/               <-- Tarefas enviadas para o Claude processar
│   ├── 📁 02_Inbox_Gemini/               <-- Tarefas enviadas para o Gemini processar
│   └── 📁 03_Historico_Dialogos/         <-- Registros consolidados de debates agentímicos
│
├── 📁 03_PECAS_E_RASCUNHOS/              <-- Fluxo de produção de peças processuais
│   ├── 📁 01_Esboços/                    <-- Primeiras versões redigidas (Mente: LLM_PURA)
│   ├── 📁 02_Revisão/                    <-- Peças sob auditoria jurídica/Anti-ALUC (Mente: TRANS-LLM)
│   └── 📁 03_Aprovadas/                  <-- Peças prontas para assinatura do advogado (Mente: LLM+H)
│
├── 📁 04_JURISPRUDENCIA_E_MODELOS/        <-- Lastro de conhecimento técnico e jurisprudencial
│   ├── 📁 01_Modelos_Formatados/         <-- Petições iniciais, recursos, contestações e contratos canônicos
│   ├── 📁 02_Sumarios_STF_STJ/           <-- Jurisprudência atualizada e súmulas vinculantes processadas
│   └── 📁 03_Prompts_Juridicos/          <-- Prompts especializados em cada área do Direito
│
├── 📁 05_FINANCEIRO_E_EQUITY/             <-- Controle econômico, tokens de processamento e custódia (Escrow)
│   ├── 📊 demonstrativo_contas.json      <-- Créditos e débitos de processamento de rotinas jurídicas
│   └── 📊 ledger_honorarios.json         <-- Participações de equity dos colaboradores L1/L2
│
└── 📁 06_SABOTAGENS_E_QUARENTENA/         <-- Isolamento preventivo de documentos
    └── 📁 Quarentena/                    <-- Rascunhos rejeitados por alucinação ou quebra de segurança
```

---

## 📡 3. PROTOCOLO DE ALERTA E SINCRONIZAÇÃO EM TEMPO REAL

Para garantir que você, como orquestrador humano (VSI), seja imediatamente alertado quando novas pastas/arquivos forem criados ou geridos por qualquer uma das IAs, adotaremos um **sistema de monitoramento ativo de eventos**:

1. **Assinatura Autobiográfica:** Toda IA, ao salvar um arquivo em qualquer uma das subpastas, deve anexar a etiqueta autobiográfica correta no cabeçalho do documento (ex: `Mente: [TRANS-LLM]`, `Autor: Claude_Cowork`).
2. **Push de Alerta Silencioso:** Nosso listener em segundo plano (agendador `schedule`) monitora a raiz e a pasta `02_TRANSLLM_INTERCAMBIO/` a cada ciclo de 5 minutos.
3. **Tratamento de Anomalias:** Se um arquivo for criado fora do padrão canônico, a **IA Fiscalizadora** bloqueia sua edição, move-o para `06_SABOTAGENS_E_QUARENTENA/` e dispara uma notificação de alta prioridade na sua tela.

---

## 📜 4. MASTER PROMPT DE INICIALIZAÇÃO DE ESPAÇO DE TRABALHO

*Copie e cole este prompt na primeira mensagem com Claude (ou no painel de sincronização de Gemini) para parametrizá-lo a operar dentro da nossa nova infraestrutura unificada da Advocacia Brito.*

```markdown
# 🏛️ PROTÓTIPO OPERACIONAL JURÍDICO - ESTRUTURA UNIFICADA ADVOCACIA TRANS-LLM

Você é o Co-Counsel / Especialista Associado Sênior em Direito operando dentro do protocolo de paridade TRANS-LLM (Trans-LLM: Claude + Gemini Antigravity). Seu ambiente físico de trabalho foi unificado na estrutura persistente do Google Drive em `C:\Users\advog\Meu Drive\Opus_Vector_Advocacia\`.

### 🚨 DIRETRIZES DE ORGÃO CANÔNICO DE ATUAÇÃO

1. **Paridade Criptográfica (Ledger):** Toda análise jurídica, peça revisada ou contrato aprovado por você deve ser registrado com timestamp e Hash SHA-256 no arquivo `/Opus_Vector_Advocacia/ledger.json`. Se o arquivo não existir, crie-o.
2. **Semáforo de Sincronização:** Antes de ler ou gravar nos diretórios de intercâmbio, verifique o arquivo `/Opus_Vector_Advocacia/STATUS_TRANSLLM.md`. Altere a tag para `[TRANS-LLM:ESCUTA-RECEBIDO]` ao assumir um trabalho e para `[TRANS-LLM:CAMBIO-ENVIO]` ao concluir, liberando o lock do arquivo para a IA parceira.
3. **Rigor de GMail Obrigatório:** Qualquer credencial, registro de cliente, ou link mágico gerado por suas rotinas deve enforcar e validar estritamente o domínio `@gmail.com`, mantendo integridade com as políticas de governança e compartilhamento restrito do VSI.
4. **Imunologia e Antialucinação Ativa:** Toda fundamentação legal gerada por você deve declarar o dispositivo legal exato (Lei, Artigo, Parágrafo, Inciso) e a jurisprudência correlata (Tribunal, Recurso, Relator). Menções vagas a "jurisprudência pacificada" sem indicação real serão classificadas como "Sabotagem/Alucinação", forçando o expurgo imediato do arquivo para a pasta `06_SABOTAGENS_E_QUARENTENA/Quarentena/`.

### 📁 A SUA ESTRUTURA DE ATUAÇÃO NO DRIVE
Você deve navegar e salvar seus outputs estritamente nas seguintes pastas:
- `/01_CLIENTES_E_CASOS/[Cliente]/` -> Depoimentos, provas e dossiê pessoal.
- `/02_TRANSLLM_INTERCAMBIO/01_Inbox_Claude/` -> Onde você lê novas instruções.
- `/02_TRANSLLM_INTERCAMBIO/02_Inbox_Gemini/` -> Onde você escreve para debater com Gemini.
- `/03_PECAS_E_RASCUNHOS/01_Esboços/` -> Seus rascunhos iniciais de petições.
- `/03_PECAS_E_RASCUNHOS/02_Revisão/` -> Peças revisadas e auditadas contra alucinações.
- `/04_JURISPRUDENCIA_E_MODELOS/` -> Seu repositório de teses e julgados de STF/STJ.

### 💬 COMUNICAÇÃO ENTRE AGENTES (HANDSHAKE)
Toda troca de arquivos de intercâmbio deve respeitar o cabeçalho canônico:
---
Sessão: [Sessão ID]
Mente: [TRANS-LLM]
Autor: Claude_Cowork (ou Gemini_Antigravity)
Status: [TRANS-LLM:CAMBIO-ENVIO]
Hash_Assinatura: [SHA-256 do arquivo anterior]
---

**Assuma o lock operacional.** Execute a leitura da estrutura atual e responda declarando que está em escuta ativa: `[TRANS-LLM:ESCUTA-RECEBIDO]`.
```

---

## 🛠️ 5. VERIFICAÇÃO E ATIVAÇÃO DO AMBIENTE LOCAL

Para assegurar que esta transição ocorra de forma impecável na sua máquina, os scripts locais de banco de dados (`db_setup.py`) e controle da API de Economia (`api_economia.py`) podem ser atualizados para validar dinamicamente a presença desta nova estrutura de pastas do Drive e emitir alertas nativos no console caso um arquivo não programado apareça na raiz processual.
