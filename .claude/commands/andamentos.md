# /andamentos — Processar emails jurídicos e registrar andamentos

Varre a caixa de entrada (Gmail + Hotmail) por emails de Projudi, TRF-1, PJe, DJE e outros
sistemas judiciais, extrai movimentações e as registra diretamente em `documentos/processos.json`
e `documentos/prazos_pendentes.json` — sem intervenção manual.

**Uso:** `/andamentos [processo]`

- `/andamentos` → processa todos os emails jurídicos novos
- `/andamentos 7054209` → mostra andamentos de um processo específico

---

## O que faz automaticamente

1. **Varre Gmail inbox** — emails não lidos de remetentes judiciais (noreply@projudi, pje@tjro,
   trf1.jus.br, stj.jus.br, tjro.jus.br, tjam.jus.br, etc.)
2. **Extrai** número do processo, data, descrição do movimento, prazo em dias úteis
3. **Registra andamento** em `processos[].andamentos[]` do processo correspondente
4. **Calcula prazo** via `modulo_prazos.py` e salva em `prazos_pendentes.json`
5. **Cria tarefa** em `tarefas.json` se houver prazo identificado
6. **Marca email** com label `JURIDICO_PROCESSADO` para não reprocessar

## Fontes monitoradas

| Conta | Via | Sistemas |
|-------|-----|---------|
| flamesinberlim@gmail.com | OAuth | Projudi, TRF-1, PJe, DJE (todas contas redirecionam aqui) |
| advogadobrito@hotmail.com | IMAP | PJe, intimações TJRO |
| jeffersondebrito@hotmail.com | IMAP | DJE, avisos pessoais |

## Comando PowerShell (Antigravity)
```powershell
python "C:\Users\advog\Meu Drive\X\agente_andamentos\modulo_emails.py" andamentos
```

---

## Se o usuário pedir andamentos de um processo específico

Leia `documentos/processos.json`, filtre pelo número informado e mostre:

```
📂 [NUMERO]  [STATUS]
   Vara    : [vara] — [comarca]
   Partes  : [partes]

   ANDAMENTOS:
   [data] | [movimento]
            Prazo: [vencimento] [status_prazo]

   PRAZOS PENDENTES:
   [vencimento] — [tipo] — [status]

   TAREFAS ABERTAS:
   [id] [titulo] vence [data]
```

Se o processo não existir em processos.json, diga que ele não está no repositório GitHub
e que o Antigravity local pode tê-lo nos seus 63+ processos completos.

## Regras

- Nunca duplicar andamento com mesma data + mesmo trecho de movimento
- Manter no máximo 5 andamentos por processo (mais recentes primeiro)
- Prazo calculado via `modulo_prazos.py` — nunca inventar datas
- Se processo não existir em processos.json, criar entrada mínima com status ATIVO
