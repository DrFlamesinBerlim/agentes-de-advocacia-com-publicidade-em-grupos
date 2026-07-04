# GUIA DE INSTALAÇÃO - DRA. JULIA ADVOCACIA

## Passo 1: Importar Workflow no N8N
1. Acesse N8N → Workflows → Import from file
2. Selecione: workflows/dra-julia-agente-ia-advocacia.json
3. Clique Import

## Passo 2: Configurar Credenciais
- whatsapp-api-token: HTTP Header Auth (Authorization: Bearer SEU_TOKEN)
- openai-api: OpenAI API Key
- google-sheets-oauth: OAuth2 Google Sheets
- google-calendar-oauth: OAuth2 Google Calendar

## Passo 3: Google Sheets
Criar planilha com 3 abas:
- Clientes_Dra_Julia: Nome, Telefone, Data_Contato, Tipo, Conteudo, Area_Juridica, Status
- Consultas_Agendadas: Data, Nome, Telefone, Area, Data_Preferida, Status
- Documentos_Gerados: Data, Tipo, Cliente, Telefone, Detalhes, Status, Conteudo

## Passo 4: WhatsApp Business
1. Meta Developer Console → App Business → WhatsApp
2. Webhook: https://seu-n8n.com/webhook/dra-julia-advocacia
3. Eventos: messages, message_deliveries

## Passo 5: Testes
- Texto: "Preciso de ajuda com contrato" → resposta jurídica
- Imagem: foto de contrato → análise GPT-4o
- Áudio: consulta falada → transcrição + resposta
- Agendamento: "agendar consulta sobre divórcio" → evento Calendar

## Troubleshooting
- Webhook não recebe: verificar URL e verify token
- OpenAI erro: verificar API key e créditos
- Sheets não salva: verificar OAuth2 e permissões