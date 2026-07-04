# Inventário de Automações

Levantamento do que está rodando hoje nesta conta: o que é acionado manualmente via chat (conectores) e o que roda sozinho por agendamento (rotinas/triggers).

## Rotinas agendadas (rodam sozinhas)

| Nome | Frequência | O que faz | Conectores usados | Notificação |
|---|---|---|---|---|
| Email triage | A cada hora (`0 * * * *`) | Revisa e-mails novos/não lidos, categoriza em Urgente / Ação Necessária / FYI / Baixa Prioridade, resume cada um em uma frase e rascunha resposta para os itens Urgente/Ação Necessária | Gmail, Google Calendar, Notion, Google Drive, monday.com | Push ativado, e-mail desativado |

Ambiente de execução: "Default - trusted network access". Existe também um segundo ambiente cadastrado, "rede doméstica segura", sem rotinas rodando nele no momento.

## Conectores disponíveis via chat (uso manual)

Conectados e habilitados neste chat:
- Gmail
- Google Calendar
- Google Drive
- Notion
- monday.com
- Slack
- Canva
- SignNow
- Granola
- Kindora Funder Discovery
- Booking.com
- Spotify
- Uber

Instalados mas não habilitados neste chat / status desconhecido:
- Docusign
- Microsoft 365
- Sanity
- Local Falcon
- Zapier

## Repositório

`agentes-de-advocacia-com-publicidade-em-grupos` está vazio (apenas um README em branco) — ainda não há código ou automação própria do projeto implementada aqui.
