# /partes — Buscar nome das partes de um processo

**Uso:** `/partes NUMERO_PROCESSO`
**Exemplo:** `/partes 7054209-31.2025.8.22.0001`

---

## REGRA CANÔNICA

Todo processo DEVE ter nome das partes. Número sozinho não serve — o Dr. Jefferson não reconhece processos por número, e sim por nome das partes envolvidas.

Se `/partes` for invocado sem argumento, liste TODOS os processos com `partes.autor` ou `partes.reu` vazios.

---

## Sequência de busca obrigatória

Execute CADA etapa até encontrar o nome. Não pule etapas.

### 1. processos.json (local)
Ler `documentos/processos.json` e verificar se já existe `partes.autor` / `partes.reu`.
Se existir → mostrar e encerrar.

### 2. Gmail — buscar pelo número do processo
Usar `mcp__Gmail__search_threads` com query:
```
"NUMERO_PROCESSO" newer_than:365d
```
O corpo dos e-mails do PJe, TRF, DJE geralmente contém nome das partes.
Usar `mcp__Gmail__get_thread` para ler o corpo completo se necessário.

### 3. Google Drive — buscar documentos
Usar `mcp__Google_Drive__search_files` com o número do processo como query.
Procurar petições, contratos, procurações — os cabeçalhos têm as partes.

### 4. Internet — portal do tribunal
Com base no número do processo, identificar o tribunal:
- 7 dígitos + `8.22` = TJRO → `https://pje.tjro.jus.br`
- `8.04` = TJAM → `https://pje2.tjam.jus.br`
- `4.01` = TRF-1 → `https://pje.trf1.jus.br`
- `4.03` = TRF-3 (SP) → `https://pje.trf3.jus.br`

Usar `WebFetch` ou `WebSearch` para consultar o portal e extrair as partes da página pública.

### 5. Perguntar ao Dr. Jefferson
Se nenhuma fonte encontrou, informar:
> "Não encontrei as partes do processo NÚMERO em nenhuma fonte (processos.json, Gmail, Drive, portal do tribunal). Você sabe o nome do autor ou réu?"

---

## Ação após encontrar

1. Atualizar `processos.json` com os nomes encontrados (maiúsculas)
2. Confirmar: "Partes do processo NUMERO atualizadas: AUTOR × RÉU"
3. Se foi perguntado ao Dr. Jefferson → registrar a resposta e atualizar

---

## Listar todos sem partes (sem argumento)

Se `/partes` for chamado sem número:

1. Ler `processos.json`
2. Listar todos os processos onde `partes.autor == ""` ou `partes.reu == ""`
3. Para cada um, tentar busca automática (Gmail + Drive) em paralelo
4. Atualizar os que encontrar, listar os que precisam de resposta manual

**Formato da listagem:**
```
PROCESSOS SEM PARTES (X encontrados):

1. 7054209-31.2025.8.22.0001 | TJRO — 10ª Vara Cível | ATIVO
   → [buscando...]

2. 0021230-05.2025.8.04.9001 | TJAM — Des. Flávio Pascarelli | ATIVO
   → [buscando...]
```
