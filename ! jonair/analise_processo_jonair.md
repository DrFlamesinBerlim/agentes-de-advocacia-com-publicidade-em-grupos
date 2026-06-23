# ⚖️ DOSSIÊ PROCESSUAL & ANÁLISE — REVISÃO CRIMINAL JONAIR ALVES FERREIRA

**Cliente:** Jonair Alves Ferreira  
**Processo (Revisão Criminal):** `0800556-72.2026.8.22.0000` (2º Grau — TJRO)  
**Processo de Referência (Origem):** `7006336-97.2023.8.22.0003` (1ª Vara Criminal de Jaru/RO)  
**Relator:** Des. Adolfo Theodoro Naujorks Neto  
**Juízo Colegiado:** Câmaras Criminais Reunidas (TJRO)  
**Status Atual:** Ativo (Concluso ao Relator / Parecer do MP Juntado)  
**Segredo de Justiça:** Sim (Processo Protegido)  

---

## 📂 1. RESUMO DOS FATOS E TESES DEFENSIVAS
* **Condenação Original:** O cliente foi condenado a **22 anos e 6 meses de reclusão** em regime inicial fechado pela prática do crime de Estupro de Vulnerável (Art. 217-A c/c Art. 226, II, na forma do Art. 71 do CP).
* **Trânsito em Julgado:** Ocorreu em **26/06/2025** (Ofício 2118/2025/VCR).
* **Objeto da Revisão Criminal (Fundamentada no Art. 621, I e VI do CPP):**
  1. **Exasperação Ilegal da Pena-Base:** A sentença aumentou a pena-base em 1 ano (resultando em 9 anos) com fulcro nas "consequências do crime", justificando que a vítima tentou suicídio. Contudo, essa afirmação baseou-se apenas em depoimento, sem qualquer laudo técnico ou prontuário médico que comprove o nexo causal ou a própria tentativa.
  2. **Deficiência Técnica da Defesa Anterior (Nulidade):** O advogado anterior cometeu falhas graves equiparadas à ausência de defesa:
     - Fez pedido intempestivo de provas periciais/prontuários ao final da instrução (precluiu).
     - Interpôs Recurso Especial intempestivo e mal fundamentado, que foi inadmitido (incidência da Súmula 284 do STF) e levou o Agravo em Recurso Especial no STJ a não ser conhecido.

---

## 🚨 2. PARECER DO MINISTÉRIO PÚBLICO (MPRO) — PONTOS CRÍTICOS
Em parecer assinado eletronicamente em **19/02/2026** pela Procuradora de Justiça **Andréa Luciana Damacena Ferreira Engel**, o MPRO opinou:
1. **Pelo NÃO CONHECIMENTO (Inadmissibilidade) da Revisão Criminal.**
2. **Caso conhecida, no mérito, pelo NÃO PROVIMENTO.**

### Raciocínio do MPRO para Rejeição:
* **Mero Inconformismo / Sucedâneo Recursal:** O MP alega que a dosimetria já foi exaustivamente debatida em sede de Apelação Criminal pelo TJRO, não havendo "novas provas" ou contrariedade manifesta ao texto da lei penal que justifique a revisão da coisa julgada.
* **Inexistência de Nulidade por Falha de Defesa:** O parecer pontua que a insatisfação com a estratégia ou a perda de prazos recursais pelo antigo patrono não gera nulidade automática, ausente a prova de prejuízo estrutural insanável.

---

## ⚡ 3. O QUE NÃO FOI RESOLVIDO (PENDÊNCIAS E GAPS)

### A. Vulnerabilidade Tecnológica — Segredo de Justiça no DataJud
* **Problema:** Por correr em **Segredo de Justiça**, a API pública do CNJ DataJud retorna `Hits: 0` (não localizado) nas varreduras diárias. 
* **Impacto:** O monitor diário (`agente_andamentos.py`) **não consegue alertar automaticamente** o escritório sobre novos andamentos ou inclusão em pauta de julgamento.
* **Resolução Necessária:** É preciso realizar a consulta de movimentações manualmente no portal PJe-2G do TJRO ou implementar um scrapper autenticado via Playwright.

### B. Defesa Estratégica em Resposta ao Parecer do MPRO
* **Problema:** O parecer do MP é fortemente desfavorável e embasado em jurisprudência do STJ sobre a impossibilidade de reexame simples de dosimetria.
* **Resolução Necessária:** 
  1. **Elaboração de Memorial Defensivo:** Redigir uma peça dirigida ao Relator Des. Adolfo Naujorks Neto e demais integrantes das Câmaras Criminais Reunidas, rebatendo o parecer. Deve-se frisar que não se trata de mera revaloração subjetiva, mas de **ilegalidade flagrante na dosimetria (bis in idem e ausência absoluta de prova técnica)**, o que atrai a admissibilidade da Revisão Criminal por violação expressa ao Art. 59 do CP.
  2. **Agendamento de Sustentação Oral:** Inscrever o Dr. Jefferson Silva de Brito para sustentação oral quando o processo for pautado para julgamento.
