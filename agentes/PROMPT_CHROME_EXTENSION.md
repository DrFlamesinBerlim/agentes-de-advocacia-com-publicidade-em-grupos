# Prompt operacional — Claude for Chrome → Apps Script MABIOS

Cole o bloco abaixo inteiro na extensão Claude for Chrome.
Ele já antecipa os erros conhecidos do projeto (ver seção "Falhas antecipadas" no fim deste arquivo).

---

```
MISSÃO
Instalar e ativar o sistema MABIOS v3 num projeto Google Apps Script, colando 7 arquivos
de código e executando 2 funções. Trabalhe com autonomia, mas PARE e me pergunte sempre
que encontrar algo fora do previsto abaixo. Não invente valores, não adivinhe chaves,
não improvise nomes de função.

═══════════════════════════════════════════════════════
FASE 0 — VERIFICAÇÃO DE IDENTIDADE (não pule)
═══════════════════════════════════════════════════════
Abra: https://script.google.com/home/projects/1liBsDxSYRTxGyeRA0HFjFecMSN2VZiq33LovaDQxZMeTlS7ePpb_ubKv/edit

Antes de qualquer coisa, me reporte:
  a) O nome do projeto exibido no topo
  b) A lista COMPLETA de arquivos já existentes no painel esquerdo
  c) Se existe algum gatilho já configurado (menu lateral → ícone de relógio "Acionadores")

PARE AQUI e espere minha confirmação se qualquer uma destas condições for verdadeira:
  - O projeto contém código sobre "presidentes", "TRU", DocumentApp ou qualquer assunto
    não-jurídico → é o projeto ERRADO, não continue
  - Já existem acionadores configurados → preciso decidir se podem ser apagados
  - Já existem arquivos começando com "CC001_" → é reinstalação, o procedimento muda

Se o projeto estiver vazio ou só com o "Código.gs" padrão, siga para a Fase 1.

═══════════════════════════════════════════════════════
FASE 1 — COLAR OS 7 ARQUIVOS
═══════════════════════════════════════════════════════
Para CADA arquivo da lista abaixo, nesta ordem:

  1. Abra a URL raw numa aba nova
  2. Confirme que a página carregou código (começa com "/**") e NÃO é uma página de erro
     404 do GitHub. Se der 404, PARE e me avise imediatamente.
  3. Selecione tudo (Ctrl+A) e copie (Ctrl+C)
  4. Volte à aba do Apps Script
  5. Clique no "+" ao lado de "Arquivos" → escolha "Script"
  6. Digite o nome SEM a extensão .gs (o Apps Script adiciona sozinho —
     digitar "CC001_EmailMonitor.gs" cria "CC001_EmailMonitor.gs.gs", o que quebra tudo)
  7. Apague TODO o conteúdo padrão do editor (Ctrl+A → Delete)
  8. Cole (Ctrl+V)
  9. Salve (Ctrl+S)
  10. Confirme que não apareceu erro de sintaxe em vermelho antes de ir ao próximo

ARQUIVOS (nome a digitar → URL para copiar):

CC001_EmailMonitor
https://raw.githubusercontent.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos/claude/mabios-cowork-agent-setup-4j1rkz/agentes/CC001_EmailMonitor.gs

CC001_PrazoAnalyzer
https://raw.githubusercontent.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos/claude/mabios-cowork-agent-setup-4j1rkz/agentes/CC001_PrazoAnalyzer.gs

CC001_AgendaPlanner
https://raw.githubusercontent.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos/claude/mabios-cowork-agent-setup-4j1rkz/agentes/CC001_AgendaPlanner.gs

CC001_PJeIngestor
https://raw.githubusercontent.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos/claude/mabios-cowork-agent-setup-4j1rkz/agentes/CC001_PJeIngestor.gs

CC001_DataJudIntegration
https://raw.githubusercontent.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos/claude/mabios-cowork-agent-setup-4j1rkz/agentes/CC001_DataJudIntegration.gs

CC001_ErrorHandler
https://raw.githubusercontent.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos/claude/mabios-cowork-agent-setup-4j1rkz/agentes/CC001_ErrorHandler.gs

CC001_MasterSetup
https://raw.githubusercontent.com/DrFlamesinBerlim/agentes-de-advocacia-com-publicidade-em-grupos/claude/mabios-cowork-agent-setup-4j1rkz/agentes/CC001_MasterSetup.gs

Ao terminar os 7: apague o arquivo "Código.gs" (ou "Code.gs") padrão, se ele ainda
existir e contiver apenas a função vazia myFunction(). Salve.

Me reporte: "7 arquivos colados, nenhum erro de sintaxe" — ou descreva o que deu errado.

═══════════════════════════════════════════════════════
FASE 2 — CHAVE DA API DATAJUD (requer minha confirmação)
═══════════════════════════════════════════════════════
Abra: https://datajud-wiki.cnj.jus.br/api-publica/acesso

Localize na página a APIKey pública divulgada pelo CNJ. NÃO execute nada ainda:
me mostre o valor exato que você encontrou e me diga em que trecho da página estava.
Só prossiga depois que eu confirmar que é a chave certa.

Depois da minha confirmação:
  1. No arquivo CC001_DataJudIntegration, localize a função setDataJudApiKey
  2. Adicione TEMPORARIAMENTE no final do arquivo:
       function _aplicarChave() { setDataJudApiKey('CHAVE_CONFIRMADA'); }
  3. Selecione "_aplicarChave" no seletor de função e execute
  4. Confirme no log que apareceu "API Key do DataJud salva com sucesso."
  5. APAGUE a função _aplicarChave e salve (para a chave não ficar no código)

═══════════════════════════════════════════════════════
FASE 3 — INSTALAÇÃO
═══════════════════════════════════════════════════════
Selecione a função "instalarTudoMABIOS" no seletor do topo e clique em Executar (▶).

QUANDO A TELA DE AUTORIZAÇÃO DO GOOGLE APARECER: pare e me chame.
Eu mesmo faço os cliques de consentimento — não clique em "Permitir" por mim.
(Vai pedir acesso a Gmail, Drive, Calendar e requisições externas.)

Depois que eu autorizar, execute novamente e me mostre o log completo.
O log deve listar 4 linhas com ✅. Se alguma tiver ❌, me mostre o erro exato.

ATENÇÃO — pode aparecer uma SEGUNDA tela de autorização mais tarde, na Fase 4,
quando o DataJud fizer a primeira chamada externa. Isso é normal, me chame de novo.

═══════════════════════════════════════════════════════
FASE 4 — TESTES (um de cada vez, não use testarTudoMABIOS)
═══════════════════════════════════════════════════════
Execute NESTA ORDEM, uma por vez, esperando cada uma terminar:

  1. testarRelatorioDiario     → deve enviar 1 email, leva poucos segundos
  2. testarAnalisadorPrazos    → pode não enviar email nenhum (só envia se houver
                                 prazo crítico/urgente) — isso é comportamento correto
  3. testarPlanificadorAgenda  → cria eventos no Google Calendar + envia email
  4. testarDataJudIngestor     → LENTO: consulta ~100 processos, pode levar minutos
                                 ou estourar o limite de 6 min do Apps Script.
                                 Se der timeout, NÃO é falha — me avise e seguimos.

NÃO execute "testarMonitoramento" nesta rodada: ele força um diff completo e gera
um email gigante listando todos os processos como novos. Só serve depois.

Após cada execução, me diga: nome da função, status (Concluída/Erro), e o log.

═══════════════════════════════════════════════════════
FASE 5 — VERIFICAÇÃO FINAL
═══════════════════════════════════════════════════════
  a) Menu lateral → "Acionadores": me liste todos os gatilhos criados.
     Esperado: 5 gatilhos, todos com nomes terminando em "_protegido"
  b) Menu lateral → "Execuções": me diga se alguma aparece como "Falhou"
  c) Abra gmail.com e me diga quais emails com "[CC-001]" chegaram
  d) Abra calendar.google.com e me diga se apareceram eventos novos de petições

═══════════════════════════════════════════════════════
REGRAS PERMANENTES
═══════════════════════════════════════════════════════
- Nunca clique em botões de consentimento OAuth do Google — sempre me chame
- Nunca invente uma API key, número de processo ou nome de função
- Se um erro mencionar "has already been declared", me avise: significa arquivo
  colado em duplicidade, e eu digo qual apagar
- Se algo divergir deste roteiro, pare e pergunte em vez de improvisar
```

