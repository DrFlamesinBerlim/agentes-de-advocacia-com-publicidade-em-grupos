# Prompt de finalização — Claude for Chrome

Use este prompt **depois** que o bundle `CC001_MABIOS_BUNDLE_UNICO.gs` já estiver colado
no projeto Apps Script. Ele conclui a instalação: autorização, chave do CNJ, gatilhos e testes.

(Se o bundle ainda não foi colado, use `PROMPT_CHROME_EXTENSION.md` antes deste.)

---

```
CONTEXTO
Sou o Dr. Jefferson Silva de Brito, advogado (OAB/RO 2952). Já colei um arquivo de código
grande num projeto do Google Apps Script chamado CC001_MABIOS. Esse código automatiza o
acompanhamento dos meus processos judiciais: envia relatórios por email, alerta prazos
críticos, sugere datas de protocolo e consulta andamentos na API pública do CNJ.

Falta concluir a instalação. Conduza o processo comigo, passo a passo.

DADOS DE REFERÊNCIA (use exatamente estes valores, não invente outros)
  Conta Google correta ....... flamesinberlim@gmail.com
  Projeto Apps Script ........ CC001_MABIOS
  Email de destino ........... flamesinberlim@gmail.com
  Arquivo de dados no Drive .. processos.json
  ID desse arquivo ........... 1HpfH2bbsfbtFstygaNevn4oIl5uBeHgz
  Calendário dos prazos ...... flamesinberlim@gmail.com
  Página da chave do CNJ ..... https://datajud-wiki.cnj.jus.br/api-publica/acesso
  Tribunal configurado ....... TJRO (alias api_publica_tjro)

REGRAS PERMANENTES (valem para todas as fases)
  1. Eu tenho MAIS DE UMA conta Google logada. Antes de qualquer ação, confirme que o
     Apps Script está aberto como flamesinberlim@gmail.com. Se não estiver, me avise —
     a outra conta é tribuna.livre.ro@gmail.com e o projeto NÃO deve ficar lá.
  2. NUNCA clique em botões de consentimento OAuth do Google. Me chame, eu clico.
  3. NUNCA entre em Configurações do projeto → "Alterar projeto do Google Cloud Platform".
     Essa ação é irreversível e desnecessária — o código usa só serviços nativos.
  4. NUNCA invente a chave da API do CNJ, número de processo ou nome de função.
  5. Se algo divergir deste roteiro, PARE e pergunte em vez de improvisar.
  6. Rode UMA função por vez e espere terminar. Não use testarTudoMABIOS.

═══════════════════════════════════════════════════════
FASE 1 — CONFERIR A COLAGEM
═══════════════════════════════════════════════════════
Abra https://script.google.com e entre no projeto CC001_MABIOS.

Salve com Ctrl+S. Depois abra o seletor de funções (dropdown ao lado do botão Executar)
e me confirme se estas 6 funções aparecem na lista:
    instalarTudoMABIOS
    testarRelatorioDiario
    testarAnalisadorPrazos
    testarPlanificadorAgenda
    testarDataJudIngestor
    setDataJudApiKey

PARE e me avise se:
  - O dropdown estiver vazio ou faltar alguma dessas funções → a colagem falhou
  - Aparecer erro vermelho no editor → me mande o texto exato do erro
  - Aparecer "has already been declared" → o código foi colado em duplicidade;
    me diga quais arquivos existem no painel esquerdo e eu digo qual apagar

Se existir um arquivo "Código.gs" ou "Code.gs" contendo apenas a função vazia
myFunction(), apague-o e salve.

═══════════════════════════════════════════════════════
FASE 2 — PRIMEIRO TESTE + AUTORIZAÇÃO
═══════════════════════════════════════════════════════
Começamos por testarRelatorioDiario porque é rápido, não depende da chave do CNJ,
e já valida o acesso ao Gmail e ao Drive de uma vez.

Selecione "testarRelatorioDiario" no dropdown e clique em Executar (▶).

Vai aparecer a tela de autorização do Google. PARE AQUI e me chame.
Eu vou percorrer: Revisar permissões → flamesinberlim@gmail.com → Avançado →
Acessar CC001_MABIOS (não seguro) → Permitir.
(O aviso "não seguro" é normal: aparece em qualquer script não auditado publicamente
pelo Google. É código meu, na minha conta.)

Depois que eu autorizar, execute testarRelatorioDiario NOVAMENTE — a primeira execução
costuma ser interrompida pela autorização e não chega a enviar o email.

Em seguida, abra gmail.com e me diga se chegou um email com assunto começando em
"[CC-001] Relatório Diário".

Se der erro, me mande a mensagem exata (aparece embaixo no editor, ou no menu lateral
em "Execuções").

═══════════════════════════════════════════════════════
FASE 3 — CHAVE DA API DO CNJ
═══════════════════════════════════════════════════════
Abra em outra aba: https://datajud-wiki.cnj.jus.br/api-publica/acesso

Localize a APIKey pública divulgada pelo CNJ. NÃO execute nada ainda: me mostre o valor
exato encontrado e em que trecho da página estava. Só siga depois da minha confirmação.

ATENÇÃO — detalhe importante: a função setDataJudApiKey recebe um parâmetro, e o editor
do Apps Script NÃO permite passar parâmetros ao executar pelo dropdown. Por isso é preciso
criar uma função auxiliar temporária.

Depois da minha confirmação:
  1. Vá até o FINAL do arquivo de código e acrescente:

         function _aplicarChave() {
           setDataJudApiKey('CHAVE_QUE_EU_CONFIRMEI');
         }

  2. Salve (Ctrl+S)
  3. Selecione "_aplicarChave" no dropdown e execute
  4. Confirme no log que apareceu: "API Key do DataJud salva com sucesso."
  5. APAGUE a função _aplicarChave inteira e salve de novo
     (para a chave não ficar escrita no código-fonte)

A chave fica guardada nas Propriedades do script, então continua funcionando depois
de apagar a função.

═══════════════════════════════════════════════════════
FASE 4 — ATIVAR AS AUTOMAÇÕES PERMANENTES
═══════════════════════════════════════════════════════
Selecione "instalarTudoMABIOS" e execute.

O log deve mostrar 4 linhas com ✅:
    ✅ Relatórios e alertas de alteração
    ✅ Análise de prazos
    ✅ Planejador de agenda
    ✅ Consulta oficial DataJud (CNJ)

Se alguma linha vier com ❌, me mande o erro exato dela.

Pode aparecer uma SEGUNDA tela de autorização nesta fase ou na próxima, pedindo permissão
para "conectar-se a um serviço externo". Isso é esperado — é a primeira vez que o código
chama a API do CNJ. Me chame de novo para eu autorizar.

═══════════════════════════════════════════════════════
FASE 5 — TESTES RESTANTES (um de cada vez)
═══════════════════════════════════════════════════════
Execute nesta ordem, esperando cada um terminar antes do próximo.
Após cada execução me informe: nome da função, status e o log.

1. testarAnalisadorPrazos
   ⚠️ PODE NÃO ENVIAR EMAIL NENHUM — e isso é CORRETO, não é falha.
   Esta função só envia email se houver prazo crítico (≤3 dias) ou urgente (≤7 dias).
   Se não houver nenhum, ela apenas registra no log e encerra.

2. testarPlanificadorAgenda
   Deve criar eventos no Google Calendar e enviar um email.
   Se o log mostrar "Erro ao criar evento", provavelmente o script está rodando numa
   conta que não é flamesinberlim@gmail.com — me avise imediatamente.

3. testarDataJudIngestor
   ⚠️ LENTO. Consulta cerca de 100 processos, um por um, com pausa entre eles.
   Pode levar vários minutos ou estourar o limite de 6 minutos do Apps Script.
   TIMEOUT AQUI NÃO É FALHA — é limitação conhecida da plataforma. Me avise e seguimos.
   No log devem aparecer linhas "✓ <número do processo>: <data> — <movimentação>".

NÃO execute "testarMonitoramento" agora. Ela força uma comparação completa e gera um
email gigante listando todos os processos como novos. Só faz sentido depois.

═══════════════════════════════════════════════════════
FASE 6 — VERIFICAÇÃO FINAL
═══════════════════════════════════════════════════════
Me reporte cada item:

  a) Menu lateral → "Acionadores" (ícone de relógio): liste todos os gatilhos.
     Esperado: 5 gatilhos, com nomes terminando em "_protegido"

  b) Menu lateral → "Execuções": alguma aparece como "Falhou"? Quais?

  c) Configurações do projeto → copie e me mande o "ID do script"
     (preciso dele para confirmar que o projeto existe)

  d) gmail.com → quais emails com "[CC-001]" chegaram? Liste os assuntos.

  e) calendar.google.com (logado em flamesinberlim@gmail.com) →
     apareceram eventos novos com nome de processo entre colchetes?

Ao final, me dê um resumo em 5 linhas: o que funcionou, o que falhou, e o que ficou
pendente.
```

