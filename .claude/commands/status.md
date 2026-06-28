# /status — Status do escritório De Brito Advocacia

Mostra um painel rápido com o estado atual do sistema e dos processos.

---

Ao receber este comando, leia os seguintes arquivos e apresente um resumo executivo:

**Fontes:**
- `documentos/processos.json` → contagem por status
- `documentos/tarefas.json` → tarefas abertas, urgentes, vencendo
- `documentos/prazos_pendentes.json` → prazos críticos
- `antigravity_output.txt` → últimas linhas (atividade recente do Antigravity)

**Formato do painel:**

```
=== DE BRITO ADVOCACIA — STATUS ===
Data: DD/MM/YYYY HH:MM

PROCESSOS
  Ativos    : XX
  Conferidos: XX
  Arquivados: XX

PRAZOS CRÍTICOS (vencendo em ≤ 7 dias)
  🔴 [número] vence DD/MM — movimento

TAREFAS ABERTAS
  Total: XX  |  Urgentes: XX  |  Vencendo hoje: XX
  → [T-001] título (vence DD/MM)

ANTIGRAVITY (último log)
  [timestamp] última atividade registrada
===================================
```

Se algum arquivo não existir, informe qual está faltando.
