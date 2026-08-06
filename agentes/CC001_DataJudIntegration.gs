/**
 * CC-001 — MABIOS v3 — Integração API Pública DataJud (CNJ)
 * Dr. Jefferson Silva de Brito | OAB/RO 2952
 *
 * Substitui o scraping do PJe por consulta OFICIAL à API pública do CNJ.
 * Não requer login, certificado digital nem 2FA — apenas uma API Key
 * pública fornecida pelo próprio CNJ.
 *
 * Cobre processos NÃO SIGILOSOS. Processos em segredo de justiça
 * continuam exigindo consulta manual no PJe (login com certificado).
 *
 * COMO OBTER A API KEY:
 * 1. Acesse https://datajud-wiki.cnj.jus.br/api-publica/acesso
 * 2. Copie a APIKey pública divulgada pelo CNJ (é a mesma para todos os usuários)
 * 3. Em script.google.com → Configurações do projeto → Propriedades do script
 *    → adicione: DATAJUD_API_KEY = <chave copiada>
 *    (ou rode setDataJudApiKey('sua-chave') uma vez)
 *
 * SETUP:
 * setupDataJudIngestor()   // cria o gatilho — roda a cada 30 min
 * testarDataJudIngestor()  // executa uma consulta agora
 */

const CONFIG_DATAJUD = {
  PROCESSOS_FILE_ID: '1HpfH2bbsfbtFstygaNevn4oIl5uBeHgz',
  // Alias do tribunal no DataJud. TJRO = api_publica_tjro.
  // Lista completa: https://datajud-wiki.cnj.jus.br/api-publica/endpoints
  ALIAS_TRIBUNAL: 'api_publica_tjro',
  BASE_URL: 'https://api-publica.datajud.cnj.jus.br',
  API_KEY_PROP: 'DATAJUD_API_KEY',
  INGESTOR_HASH_KEY: 'datajud_ultima_consulta',
};

function setDataJudApiKey(chave) {
  PropertiesService.getScriptProperties().setProperty(CONFIG_DATAJUD.API_KEY_PROP, chave);
  Logger.log('API Key do DataJud salva com sucesso.');
}

function setupDataJudIngestor() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'ingerirAndamentosDataJud')
    .forEach(t => ScriptApp.deleteTrigger(t));

  ScriptApp.newTrigger('ingerirAndamentosDataJud')
    .timeBased()
    .everyMinutes(30)
    .create();

  Logger.log('Ingestor DataJud ativado — consulta oficial a cada 30 minutos.');
}

// ─────────────────────────────────────────────
// LEITURA / GRAVAÇÃO processos.json
// ─────────────────────────────────────────────
function lerProcessosDataJud() {
  try {
    const file = DriveApp.getFileById(CONFIG_DATAJUD.PROCESSOS_FILE_ID);
    const conteudo = file.getBlob().getDataAsString('utf-8');
    return JSON.parse(conteudo);
  } catch (e) {
    Logger.log('Erro ao ler processos.json: ' + e);
    return [];
  }
}

function gravarProcessosDataJud(processos) {
  try {
    const file = DriveApp.getFileById(CONFIG_DATAJUD.PROCESSOS_FILE_ID);
    file.setContent(JSON.stringify(processos, null, 2));
    Logger.log('processos.json atualizado via DataJud.');
    return true;
  } catch (e) {
    Logger.log('Erro ao gravar processos.json: ' + e);
    return false;
  }
}

// ─────────────────────────────────────────────
// NORMALIZAÇÃO DO NÚMERO DE PROCESSO
// DataJud exige o número CNJ só com dígitos (sem . e -)
// ─────────────────────────────────────────────
function normalizarNumeroProcesso(numero) {
  return (numero || '').replace(/\D/g, '');
}

