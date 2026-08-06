# MABIOS v3 — De Brito Advocacia
**Dr. Jefferson Silva de Brito | OAB/RO 2952**

## Rede Trans-LLM
| Nó | Identidade | Função |
|---|---|---|
| JB-000 | Dr. Jefferson (Operador Humano) | Direção e aprovação |
| CC-001 | Claude Cowork | Redação jurídica + análise + governança |
| GA-002 | Gemini Antigravity | Automação local + scripts + integridade de dados |
| WA-003 | WhatsApp Coordinator | Atendimento + triagem + alertas (Evolution API) |

## Estrutura do Repositório
```
agentes/          — Prompts e diretrizes dos nós
documentos/       — processos.json, nodos_registro.json, capacidades_nodos.json
pecas/            — Peças processuais redigidas e aprovadas
config/           — Configurações de integração e ledger
```

## Regras Operacionais
- API local: `http://localhost:8000` (FastAPI MABIOS — máquina física do escritório)
- Compliance OAB: dispositivo legal exato + jurisprudência real TJRO→STJ→STF
- Monitoramento CC-001: ciclo horário automático ativo (CronJob 7dbf000f)
- Auto-expiração do cron: 7 dias (renovar sessão para manter ativo)

## Aviso de Segurança
Nunca modificar: `documentos/nodos_registro.json`, `documentos/capacidades_nodos.json`, arquivos em `5_codigo_bibliotecas/`.
