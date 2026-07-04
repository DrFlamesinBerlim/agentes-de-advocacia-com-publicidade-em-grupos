# /tarefas — Gestão automática de tarefas jurídicas

**Uso:** `/tarefas [comando] [argumento]`

---

## MODOS

| Comando | O que faz |
|---------|-----------|
| `/tarefas` (vazio) | Lista todas as tarefas abertas e em andamento |
| `/tarefas urgentes` | Mostra SÓ as urgentes ou vencendo em até 2 dias |
| `/tarefas nova` | Assistente interativo para criar tarefa nova |
| `/tarefas concluir T-001` | Marca tarefa T-001 como CONCLUÍDA |
| `/tarefas processo 7054209` | Mostra tarefas apenas do processo 7054209 |
| `/tarefas status` | Painel rápido com contagem |

---

## TIPOS DE TAREFA SUPORTADOS

- 🔴 **PRAZO_FATAL** — inscrição sustentação oral, contestação, recurso
- 🟡 **PRAZO_NORMAL** — manifestação, petição, juntada
- ⚖️ **SESSAO** — sessão de julgamento presencial ou eletrônica
- 🏛️ **AUDIENCIA** — audiência marcada
- 📝 **PEÇA_JURIDICA** — peça a redigir (memorial, embargos, agravo)
- 📋 **DILIGENCIA** — diligência a cumprir (citar, intimar, expedir)
- 👁️ **MONITORAMENTO** — acompanhar sem prazo imediato
- ⬆️ **RECURSO** — recurso a interpor após decisão

---

## PRIORIDADES

- 🔴 **URGENTE** — ação imediata (< 24h)
- 🟡 **ALTA** — até 7 dias
- 🟢 **NORMAL** — até 30 dias
- ⚪ **BAIXA** — sem pressa

---

## FLUXO AUTOMÁTICO

A cada **30 segundos**, o `loop_monitor.py` executa:
```python
python modulo_tarefas.py urgentes
```

Resultado aparece em:
- `antigravity_output.txt` — log automático
- `/status` — painel geral do escritório
- GitHub — sincronizado

Se houver tarefas vencidas ou vencendo hoje, aparece em **VERMELHO** 🔴.

---

## EXEMPLOS PRÁTICOS

### Listar todas abertas
```
/tarefas
```

(Exemplo com dados reais do escritório — veja acima formato dos retornos)

**Retorna:**
```
  [T-001] Sustentação Oral — 7000001
     Processo : 7000001-00.XXXX.8.22.0001 | TJRO
     Partes   : CLIENTE_AUTOR × CLIENTE_RÉU
     Tipo     : PRAZO_FATAL | Prioridade: URGENTE
     Prazo    : 2026-06-30 🔴 VENCE HOJE
     Ação     : Enviar e-mail para tribunal

  [T-002] Memorial Defensivo — 7000002
     Processo : 7000002-00.XXXX.8.22.0000 | TJRO
     Partes   : MINISTÉRIO PÚBLICO × CLIENTE_DEFESA
     Tipo     : PEÇA_JURIDICA | Prioridade: URGENTE
     Prazo    : 2026-07-15 🔴 12d restante(s)
```

### Ver só as urgentes
```
/tarefas urgentes
```

### Criar nova tarefa
```
/tarefas nova
```

**Assistente interativo:**
```
=== NOVA TAREFA ===
Número do processo: 7000003-00.XXXX.8.22.0001
Tribunal (TJRO/TJAM/STJ...): TJRO
Classe processual: Ação Ordinária Cível
Partes (resumido): CLIENTE_AUTOR × CLIENTE_RÉU
Título da tarefa: Peça jurídica a redigir
Descrição detalhada: Contestação ao mérito
Tipo: PEÇA_JURIDICA
Vencimento (AAAA-MM-DD ou Enter para sem prazo): 2026-07-15
Prioridade (URGENTE/ALTA/NORMAL/BAIXA): ALTA
Ação necessária: REDIGIR CONTESTAÇÃO 5 PÁGINAS
Destinatário (e-mail ou Enter): advogado@email.com
Link pasta cliente (ou Enter): https://drive.google.com/...
Notas adicionais (ou Enter): Cliente enviou cronologia dos fatos
Origem (DJE/PJe/WhatsApp/Manual): Manual

✅ Tarefa T-003 criada: Peça jurídica a redigir
```

