# 📝 DOSSIÊ OPERACIONAL & PIPELINE DE CASO
**Cliente:** [Nome Completo do Cliente]
**Tipo de Causa:** [Ex: Reclamatória Trabalhista, Cobrança Cível, Defesa Tributária]
**ID do Caso:** [EX: BRITO-001]
**Prazo Fatal:** YYYY-MM-DD

---

## 📂 1. MATERIAIS DE ENTRADA DISPONÍVEIS
*Documentos e mídias salvos na pasta `02_Fatos_e_Provas/`:*
- [ ] Documento 01: [Ex: RG, CPF, Comprovante de Residência]
- [ ] Documento 02: [Ex: CTPS, Holerites, Contrato Social]
- [ ] Documento 03: [Ex: Áudio com depoimento inicial gravado]
- [ ] Documento 04: [Ex: Prints de conversas de WhatsApp]

---

## 🎯 2. TESE CENTRAL & ESTRATÉGIA DE AÇÃO
*Breve resumo do que buscamos provar ou obter no processo:*
* 

---

## ⚡ 3. PIPELINE DE EXECUÇÃO (Fluxo X)

### 1️⃣ TAREFA-001 [PESADO] (Antigravity)
* **Status:** PENDENTE
* **Ação:** 
  1. Analisar todos os materiais de entrada na pasta `02_Fatos_e_Provas/`.
  2. Gerar a **Linha do Tempo Fática** exata das ocorrências em `03_Linha_do_Tempo/linha_do_tempo.md`.
  3. Mapear inconsistências ou contradições nos depoimentos/documentos.
  4. Realizar busca de Jurisprudência Exata (STJ, STF ou Tribunal local correspondente) com ementas e numeração de recursos reais, salvando na pasta `03_JURISPRUDENCIA_E_MODELOS/02_Jurisprudencia_Relevante/`.
* **Saída Esperada:** 
  - `linha_do_tempo.md` na pasta do cliente.
  - `jurisprudencia_selecionada.md` na pasta do cliente.
* **Próximo Desbloqueador:** Desbloqueia Tarefa-002.

---

### 2️⃣ TAREFA-002 [SÍNTESE] (Claude)
* **Status:** BLOQUEADO (aguarda Tarefa-001)
* **Ação:**
  1. Coletar a linha do tempo e a jurisprudência mapeadas por Antigravity na Tarefa-001.
  2. Mapear o modelo de petição aplicável na pasta `03_JURISPRUDENCIA_E_MODELOS/01_Modelos_Canônicos/`.
  3. Redigir o rascunho completo da peça jurídica (Petição Inicial, Recurso ou Contestação) sob a pasta `02_PECAS_E_RASCUNHOS/02_Revisão/` seguindo as premissas de **Anti-Alucinação** (sem menções legais vagas).
* **Saída Esperada:** 
  - `peca_revisada.md` (ou `.docx`) sob a pasta `02_PECAS_E_RASCUNHOS/02_Revisão/` (vinculada a este cliente).
* **Próximo Desbloqueador:** Desbloqueia Tarefa-003.

---

### 3️⃣ TAREFA-003 [DECISÃO] (VSI - Dr. Jefferson)
* **Status:** BLOQUEADO (aguarda Tarefa-002)
* **Ação:**
  1. Revisar a fundamentação fática e de direito da peça final produzida.
  2. Aplicar o veto/ajuste se necessário.
  3. Mover a versão aprovada para `02_PECAS_E_RASCUNHOS/03_Aprovadas/` e proceder com a assinatura e protocolo.
* **Saída Esperada:**
  - Decisão: **ACEITO** (Mover para pasta de Aprovadas) | **REVISAR** (Retornar para etapa relevante) | **EXPULSAR** (Quarentena).

---

## 📝 NOTAS DE ATUALIZAÇÃO & OBSERVATÓRIO
*(Área para anotações do advogado sobre reuniões, andamentos de audiências, etc.)*
* 