// ─────────────────────────────────────────────
// CONSULTA À API DATAJUD (Elasticsearch DSL)
// ─────────────────────────────────────────────
function consultarProcessoDataJud(numeroProcesso) {
  const apiKey = PropertiesService.getScriptProperties().getProperty(CONFIG_DATAJUD.API_KEY_PROP);
  if (!apiKey) {
    Logger.log('DATAJUD_API_KEY não configurada. Rode setDataJudApiKey(\'sua-chave\') primeiro.');
    return null;
  }

  const numeroLimpo = normalizarNumeroProcesso(numeroProcesso);
  const url = `${CONFIG_DATAJUD.BASE_URL}/${CONFIG_DATAJUD.ALIAS_TRIBUNAL}/_search`;

  const query = {
    query: {
      match: { numeroProcesso: numeroLimpo },
    },
    size: 1,
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: `APIKey ${apiKey}`,
    },
    payload: JSON.stringify(query),
    muteHttpExceptions: true,
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const code = response.getResponseCode();

    if (code !== 200) {
      Logger.log(`DataJud ${numeroProcesso}: HTTP ${code} — ${response.getContentText().substring(0, 200)}`);
      return null;
    }

    const json = JSON.parse(response.getContentText());
    const hit = json.hits && json.hits.hits && json.hits.hits[0];
    if (!hit) {
      Logger.log(`DataJud ${numeroProcesso}: não encontrado (processo pode ser sigiloso ou fora do TJRO).`);
      return null;
    }

    return hit._source;
  } catch (e) {
    Logger.log(`Erro ao consultar DataJud ${numeroProcesso}: ${e}`);
    return null;
  }
}

// ─────────────────────────────────────────────
// EXTRAIR ÚLTIMO ANDAMENTO DO RESULTADO
// ─────────────────────────────────────────────
function extrairUltimoAndamento(fonteDataJud) {
  const movimentos = fonteDataJud.movimentos || [];
  if (!movimentos.length) return null;

  // Ordena por data decrescente
  const ordenados = movimentos
    .filter(m => m.dataHora)
    .sort((a, b) => new Date(b.dataHora) - new Date(a.dataHora));

  if (!ordenados.length) return null;

  const ultimo = ordenados[0];
  const data = new Date(ultimo.dataHora);
  const dataStr = Utilities.formatDate(data, 'America/Porto_Velho', 'dd/MM/yyyy');
  const descricao = ultimo.nome || ultimo.complementosTabelados?.map(c => c.nome).join(' | ') || 'Movimentação sem descrição';

  return { ultima_mov: dataStr, mov_desc: descricao };
}

// ─────────────────────────────────────────────
// INGESTÃO PRINCIPAL
// ─────────────────────────────────────────────
function ingerirAndamentosDataJud() {
  const props = PropertiesService.getScriptProperties();
  const ultimaConsulta = props.getProperty(CONFIG_DATAJUD.INGESTOR_HASH_KEY);
  const agora = new Date();

  if (ultimaConsulta) {
    const minutos = (agora - new Date(ultimaConsulta)) / 60000;
    if (minutos < 25) {
      Logger.log('DataJud: aguardando próximo ciclo (última consulta há ' + minutos.toFixed(0) + 'min)');
      return;
    }
  }

  Logger.log('[CC-001 DataJud] Iniciando consulta oficial ao CNJ...');

  const processos = lerProcessosDataJud();
  if (!processos.length) {
    Logger.log('DataJud: nenhum processo em processos.json');
    return;
  }

  let atualizados = 0;
  let naoEncontrados = 0;

  processos.forEach(p => {
    const fonte = consultarProcessoDataJud(p.numero);
    if (!fonte) {
      naoEncontrados++;
      return;
    }

    const ultimo = extrairUltimoAndamento(fonte);
    if (ultimo && ultimo.ultima_mov !== p.ultima_mov) {
      p.ultima_mov = ultimo.ultima_mov;
      p.mov_desc = ultimo.mov_desc;
      p.status_conferido = true;
      p.ultima_verificacao = new Date().toISOString();
      atualizados++;
      Logger.log(`✓ ${p.numero}: ${ultimo.ultima_mov} — ${ultimo.mov_desc}`);
    }

    // Rate limit — respeita a API pública do CNJ
    Utilities.sleep(300);
  });

  if (atualizados > 0) {
    gravarProcessosDataJud(processos);
    Logger.log(`[CC-001 DataJud] ${atualizados} processo(s) atualizado(s), ${naoEncontrados} não encontrado(s) (sigilosos ou fora do TJRO).`);
  } else {
    Logger.log(`[CC-001 DataJud] Nenhuma alteração. ${naoEncontrados} não encontrado(s).`);
  }

  props.setProperty(CONFIG_DATAJUD.INGESTOR_HASH_KEY, agora.toISOString());
}

// ─────────────────────────────────────────────
// TESTES
// ─────────────────────────────────────────────
function testarDataJudIngestor() {
  ingerirAndamentosDataJud();
}

function testarConsultaUnicaDataJud(numeroProcesso) {
  const resultado = consultarProcessoDataJud(numeroProcesso);
  Logger.log(JSON.stringify(resultado, null, 2));
  return resultado;
}
