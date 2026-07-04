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

## Plugins habilitados na conta

- legal
- cowork-plugin-management
- zapier
- sanity-plugin
- brightdata-plugin
- wix
- valtown
- datarobot-agent-skills

Não tenho acesso ao conteúdo/configuração interna de cada plugin (o que exatamente o "legal" ou o "cowork-plugin-management" fazem por trás) — só sei que estão habilitados na conta.

## Limitações deste levantamento

Este inventário reflete apenas o que é visível a partir desta sessão de chat, via as ferramentas de conta (rotinas agendadas e conectores). Ele **não** cobre:
- Outras sessões ativas do Claude Code (CLI/app), incluindo subagentes rodando em outros projetos ou repositórios.
- Agentes ou automações configuradas dentro do Cowork além dos plugins listados acima.
- O comportamento interno de cada plugin/conector.

Para um retrato completo, é preciso checar diretamente as telas de configuração do Code e do Cowork.

## Repositório

`agentes-de-advocacia-com-publicidade-em-grupos` está vazio (apenas um README em branco) — ainda não há código ou automação própria do projeto implementada aqui.
