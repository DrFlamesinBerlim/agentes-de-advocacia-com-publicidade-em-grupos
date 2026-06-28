# CLAUDE.md — Regras Canônicas | De Brito Advocacia MABIOS V3
**Dr. Jefferson Silva de Brito | OAB/RO 2952 | Porto Velho/RO**

---

## REGRA #1 — TODO PROCESSO TEM QUE TER NOME DAS PARTES

Esta é a regra mais importante do sistema. **Números de processo sozinhos são inúteis para o Dr. Jefferson.**

### Obrigação
Toda entrada em `processos.json` DEVE ter `partes.autor` e `partes.reu` preenchidos com nomes reais.
Campo vazio, `""`, `"—"` ou `"desconhecido"` é **inaceitável** — aciona busca imediata.

### Ordem de busca (executar nesta sequência)

1. **DataJud CNJ** — `modulo_partes_datajud.py` (roda no Antigravity local)
2. **Google Drive** — buscar na pasta do cliente por petições, contratos, procurações
3. **Gmail** — buscar e-mails com o número do processo; o corpo geralmente tem nome das partes
4. **Internet** — consultar diretamente o portal do tribunal (PJe, eSAJ, Projudi, TRF1 etc.)
5. **Perguntar ao Dr. Jefferson** — última opção; incluir o número e pedir o nome

### Formato obrigatório em processos.json
```json
"partes": {
  "autor": "NOME COMPLETO DO AUTOR (maiúsculas)",
  "reu": "NOME COMPLETO DO RÉU (maiúsculas)",
  "advogado_reu": "Dr. Jefferson De Brito — OAB/RO 2952"
}
```

### Em relatórios e respostas
**NUNCA** mencionar apenas o número. Sempre usar o formato:
> `NÚMERO | AUTOR × RÉU | Tribunal — Vara`

Exemplo correto:
> `7057519-45.2025.8.22.0001 | ALESSANDRA VIEIRA LEMOS × HENRIQUE LUCAS ASSUNCAO DE AMORIM | TJRO — 2ª Turma Recursal`

---

## REGRA #2 — NUNCA CRIAR ARQUIVOS DUPLICADOS

- Editar o original. Nunca criar `modulo_emails_v2.py`, `loop_monitor_novo.py` etc.
- Módulos FROZEN (listados em `FROZEN.md`) só podem ser alterados com autorização explícita.

## REGRA #3 — SEGURANÇA

- `.env`, `credentials.json`, `token.json` NUNCA commitados no git.
- Senhas apenas no `.env` local do Antigravity.
- Dados processuais reais: anonimizar em exemplos públicos.

## REGRA #4 — PROTOCOLO TRANS-LLM

- `claude_output.txt` → Claude escreve instruções XML para o Antigravity
- `antigravity_output.txt` → Antigravity responde com logs
- Antigravity verifica a cada 30s via `loop_monitor.py`

## REGRA #5 — IDENTIFICAÇÃO DE PROCESSOS

Ao citar qualquer processo, sempre usar:
`NÚMERO | PARTES | TRIBUNAL | STATUS`

Se as partes não estiverem na base → executar a skill `/partes NUMERO` antes de responder.

---

## Módulos FROZEN — não modificar sem autorização

Ver `FROZEN.md` para lista completa. Os principais:
- `modulo_prazos.py` — lógica jurídica validada
- `modulo_mabios_email.py` — MABIOS OAuth testado
- `modulo_relatorios.py` — relatórios validados
- `loop_monitor.py` — daemon principal
- `sync_github.py` — sync GitHub

## Skills disponíveis

| Skill | Uso |
|---|---|
| `/partes NUMERO` | Busca nome das partes em todas as fontes |
| `/andamentos` | Processa e-mails jurídicos e registra andamentos |
| `/mabios TIPO NUMERO` | Aplica ação MABIOS |
| `/relatorio [filtro]` | Relatório por comarca/tribunal/cliente |
| `/status` | Painel rápido do escritório |
| `/sync` | Sincroniza GitHub |
| `/powershell` | Comandos prontos para o terminal Windows |
