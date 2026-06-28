# /partes — Buscar e garantir nome das partes em todos os processos

**Uso:** `/partes [NUMERO_PROCESSO]`
**Sem argumento:** varre TODOS os processos sem partes
**Com número:** busca apenas aquele processo

---

## REGRA CANÔNICA (CLAUDE.md Regra #1)

Todo processo DEVE ter `partes.autor` e `partes.reu` preenchidos.
Número sozinho não serve — Dr. Jefferson reconhece processos por nome, não por número.
Campo vazio aciona busca automática imediata.

---

## Pipeline de busca — executar nesta ordem exata

### FONTE 1 — Relatórios Gmail (mais rico, já existe)

Buscar threads com subject:
- `[MABIOS v3] Relatório OAB de Partes e Causas Não Arquivadas`
- `[DE BRITO ADV]`
- `[MABIOS v3] Relatório de Inatividade`

Usar `mcp__Gmail__search_threads` + `mcp__Gmail__get_thread` para ler o corpo.
O relatório OAB lista todos os processos com `Cliente/Parte` — extrair por regex do número.

### FONTE 2 — DataJud CNJ (cloud-safe, já temos chave)

```python
POST https://api-publica.datajud.cnj.jus.br/api_publica_{tribunal}/_search
Authorization: ApiKey cDZHYzlZa0JadVREZDJCendFbXNwWnA6MusICgs4R14wMWI1ZUp1ZmQ5djVncw==
{"query": {"match": {"numeroProcesso": "NUMERO"}}, "size": 1}
```
Extrai `_source.partes[]` → separa polo ativo (autor) e passivo (réu).
Funciona para todos os tribunais em TRIBUNAL_MAP.

### FONTE 3 — Escavador por OAB (requer ESCAVADOR_API_KEY)

SDK Python oficial: `pip install escavador`
```python
import escavador; escavador.config(API_KEY)
from escavador.v2 import Processo
_, processos = Processo.por_oab(numero=2952, estado="RO")
# filtra pelo número CNJ
```
Busca todos os processos do OAB/RO 2952 e filtra pelo número.
Adicionar `ESCAVADOR_API_KEY` no `config/.env`.

API direta v1 (sem SDK):
```
GET https://api.escavador.com/api/v1/processos/numero_cnj?numero=NUMERO
Authorization: Bearer {ESCAVADOR_API_KEY}
```

### FONTE 4 — DJEs / Diários Oficiais (Gmail)

Buscar no Gmail por `"NUMERO_PROCESSO" newer_than:365d` — e-mails do PJe,
TRF, DJE geralmente contêm o nome das partes no corpo.
Usar `mcp__Gmail__get_thread` para ler corpo completo.

### FONTE 5 — Google Drive (documentos do cliente)

```
mcp__Google_Drive__search_files query: "NUMERO_PROCESSO"
```
Procurar em petições, contratos, procurações — cabeçalhos têm nome das partes.

### FONTE 6 — JusBrasil (busca pública)

Usar `WebSearch` com query: `"NUMERO_PROCESSO" site:jusbrasil.com.br`
Usar `WebFetch` para extrair partes da página pública.

### FONTE 7 — Portal do tribunal (busca pública)

Identificar tribunal pelo número:
- `.8.22.` → TJRO: `https://pje.tjro.jus.br`
- `.8.04.` → TJAM: `https://projudi.tjam.jus.br`
- `.4.01.` → TRF-1: `https://pje.trf1.jus.br`
- `.4.03.` → TRF-3/SP: `https://pje.trf3.jus.br`
- `.8.22.0000` → processo de número 0xxxxxxx = criminal especial TJRO

Usar `WebFetch` para consultar página pública e extrair partes.

### FONTE 8 — Perguntar ao Dr. Jefferson

Último recurso. Informar:
> "Não encontrei as partes do processo NUMERO × TRIBUNAL em nenhuma fonte
> (Gmail, DataJud, Escavador, Drive, JusBrasil, portal). Você sabe o nome?"

---

## Módulo Python para Antigravity

`agente_andamentos/modulo_partes_web.py`
```powershell
# Preenche todos os processos sem partes
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_partes_web.py"

# Busca um processo específico
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_partes_web.py" 7054209-31.2025.8.22.0001
```

Requer no `config/.env`:
```
ESCAVADOR_API_KEY=seu_token_aqui
```
Obter token em: https://api.escavador.com/tokens

---

## Integração com relatórios automáticos

O Antigravity já envia relatórios com partes por e-mail (`[MABIOS v3]`).
A cada execução do `/partes`, verificar primeiro esses e-mails antes de
fazer chamadas externas — é a fonte mais completa e gratuita.

---

## Formato de atualização em processos.json

```json
"partes": {
  "autor": "NOME COMPLETO DO AUTOR EM MAIÚSCULAS",
  "reu": "NOME COMPLETO DO RÉU EM MAIÚSCULAS",
  "advogado_reu": "Dr. Jefferson De Brito — OAB/RO 2952",
  "fonte_partes": "DataJud | Escavador | Relatório Gmail | JusBrasil | Drive"
}
```

---

## Processos ainda sem partes (28/06/2026)

| Processo | Tribunal | Situação |
|---|---|---|
| `0021230-05.2025.8.04.9001` | TJAM | Projudi AM — sem acesso cloud |
| `0001882-63.2014.8.22.0019` | TJRO — Machadinho | DataJud local |
| `0611311-40.2023.8.04.4400` | TJAM | "Alexandre" — Dr. Jefferson sabe |
| `7023346-63.2023.8.22.0001` | TJRO | DataJud local |
| `4000311-20.2022.8.22.0015` | TJRO — Vilhena | DataJud local |
| `4000536-43.2022.8.22.0014` | TJRO — Vilhena | DataJud local |
| `7021493-48.2025.8.22.0001` | TJRO | "Nome de quem?" — aguarda Dr. Jefferson |
| `7013265-84.2025.8.22.0001` | TJRO | DataJud local |
| `7007424-74.2026.8.22.0001` | TJRO | Relatório trouxe "319 2026" — inválido |
| `0000558-26.2018.8.22.0010` | TJRO — Rolim de Moura | Segredo de justiça |
| `0609455-41.2023.8.04.4400` | TJAM | DataJud local |
| `7002410-25.2021.8.22.0021` | TJRO — Buritis | DataJud local |
| `0010577-05.2020.8.22.0501` | TJRO | DataJud local |
