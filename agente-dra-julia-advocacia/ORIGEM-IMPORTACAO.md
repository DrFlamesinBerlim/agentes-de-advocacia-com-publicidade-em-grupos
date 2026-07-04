# Origem deste material

Este diretório foi importado do Google Drive do usuário (pasta `TESTE/agente-dra-julia-advocacia`),
que por sua vez é uma cópia local do repositório GitHub `JeffersonMFti/agente-dra-julia-advocacia`.

## Limitação importante

O arquivo `workflows/dra-julia-agente-ia-advocacia.json` salvo no Drive **não é o workflow completo**.
É um resumo estrutural com apenas 2 dos 35 nós do workflow real (o próprio arquivo contém uma nota
interna dizendo isso). Para obter o workflow N8N completo e funcional, é preciso importar o `.json`
original diretamente do repositório GitHub `JeffersonMFti/agente-dra-julia-advocacia` — esta sessão
não conseguiu adicionar esse repositório automaticamente porque pertence a outro dono (só é possível
adicionar repositórios do mesmo dono dos já presentes na sessão).

## Também pendente

- Credenciais (WhatsApp Business API, OpenAI, Google Sheets/Calendar) precisam ser configuradas —
  ver `config/configuracao.md` e `documentacao/GUIA-INSTALACAO.md`.
- Nenhum código foi adaptado ainda para "publicidade em grupos" (o foco original deste projeto é
  atendimento individual via WhatsApp, não postagem em grupos).