### Marcar tarefa concluída
```
/tarefas concluir T-001
```

**Resultado:**
```
✅ Tarefa T-001 marcada como CONCLUÍDA.

[atualizado_em: 2026-07-04T14:30:00Z]
```

Tarefa desaparece dos relatórios de abertas, mas fica no histórico.

### Tarefas de um processo
```
/tarefas processo 7000001
```

**Retorna apenas as tarefas daquele processo.**

---

## INTEGRAÇÃO COM OUTROS SISTEMAS

### 1. **Skill `/status`** — painel geral
```
/status  →  mostra:
  📋 Tarefas abertas: 4
     🔴 URGENTES: 2
```

### 2. **Skill `/relatorio`** — filtra por processo
```
/relatorio 7054209  →  inclui tarefas daquele processo
```

### 3. **Google Calendar** — sincronização automática
Se a tarefa tem `vencimento`, modulo_calendar.py cria evento no Calendar.

### 4. **MISSOES.md** — painel de controle
Tarefas com origem "Manual" sincronizam com MISSOES.md para auditoria.

---

## FORMATO INTERNO (tarefas.json)

```json
{
  "atualizado_em": "2026-07-04T14:30:00Z",
  "tarefas": [
    {
      "id": "T-001",
      "criada_em": "2026-06-28",
      "status": "ABERTA",
      "processo": "7000001-00.XXXX.8.22.0001",
      "tribunal": "TJRO",
      "classe": "EDCiv",
      "partes": "CLIENTE_AUTOR × CLIENTE_RÉU",
      "titulo": "Sustentação Oral",
      "descricao": "Inscrição sustentação oral para sessão eletrônica",
      "tipo": "PRAZO_FATAL",
      "vencimento": "2026-06-30",
      "prioridade": "URGENTE",
      "acao_necessaria": "ENVIAR E-MAIL PARA TRIBUNAL",
      "destinatario": "tribunal@tjro.jus.br",
      "pasta_cliente": "",
      "calendar_id": "XXXXXXXXXXXXXXXX",
      "notas": "Prazo improrrogável — verificar calendário processual",
      "origem": "PJe"
    }
  ]
}
```

---

## AUTOMAÇÃO NO loop_monitor.py

A cada **30 segundos**, a skill `/tarefas urgentes` executa:

```python
def checar_tarefas_urgentes() -> None:
    """Verifica tarefas urgentes e registra em antigravity_output.txt."""
    log.info("=== Verificando tarefas urgentes ===")
    code, out = run(
        [sys.executable, str(AGENTE_DIR / "modulo_tarefas.py"), "urgentes"],
        timeout=30,
    )
    if "URGENTE" in out or "VENCIDO" in out:
        log_out(f"[TAREFAS:URGENTES]\n{out[:600]}")
```

**Resultado:**
- Se houver urgentes → aparece em `antigravity_output.txt` com 🔴 vermelho
- GitHub pusha o log automaticamente
- Claude lê e pode alertar Dr. Jefferson

---

## REGRAS DE OURO

1. **Nunca deletar** uma tarefa — apenas marcar CANCELADA ou CONCLUIDA
2. **Sempre preencher processo/tribunal** — para integração com relatórios
3. **Vencimento é obrigatório** para PRAZO_FATAL e PRAZO_NORMAL
4. **Status automático** — CONCLUIDA → nunca mais aparece em "abertas"
5. **Origem importante** — DJe, PJe, WhatsApp, Manual — rastreia fonte

---

## CHECKLIST — Antes de marcar CONCLUÍDA

- [ ] Ação foi executada (peça redigida, e-mail enviado, etc.)
- [ ] Resultado documentado (link, número de autuação, confirmação)
- [ ] Se era PRAZO_FATAL → calendário judicial conferido?
- [ ] Há próxima ação? (criar tarefa T-0XX para ela)
- [ ] Dr. Jefferson confirma a conclusão?

---

## CANAL MABIOS

Marcar tarefa concluída via Gmail rascunho:

```
Assunto: MABIOS_ACTION:CONCLUIR:T-001
Corpo: Sustentação oral inscrita com sucesso em 30/06/2026
```

`modulo_mabios_email.py` detecta → marca T-001 como CONCLUIDA em tarefas.json

---

**Skill pronta para rodar 24/7 automaticamente!** 🚀