---

## Falhas antecipadas (por que o prompt é assim)

| Risco real | Onde | Mitigação no prompt |
|---|---|---|
| Projeto errado aberto (já aconteceu: script de "presidentes") | Fase 0 | Verificação de identidade obrigatória antes de tocar em qualquer coisa |
| `setupTriggers()` faz `getProjectTriggers().forEach(deleteTrigger)` — apaga **todos** os gatilhos do projeto, inclusive de outros scripts | `CC001_EmailMonitor.gs:29` | Fase 0 exige listar gatilhos existentes e parar se houver |
| Nome de arquivo digitado com `.gs` vira `arquivo.gs.gs` | UI do Apps Script | Instrução explícita de digitar sem extensão |
| Arquivo colado duas vezes → `Identifier 'CONFIG' has already been declared` (escopo global é compartilhado entre todos os `.gs`) | Comportamento do Apps Script | Regra permanente com diagnóstico pronto |
| Segunda tela de OAuth aparece só quando `UrlFetchApp` roda pela 1ª vez | DataJud | Avisado na Fase 3, esperado na Fase 4 |
| `testarDataJudIngestor` percorre ~100 processos com `sleep(300)` + HTTP → pode estourar o limite de 6 min | `CC001_DataJudIntegration.gs` | Marcado como lento; timeout classificado como não-falha |
| `testarAnalisadorPrazos` não envia email se não houver prazo crítico — parece falha, mas é o comportamento correto | `CC001_PrazoAnalyzer.gs:98` | Explicitado para não gerar diagnóstico errado |
| `testarMonitoramento` apaga o hash e gera email gigante com todos os processos como "novos" | `CC001_EmailMonitor.gs:378` | Excluído da primeira rodada |
| URL raw pode dar 404 (branch tem `/` no nome) | GitHub | Verificação de conteúdo antes de colar |
| Chave da API inventada pelo agente | DataJud | Confirmação humana obrigatória antes de aplicar |
