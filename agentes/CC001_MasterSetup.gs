/**
 * CC-001 — MABIOS v3 — Instalação Mestre
 * Dr. Jefferson Silva de Brito | OAB/RO 2952
 *
 * Depois de colar TODOS os scripts (.gs) neste projeto e configurar a
 * DATAJUD_API_KEY (setDataJudApiKey), rode só estas duas funções:
 *
 *   instalarTudoMABIOS()   → ativa todos os gatilhos permanentes
 *   testarTudoMABIOS()     → dispara todos os testes agora, envia emails
 *
 * Não precisa rodar cada função de setup ou de teste individualmente.
 */

function instalarTudoMABIOS() {
  const resultados = [];

  const passos = [
    ['Relatórios e alertas de alteração', setupTriggers],
    ['Análise de prazos', setupAnalisadorPrazos],
    ['Planejador de agenda', setupPlanificadorAgenda],
    ['Consulta oficial DataJud (CNJ)', setupDataJudIngestor],
  ];

  passos.forEach(([nome, fn]) => {
    try {
      fn();
      resultados.push(`✅ ${nome}`);
    } catch (e) {
      resultados.push(`❌ ${nome} — ERRO: ${e}`);
    }
  });

  Logger.log('═══════════════════════════════════════');
  Logger.log('INSTALAÇÃO MABIOS v3 — RESULTADO');
  Logger.log('═══════════════════════════════════════');
  resultados.forEach(r => Logger.log(r));
  Logger.log('═══════════════════════════════════════');

  const apiKey = PropertiesService.getScriptProperties().getProperty(CONFIG_DATAJUD.API_KEY_PROP);
  if (!apiKey) {
    Logger.log('⚠️  ATENÇÃO: DATAJUD_API_KEY não configurada ainda.');
    Logger.log('   Rode: setDataJudApiKey(\'sua-chave\')');
    Logger.log('   Chave em: https://datajud-wiki.cnj.jus.br/api-publica/acesso');
  }

  return resultados;
}

function testarTudoMABIOS() {
  const resultados = [];

  const testes = [
    ['Relatório diário', testarRelatorioDiario],
    ['Detecção de alterações', testarMonitoramento],
    ['Análise de prazos', testarAnalisadorPrazos],
    ['Sugestões de agenda', testarPlanificadorAgenda],
    ['Consulta DataJud', testarDataJudIngestor],
  ];

  testes.forEach(([nome, fn]) => {
    try {
      fn();
      resultados.push(`✅ ${nome} — executado, verifique o email`);
    } catch (e) {
      resultados.push(`❌ ${nome} — ERRO: ${e}`);
    }
  });

  Logger.log('═══════════════════════════════════════');
  Logger.log('TESTE MABIOS v3 — RESULTADO');
  Logger.log('═══════════════════════════════════════');
  resultados.forEach(r => Logger.log(r));
  Logger.log('═══════════════════════════════════════');
  Logger.log('Verifique flamesinberlim@gmail.com — emails devem ter chegado.');

  return resultados;
}
