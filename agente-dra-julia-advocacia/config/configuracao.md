# CONFIGURAÇÃO - DRA. JULIA ADVOCACIA

## Variáveis de Ambiente Necessárias

### WhatsApp Business API
WHATSAPP_TOKEN=seu_token_permanente_meta
PHONE_NUMBER_ID=seu_phone_number_id
WEBHOOK_VERIFY_TOKEN=seu_token_verificacao

### OpenAI API
OPENAI_API_KEY=sua_chave_openai
# Modelos: gpt-4o (conversas + visão), whisper-1 (transcrição)

### Google Workspace
GOOGLE_SHEETS_ID_ADVOCACIA=id_da_planilha_advocacia
GOOGLE_CALENDAR_ID=primary_ou_id_calendario

## Webhook WhatsApp
URL: https://seu-n8n.com/webhook/dra-julia-advocacia
Método: POST e GET
API Version: v20.0 (Graph API)

NOTA v2.0: Configure WEBHOOK_VERIFY_TOKEN com valor aleatório (32+ chars).
NUNCA coloque tokens diretamente no JSON do workflow.
Use variáveis de ambiente ($env['WHATSAPP_TOKEN'], etc.)

## Credenciais N8N
- whatsapp-api-token (HTTP Header Auth)
- openai-api (OpenAI API)
- google-sheets-oauth (Google Sheets OAuth2)
- google-calendar-oauth (Google Calendar OAuth2)

## Cron
Expression: 0 9 * * 1-5 (Lembretes às 9h dias úteis)