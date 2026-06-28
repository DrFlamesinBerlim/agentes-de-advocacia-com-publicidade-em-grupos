# /mabios — Processar ação MABIOS em processo

Aplica uma ação MABIOS diretamente em processos.json sem precisar criar rascunho de e-mail.

**Uso:** `/mabios TIPO NUMERO_PROCESSO [observação]`

**Tipos disponíveis:**
| Tipo | Efeito |
|------|--------|
| CONFERIDO | Processo sai dos relatórios ativos (prazo cumprido) |
| ARQUIVAR | Arquiva definitivamente |
| ATIVO | Reativa processo arquivado/conferido |
| URGENTE | Eleva prioridade das tarefas do processo |
| NOTA | Adiciona nota ao processo |
| CONCLUIR | Conclui tarefa (ex: T-001) |

**Exemplos:**
- `/mabios CONFERIDO 7057519`
- `/mabios ARQUIVAR 7032508`
- `/mabios URGENTE 7013265 audiência amanhã`
- `/mabios NOTA 7077392 cliente ligou pedindo prazo`
- `/mabios CONCLUIR T-001`

---

Ao receber este comando, aplique a ação diretamente em `documentos/processos.json` ou `documentos/tarefas.json` conforme o tipo, registre em `antigravity_output.txt` e confirme o que foi feito.

Se o argumento não for fornecido, pergunte: tipo e número do processo.
