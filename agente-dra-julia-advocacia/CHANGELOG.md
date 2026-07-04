# CHANGELOG - DRA. JULIA ADVOCACIA

## Versão 2.0.0 - Guardrails, Segurança e Robustez
Data: Abril 2025 | Status: Estável

### Correções Críticas de Segurança
- Tokens removidos do JSON: WHATSAPP_TOKEN e PHONE_NUMBER_ID movidos para variáveis de ambiente
- Webhook challenge verificado
- Anti-replay attack: mensagens com timestamp > 5 minutos são descartadas
- Truncamento de input: mensagens limitadas a 4.000 caracteres

### Correções de Fluxo
- Loop circular eliminado
- onError em todos os nós
- Dois passos para mídia (URL + binário) — API v20.0
- Stickers ignorados silenciosamente
- Validação E.164 nos lembretes

### Melhorias
- Modelo atualizado: gpt-4-vision-preview → gpt-4o
- maxTokens aumentado: 800 → 1.200/1.500/2.000
- Classificação: 6 → 9 áreas + fallback Geral
- 6 guardrails no system prompt
- Graph API v17.0 → v20.0
- Aviso legal obrigatório em documentos gerados
- saveDataErrorExecution: "all"

## Versão 1.0.0 - Lançamento Inicial
Data: Outubro 2024 | Status: Estável