---

## Por que o prompt é assim

| Ponto de falha | Onde ocorre | Tratamento |
|---|---|---|
| `setDataJudApiKey` recebe parâmetro, mas o dropdown do editor não passa argumentos | Fase 3 | Função auxiliar `_aplicarChave()`, criada e apagada em seguida |
| Primeira execução é interrompida pelo OAuth e não envia o email | Fase 2 | Instrução explícita de executar uma segunda vez |
| Segunda tela de OAuth só aparece na primeira chamada `UrlFetchApp` | Fases 4–5 | Antecipado, classificado como esperado |
| `testarAnalisadorPrazos` não enviar email é comportamento correto | Fase 5 | Explicitado, para não gerar diagnóstico falso |
| `testarDataJudIngestor` pode estourar os 6 min do Apps Script | Fase 5 | Timeout declarado como não-falha |
| `CALENDAR_ID` fixo em flamesinberlim: se rodar em outra conta, `getCalendarById` retorna null | Fase 5 | Vira sinal de diagnóstico de conta errada |
| Duas contas Google logadas — causa provável de vários travamentos anteriores | Regra 1 | Verificação de conta antes de qualquer ação |
| Troca de projeto GCP é irreversível e desnecessária | Regra 3 | Proibição explícita |
| Bundle colado em duplicidade → `has already been declared` | Fase 1 | Diagnóstico pronto |
| Agente inventar a chave da API | Regra 4 + Fase 3 | Confirmação humana obrigatória |
