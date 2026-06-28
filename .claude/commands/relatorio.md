# /relatorio — Relatório elástico de processos

Gera relatório filtrado a partir de `documentos/processos.json`.

**Uso:** `/relatorio [filtro]`

**Filtros aceitos (pode combinar):**
- `/relatorio` → todos os ativos
- `/relatorio ariquemes` → comarca Ariquemes
- `/relatorio tjro` → tribunal TJRO
- `/relatorio jonair` → cliente/parte com "jonair"
- `/relatorio urgentes` → só urgentes/vencendo hoje
- `/relatorio 7057519` → número de processo (parcial)
- `/relatorio tudo` → inclui arquivados e conferidos

---

Ao receber este comando, leia `documentos/processos.json` e `documentos/tarefas.json`, aplique o filtro informado e apresente um relatório formatado com:

- Número do processo
- Classe e vara
- Partes (usar partes_datajud se disponível)
- Status e prazos pendentes
- Tarefas abertas vinculadas
- Observações/notas

Agrupe por tribunal/comarca. Mostre contagem total ao final.

Exclua status ARQUIVADO por padrão (exceto se filtro for "tudo").
