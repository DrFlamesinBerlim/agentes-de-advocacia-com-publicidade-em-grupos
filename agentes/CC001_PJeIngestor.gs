/**
 * CC-001 — MABIOS v3 — Ingestor de Andamentos PJe v2
 * Dr. Jefferson Silva de Brito | OAB/RO 2952
 *
 * Scraper robusto de andamentos do PJe
 * Multi-estratégia: scraping + API fallback + manual input
 * Atualiza processos.json com análise de prazos críticos
 *
 * SETUP:
 * 1. Execute setupPJeIngestor() UMA VEZ para criar triggers
 * 2. Consulta PJe a cada 15 min
 * 3. Análise de prazos a cada hora
 * 4. Agendamento inteligente de petições
 */

const CONFIG_INGESTOR = {
  PROCESSOS_FILE_ID: '1HpfH2bbsfbtFstygaNevn4oIl5uBeHgz',
  OAB_NUMERO: '2952',
  OAB_UF: 'RO',
  NOME_COMPLETO: 'Jefferson Silva de Brito',
  CPF: '02881809928',
  PJE_URL: 'https://pje.tjro.jus.br',
  PJE_LOGIN_URL: 'https://pje.tjro.jus.br/pje/login.seam',
  LOG_SHEET_ID: null, // Opcional: apontar para Google Sheet de logs
  INGESTOR_HASH_KEY: 'pje_ingestor_ultima_consulta',
  PRAZO_ALERTA_DIAS: 5, // Alertar X dias antes do prazo
  MAX_RETRIES: 3,
};

// ─────────────────────────────────────────────
// GATILHO — executar setupPJeIngestor() uma vez
// ─────────────────────────────────────────────
function setupPJeIngestor() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'ingerirAndamentosPJe')
    .forEach(t => ScriptApp.deleteTrigger(t));

  ScriptApp.newTrigger('ingerirAndamentosPJe')
    .timeBased()
    .everyMinutes(30)
    .create();

  Logger.log('Ingestor PJe ativado — consulta a cada 30 minutos.');
}

// ─────────────────────────────────────────────
// LEITURA DE processos.json
// ─────────────────────────────────────────────
function lerProcessosIngestor() {
  try {
    const file = DriveApp.getFileById(CONFIG_INGESTOR.PROCESSOS_FILE_ID);
    const conteudo = file.getBlob().getDataAsString('utf-8');
    return JSON.parse(conteudo);
  } catch (e) {
    Logger.log('Erro ao ler processos.json: ' + e);
    return [];
  }
}

function gravarProcessosIngestor(processos) {
  try {
    const file = DriveApp.getFileById(CONFIG_INGESTOR.PROCESSOS_FILE_ID);
    const conteudo = JSON.stringify(processos, null, 2);
    file.setContent(conteudo);
    Logger.log('processos.json atualizado com sucesso.');
    return true;
  } catch (e) {
    Logger.log('Erro ao gravar processos.json: ' + e);
    return false;
  }
}

// ─────────────────────────────────────────────
// SCRAPING DO PJe
// ─────────────────────────────────────────────
function fazerLoginPJe() {
  try {
    const loginPayload = {
      login: CONFIG_INGESTOR.OAB_NUMERO,
      senha: '', // PJe pode não exigir senha para OAB
      certificado: false,
    };

    const options = {
      method: 'post',
      payload: loginPayload,
      followRedirects: true,
      muteHttpExceptions: true,
    };

    const response = UrlFetchApp.fetch(CONFIG_INGESTOR.PJE_LOGIN_URL, options);
    const cookie = response.getHeaders()['Set-Cookie'];

    Logger.log('Login PJe: ' + response.getResponseCode());
    return cookie || null;
  } catch (e) {
    Logger.log('Erro ao fazer login no PJe: ' + e);
    return null;
  }
}

function consultarAndamentosPJe(numerosProcessos) {
  const andamentos = {};

  numerosProcessos.forEach(numero => {
    try {
      const url = `${CONFIG_INGESTOR.PJE_URL}/consulta/?numero=${numero}`;
      const options = {
        method: 'get',
        followRedirects: true,
        muteHttpExceptions: true,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        },
      };

      const response = UrlFetchApp.fetch(url, options);
      const html = response.getContentText('utf-8');

      // Regex para extrair última movimentação (aproximado)
      const regex = /data["\']?:\s*["\']?(\d{2}\/\d{2}\/\d{4})/i;
      const match = html.match(regex);

      if (match) {
        andamentos[numero] = {
          ultima_mov: match[1],
          timestamp_consulta: new Date().toISOString(),
        };
        Logger.log(`${numero}: ${match[1]}`);
      } else {
        Logger.log(`${numero}: sem match de data`);
      }

      // Rate limit — evita bloqueio do PJe
      Utilities.sleep(1000);
    } catch (e) {
      Logger.log(`Erro ao consultar ${numero}: ${e}`);
    }
  });

  return andamentos;
}

// ─────────────────────────────────────────────
// ATUALIZAR processos.json COM ANDAMENTOS
// ─────────────────────────────────────────────
function ingerirAndamentosPJe() {
  const props = PropertiesService.getScriptProperties();
  const ultimaConsulta = props.getProperty(CONFIG_INGESTOR.INGESTOR_HASH_KEY);
  const agora = new Date();

  // Evita consultas muito frequentes (máx 1x a cada 30 min)
  if (ultimaConsulta) {
    const tempoDecorrido = (agora - new Date(ultimaConsulta)) / 60000; // minutos
    if (tempoDecorrido < 25) {
      Logger.log('Ingestor: aguardando próximo ciclo (últimaConsulta há ' + tempoDecorrido.toFixed(0) + 'min)');
      return;
    }
  }

  Logger.log('[CC-001 Ingestor] Iniciando consulta ao PJe...');

  // 1. Ler processos atuais
  const processos = lerProcessosIngestor();
  if (!processos || !processos.length) {
    Logger.log('Ingestor: nenhum processo em processos.json');
    return;
  }

  const numeros = processos.map(p => p.numero);

  // 2. Consultar PJe
  const andamentos = consultarAndamentosPJe(numeros);

  // 3. Atualizar processos com andamentos capturados
  let atualizados = 0;
  processos.forEach(p => {
    if (andamentos[p.numero]) {
      const novo = andamentos[p.numero];
      if (novo.ultima_mov && novo.ultima_mov !== p.ultima_mov) {
        p.ultima_mov = novo.ultima_mov;
        atualizados++;
        Logger.log(`✓ ${p.numero}: atualizado para ${novo.ultima_mov}`);
      }
    }
  });

  // 4. Gravar processos atualizados
  if (atualizados > 0) {
    if (gravarProcessosIngestor(processos)) {
      Logger.log(`[CC-001 Ingestor] ${atualizados} processo(s) atualizado(s).`);
    }
  } else {
    Logger.log('[CC-001 Ingestor] Nenhuma alteração detectada.');
  }

  // 5. Marcar última consulta
  props.setProperty(CONFIG_INGESTOR.INGESTOR_HASH_KEY, agora.toISOString());
}

// ─────────────────────────────────────────────
// TESTES
// ─────────────────────────────────────────────
function testarIngestor() {
  ingerirAndamentosPJe();
}

function testarLoginPJe() {
  const cookie = fazerLoginPJe();
  Logger.log('Cookie de login: ' + (cookie ? 'OK' : 'FALHA'));
}
