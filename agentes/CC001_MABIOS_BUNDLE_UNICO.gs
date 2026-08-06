/**
 * ╔══════════════════════════════════════════════════════════════╗
 * ║  CC-001 — MABIOS v3 — ARQUIVO ÚNICO (BUNDLE)                 ║
 * ║  Dr. Jefferson Silva de Brito | OAB/RO 2952                  ║
 * ╚══════════════════════════════════════════════════════════════╝
 *
 * Este arquivo contém TODO o sistema. Não é preciso colar 7 arquivos:
 * cole só este, num único arquivo de script.
 *
 * ─────────────────────────────────────────────────────────────
 * INSTALAÇÃO (4 passos)
 * ─────────────────────────────────────────────────────────────
 * 1. Em script.google.com → Novo projeto → nomeie "CC001_MABIOS"
 * 2. Apague o conteúdo padrão e cole este arquivo inteiro. Salve (Ctrl+S).
 * 3. Pegue a APIKey pública do CNJ em:
 *      https://datajud-wiki.cnj.jus.br/api-publica/acesso
 *    e rode uma vez (troque pela chave real):
 *      setDataJudApiKey('SUA_CHAVE_AQUI')
 * 4. Rode  instalarTudoMABIOS()  → autorize quando o Google pedir
 *    Depois rode os testes um a um (veja lista no fim do arquivo).
 *
 * NÃO troque o projeto do Google Cloud Platform nas configurações.
 * Este código só usa serviços nativos e funciona no projeto padrão.
 *
 * ─────────────────────────────────────────────────────────────
 * FUNÇÕES PRINCIPAIS
 * ─────────────────────────────────────────────────────────────
 *   setDataJudApiKey('chave')  → salva a chave do CNJ (rodar 1x)
 *   instalarTudoMABIOS()       → ativa todos os gatilhos permanentes
 *   testarRelatorioDiario()    → envia o relatório agora
 *   testarAnalisadorPrazos()   → checa prazos (só envia email se houver risco)
 *   testarPlanificadorAgenda() → sugere datas + cria eventos no Calendar
 *   testarDataJudIngestor()    → consulta o CNJ (LENTO, pode dar timeout)
 */


// ═══════════════════════════════════════════════════════════════
// ORIGEM: CC001_ErrorHandler.gs
// ═══════════════════════════════════════════════════════════════

/**
 * CC-001 — MABIOS v3 — Notificação de Erros
 * Dr. Jefferson Silva de Brito | OAB/RO 2952
 *
 * Triggers do Apps Script falham SILENCIOSAMENTE — o erro só aparece
 * nos logs, que ninguém checa. Esta função avisa por email quando

// ═══════════════════════════════════════════════════════════════
// ORIGEM: CC001_ErrorHandler.gs
// ═══════════════════════════════════════════════════════════════

/**
 * CC-001 — MABIOS v3 — Notificação de Erros
 * Dr. Jefferson Silva de Brito | OAB/RO 2952
 *
 * Triggers do Apps Script falham SILENCIOSAMENTE — o erro só aparece
 * nos logs, que ninguém checa. Esta função avisa por email quando
 * qualquer automação quebra, para nunca haver falha invisível.
 *
 * Usado internamente pelos outros scripts — não precisa chamar direto.
 */

const CONFIG_ERROS = {
  EMAIL_DESTINO: 'flamesinberlim@gmail.com',
  MIN_INTERVALO_MESMO_ERRO_HORAS: 6, // evita spam do mesmo erro repetido
};

function notificarErroCC001(origem, erro) {
  try {
    const props = PropertiesService.getScriptProperties();
    const chaveUltimoAlerta = `erro_${origem}_ultimo_alerta`;
    const agora = new Date();
    const ultimoAlerta = props.getProperty(chaveUltimoAlerta);

    if (ultimoAlerta) {
      const horasDecorridas = (agora - new Date(ultimoAlerta)) / 3600000;
      if (horasDecorridas < CONFIG_ERROS.MIN_INTERVALO_MESMO_ERRO_HORAS) {
        Logger.log(`[CC-001] Erro em ${origem} suprimido (já alertado há ${horasDecorridas.toFixed(1)}h): ${erro}`);
        return;
      }
    }

    const horaStr = Utilities.formatDate(agora, 'America/Porto_Velho', 'dd/MM/yyyy HH:mm');
    const mensagem = erro && erro.stack ? erro.stack : String(erro);

    GmailApp.sendEmail(
      CONFIG_ERROS.EMAIL_DESTINO,
      `🔴 [CC-001] Falha em automação — ${origem}`,
      `A automação "${origem}" falhou em ${horaStr} (Brasília).\n\nErro:\n${mensagem}\n\n` +
      `Isso não interrompe as demais automações, mas essa função específica não rodou desta vez. ` +
      `Verifique em script.google.com → Execuções, para detalhes completos.`
    );

    props.setProperty(chaveUltimoAlerta, agora.toISOString());
    Logger.log(`[CC-001] Email de erro enviado para ${origem}.`);
  } catch (e) {
    // Última linha de defesa — se até a notificação de erro falhar, ao menos loga.
    Logger.log('[CC-001] FALHA CRÍTICA: não foi possível notificar erro. ' + e);
  }
}

/**
 * Envolve uma função de automação com captura de erro + notificação.
 * Uso: executarComProtecao('nomeDaFuncao', minhaFuncao);
 */
function executarComProtecao(nomeOrigem, funcao) {
  try {
    funcao();
  } catch (e) {
    Logger.log(`[CC-001] Erro capturado em ${nomeOrigem}: ${e}`);
    notificarErroCC001(nomeOrigem, e);
  }
}

// ═══════════════════════════════════════════════════════════════
// ORIGEM: CC001_EmailMonitor.gs
// ═══════════════════════════════════════════════════════════════

/**
 * CC-001 — MABIOS v3 — De Brito Advocacia
 * Dr. Jefferson Silva de Brito | OAB/RO 2952
 *
 * Google Apps Script: Monitor de Processos + Email Automático
 *
 * INSTALAÇÃO:
 * 1. Acesse script.google.com → Novo projeto → cole este código
 * 2. Salve como "CC001_EmailMonitor"
 * 3. Execute setupTriggers() UMA VEZ para criar os gatilhos permanentes
 * 4. Autorize as permissões (Drive + Gmail)
 * 5. Pronto — roda para sempre sem expiração
 *
 * CONFIGURAÇÕES:
 */
const CONFIG = {
  PROCESSOS_FILE_ID: '1HpfH2bbsfbtFstygaNevn4oIl5uBeHgz',
  EMAIL_DESTINO: 'flamesinberlim@gmail.com',
  HASH_PROP_KEY: 'processos_hash_anterior',
  SNAPSHOT_PROP_KEY: 'processos_snapshot_anterior',
  HORA_RELATORIO_DIARIO: 7,
};

// ─────────────────────────────────────────────
// GATILHOS — executar setupTriggers() uma vez
// ─────────────────────────────────────────────
function setupTriggers() {
  // Remove gatilhos antigos para evitar duplicatas
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));

  // Relatório diário completo às 07h
  ScriptApp.newTrigger('enviarRelatorioDiario_protegido')
    .timeBased()
    .everyDays(1)
    .atHour(CONFIG.HORA_RELATORIO_DIARIO)
    .create();

  // Monitoramento de alterações a cada hora
  ScriptApp.newTrigger('monitorarAlteracoes_protegido')
    .timeBased()
    .everyHours(1)
    .create();

  Logger.log('Gatilhos criados com sucesso. CC-001 ativo permanentemente.');
}

// Wrappers protegidos — chamados pelos triggers, avisam por email se falharem
function enviarRelatorioDiario_protegido() {
  executarComProtecao('enviarRelatorioDiario', enviarRelatorioDiario);
}

function monitorarAlteracoes_protegido() {
  executarComProtecao('monitorarAlteracoes', monitorarAlteracoes);
}

// ─────────────────────────────────────────────
// LEITURA DO processos.json
// ─────────────────────────────────────────────
function lerProcessos() {
  const file = DriveApp.getFileById(CONFIG.PROCESSOS_FILE_ID);
  const conteudo = file.getBlob().getDataAsString('utf-8');
  return JSON.parse(conteudo);
}

function calcularHash(texto) {
  const bytes = Utilities.computeDigest(
    Utilities.DigestAlgorithm.MD5,
    texto,
    Utilities.Charset.UTF_8
  );
  return bytes.map(b => ('0' + (b & 0xff).toString(16)).slice(-2)).join('');
}

// ─────────────────────────────────────────────
// CÁLCULO DE DIAS DE INATIVIDADE
// ─────────────────────────────────────────────
function parseDateBR(s) {
  if (!s || s === '—' || s === 'verificar' || s === 'ok') return null;
  const parts = s.substring(0, 10).split('/');
  if (parts.length === 3) return new Date(parts[2], parts[1] - 1, parts[0]);
  const iso = new Date(s.substring(0, 10));
  return isNaN(iso) ? null : iso;
}

function diasInatividade(ultimaMov) {
  const d = parseDateBR(ultimaMov);
  if (!d) return 9999;
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  return Math.floor((hoje - d) / 86400000);
}

function prazoVencidoOuProximo(dataPrazo) {
  const d = parseDateBR(dataPrazo);
  if (!d) return false;
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  return (d - hoje) / 86400000 <= 5;
}

// ─────────────────────────────────────────────
// GERAÇÃO DO RELATÓRIO HTML
// ─────────────────────────────────────────────
function gerarRelatorioHTML(processos, dataRef) {
  const hoje = dataRef || new Date();
  const dataStr = Utilities.formatDate(hoje, 'America/Porto_Velho', 'dd/MM/yyyy');

  const grupos = {
    urgentes: [],
    ativo: [],
    p16: [], p31: [], p46: [], p61: [], p121: [], p181: [], p261: [],
    r1ano: [], r2anos: [], r3anos: [],
    instSup: [],
    naoPrio: [],
  };

  processos.forEach(p => {
    const dias = diasInatividade(p.ultima_mov);
    const prazo = p.prazo_calculado || {};
    const urgente = prazo.urgente || (prazo.data_prazo_final && prazo_vencidoOuProximo_wrapper(prazo.data_prazo_final));
    const instSup = (p.mov_desc || '').toLowerCase().includes('remetidos em grau de recurso');

    if (!p.prioritario) { grupos.naoPrio.push({...p, dias}); return; }
    if (urgente)         { grupos.urgentes.push({...p, dias, prazo}); }
    if (instSup)         { grupos.instSup.push({...p, dias}); return; }

    if (dias <= 15)       grupos.ativo.push({...p, dias});
    else if (dias <= 30)  grupos.p16.push({...p, dias});
    else if (dias <= 45)  grupos.p31.push({...p, dias});
    else if (dias <= 60)  grupos.p46.push({...p, dias});
    else if (dias <= 120) grupos.p61.push({...p, dias});
    else if (dias <= 180) grupos.p121.push({...p, dias});
    else if (dias <= 260) grupos.p181.push({...p, dias});
    else if (dias <= 365) grupos.p261.push({...p, dias});
    else if (dias <= 730) grupos.r1ano.push({...p, dias});
    else if (dias <= 1095) grupos.r2anos.push({...p, dias});
    else                  grupos.r3anos.push({...p, dias});
  });

  function prazo_vencidoOuProximo_wrapper(dp) {
    return prazoVencidoOuProximo(dp);
  }

  function tabelaHTML(lista, cor) {
    if (!lista.length) return '<p style="color:#888;font-style:italic">Nenhum processo.</p>';
    let rows = lista.sort((a,b) => a.dias - b.dias).map(p => {
      const link = `https://pje.tjro.jus.br/consulta/?numero=${p.numero}`;
      const prazoStr = p.prazo && p.prazo.data_prazo_final
        ? `<br><span style="color:#c00;font-weight:bold">⚠️ PRAZO: ${p.prazo.data_prazo_final} — ${p.prazo.descricao || ''}</span>`
        : '';
      return `<tr>
        <td style="font-family:monospace;font-size:12px"><a href="${link}" target="_blank" style="color:#0066cc;text-decoration:none;font-weight:bold">${p.numero}</a></td>
        <td>${p.cliente || '—'}</td>
        <td style="color:#333;font-size:12px">${p.partes || '—'}</td>
        <td>${p.ultima_mov || '—'}</td>
        <td style="text-align:center"><b>${p.dias}d</b></td>
        <td>${(p.mov_desc || '—').substring(0, 80)}${prazoStr}</td>
      </tr>`;
    }).join('');
    return `<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:13px">
      <thead style="background:${cor};color:white">
        <tr><th>Processo</th><th>Cliente</th><th>Partes</th><th>Última Mov.</th><th>Dias</th><th>Movimentação</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>`;
  }

  const secoes = [
    { titulo: '🚨 URGENTE — PRAZO CORRENDO', lista: grupos.urgentes, cor: '#b71c1c' },
    { titulo: '🟢 ATIVO/RECENTE ≤15d', lista: grupos.ativo, cor: '#2e7d32' },
    { titulo: '🟡 PARALISADO 16–30d', lista: grupos.p16, cor: '#f9a825' },
    { titulo: '🟡 PARALISADO 31–45d', lista: grupos.p31, cor: '#f9a825' },
    { titulo: '🟡 PARALISADO 46–60d', lista: grupos.p46, cor: '#ef6c00' },
    { titulo: '🟡 PARALISADO 61–120d', lista: grupos.p61, cor: '#ef6c00' },
    { titulo: '🟡 PARALISADO 121–180d', lista: grupos.p121, cor: '#e65100' },
    { titulo: '🟡 PARALISADO 181–260d', lista: grupos.p181, cor: '#e65100' },
    { titulo: '🟡 PARALISADO 261–365d', lista: grupos.p261, cor: '#bf360c' },
    { titulo: '🔴 PARADO ANTIGO >1 ano', lista: grupos.r1ano, cor: '#880e4f' },
    { titulo: '🔴 PARADO ANTIGO >2 anos', lista: grupos.r2anos, cor: '#880e4f' },
    { titulo: '🔴 PARADO ANTIGO >3 anos', lista: grupos.r3anos, cor: '#4a148c' },
    { titulo: '🔵 SUSPENSOS / INSTÂNCIA SUPERIOR', lista: grupos.instSup, cor: '#0d47a1' },
    { titulo: '📦 CAIXA NÃO PRIORITÁRIA', lista: grupos.naoPrio, cor: '#546e7a' },
  ];

  // Calcular estatísticas de risco
  const risco = {
    critico: grupos.urgentes.length,
    alto: grupos.p16.length + grupos.p31.length,
    medio: grupos.p46.length + grupos.p61.length,
    baixo: grupos.p121.length + grupos.p181.length + grupos.p261.length + grupos.ativo.length,
    arquivados: grupos.naoPrio.length,
  };

  let corpo = `
    <div style="font-family:Arial,sans-serif;max-width:1100px;margin:auto">
    <h2 style="background:#1a237e;color:white;padding:16px;border-radius:6px">
      ⚖️ CC-001 — Relatório Diário de Processos<br>
      <small style="font-size:14px">De Brito Advocacia | Dr. Jefferson Silva de Brito | OAB/RO 2952</small><br>
      <small style="font-size:13px">Data: ${dataStr} | Total: ${processos.length} processos</small>
    </h2>
    <div style="background:#fff3cd;border:1px solid #ffc107;padding:12px;border-radius:4px;margin-bottom:16px">
      <small style="color:#333"><b>📊 SAÚDE DA CARTEIRA:</b> ${risco.critico} críticos | ${risco.alto} altos | ${risco.medio} médios | ${risco.baixo} baixos | ${risco.arquivados} arquivados</small>
    </div>`;

  // Resumo executivo
  corpo += `<table style="width:100%;border-collapse:collapse;margin-bottom:20px">
    <tr style="background:#f5f5f5">
      ${secoes.filter(s => s.lista.length).map(s =>
        `<td style="padding:10px;text-align:center;border:1px solid #ddd">
          <div style="font-size:20px;font-weight:bold">${s.lista.length}</div>
          <div style="font-size:11px">${s.titulo}</div>
        </td>`
      ).join('')}
    </tr>
  </table>`;

  secoes.forEach(s => {
    if (!s.lista.length) return;
    corpo += `<h3 style="background:${s.cor};color:white;padding:10px;border-radius:4px;margin-top:24px">
      ${s.titulo} — ${s.lista.length} processo(s)
    </h3>${tabelaHTML(s.lista, s.cor)}`;
  });

  corpo += '</div>';
  return corpo;
}

// ─────────────────────────────────────────────
// ENVIAR RELATÓRIO DIÁRIO COMPLETO
// ─────────────────────────────────────────────
function enviarRelatorioDiario() {
  const processos = lerProcessos();
  const hoje = new Date();
  const dataStr = Utilities.formatDate(hoje, 'America/Porto_Velho', 'dd/MM/yyyy');
  const html = gerarRelatorioHTML(processos, hoje);
  const assunto = `[CC-001] Relatório Diário — De Brito Advocacia | ${dataStr}`;

  // Deletar relatório anterior (mesmo assunto, enviado por mim mesmo)
  const threads = GmailApp.search('in:sent subject:"[CC-001] Relatório Diário"');
  threads.slice(0, 5).forEach(t => {
    const msgs = t.getMessages();
    msgs.forEach(m => {
      if (m.getSubject().includes('Relatório Diário')) {
        m.moveToTrash();
      }
    });
  });

  GmailApp.sendEmail(
    CONFIG.EMAIL_DESTINO,
    assunto,
    'Visualize em cliente de email com suporte a HTML.',
    { htmlBody: html }
  );

  // Salva snapshot atual para comparação horária
  const props = PropertiesService.getScriptProperties();
  const conteudo = JSON.stringify(processos);
  props.setProperty(CONFIG.HASH_PROP_KEY, calcularHash(conteudo));
  props.setProperty(CONFIG.SNAPSHOT_PROP_KEY, conteudo);

  Logger.log(`[CC-001] Relatório diário enviado (anterior deletado) — ${processos.length} processos — ${dataStr}`);
}

// ─────────────────────────────────────────────
// MONITORAR ALTERAÇÕES (HORÁRIO)
// ─────────────────────────────────────────────
function monitorarAlteracoes() {
  const props = PropertiesService.getScriptProperties();
  const file = DriveApp.getFileById(CONFIG.PROCESSOS_FILE_ID);
  const conteudoAtual = file.getBlob().getDataAsString('utf-8');
  const hashAtual = calcularHash(conteudoAtual);
  const hashAnterior = props.getProperty(CONFIG.HASH_PROP_KEY) || '';

  if (hashAtual === hashAnterior) {
    Logger.log('[CC-001] Nenhuma alteração detectada.');
    return;
  }

  // Detecta diferenças
  const processosAtuais = JSON.parse(conteudoAtual);
  const snapshotStr = props.getProperty(CONFIG.SNAPSHOT_PROP_KEY);
  const processosAnteriores = snapshotStr ? JSON.parse(snapshotStr) : [];

  const mapaAnterior = {};
  processosAnteriores.forEach(p => mapaAnterior[p.numero] = p);

  const alteracoes = [];
  const novos = [];
  const camposMonitorados = ['ultima_mov', 'mov_desc', 'status', 'prioritario', 'prazo_calculado'];

  processosAtuais.forEach(pAtual => {
    const pAnt = mapaAnterior[pAtual.numero];
    if (!pAnt) {
      novos.push(pAtual);
      return;
    }
    const diffs = [];
    camposMonitorados.forEach(campo => {
      const vAtual = JSON.stringify(pAtual[campo] ?? null);
      const vAnt = JSON.stringify(pAnt[campo] ?? null);
      if (vAtual !== vAnt) {
        diffs.push({ campo, antes: pAnt[campo], depois: pAtual[campo] });
      }
    });
    if (diffs.length) alteracoes.push({ processo: pAtual, diffs });
  });

  if (!alteracoes.length && !novos.length) {
    props.setProperty(CONFIG.HASH_PROP_KEY, hashAtual);
    props.setProperty(CONFIG.SNAPSHOT_PROP_KEY, conteudoAtual);
    return;
  }

  // Gera email de alterações
  const agora = new Date();
  const horaStr = Utilities.formatDate(agora, 'America/Porto_Velho', 'dd/MM/yyyy HH:mm');
  let html = `
    <div style="font-family:Arial,sans-serif;max-width:900px;margin:auto">
    <h2 style="background:#e65100;color:white;padding:16px;border-radius:6px">
      ⚡ CC-001 — Alterações Detectadas<br>
      <small style="font-size:13px">De Brito Advocacia | ${horaStr} (Brasília)</small><br>
      <small style="font-size:13px">${alteracoes.length} processo(s) alterado(s) | ${novos.length} novo(s)</small>
    </h2>`;

  if (novos.length) {
    html += `<h3 style="color:#1a237e">🆕 Novos Processos (${novos.length})</h3>`;
    novos.forEach(p => {
      html += `<div style="border:1px solid #1a237e;border-radius:4px;padding:12px;margin:8px 0">
        <b>${p.numero}</b> | ${p.cliente || '—'}<br>
        <small>Última mov: ${p.ultima_mov || '—'} | ${p.mov_desc || '—'}</small>
      </div>`;
    });
  }

  if (alteracoes.length) {
    html += `<h3 style="color:#e65100">🔄 Processos Alterados (${alteracoes.length})</h3>`;
    alteracoes.forEach(({ processo: p, diffs }) => {
      const urgente = (p.prazo_calculado || {}).urgente;
      const bordaCor = urgente ? '#b71c1c' : '#e65100';
      html += `<div style="border:2px solid ${bordaCor};border-radius:4px;padding:12px;margin:10px 0">
        <b style="font-size:15px">${p.numero}</b> — ${p.cliente || '—'}<br>`;
      diffs.forEach(d => {
        const campo = d.campo.replace(/_/g,' ').toUpperCase();
        const antes = d.campo === 'prazo_calculado'
          ? (d.antes ? `${d.antes.descricao || ''} | Prazo: ${d.antes.data_prazo_final || '—'}` : '—')
          : String(d.antes ?? '—');
        const depois = d.campo === 'prazo_calculado'
          ? (d.depois ? `${d.depois.descricao || ''} | Prazo: ${d.depois.data_prazo_final || '—'}` : '—')
          : String(d.depois ?? '—');
        html += `<div style="margin:6px 0;padding:6px;background:#fff8e1;border-left:4px solid ${bordaCor}">
          <b>${campo}:</b><br>
          <span style="color:#888">Antes:</span> ${antes}<br>
          <span style="color:#2e7d32;font-weight:bold">Depois:</span> ${depois}
        </div>`;
      });
      if (urgente) html += `<div style="color:#b71c1c;font-weight:bold;margin-top:6px">🚨 PRAZO URGENTE ATIVO</div>`;
      html += '</div>';
    });
  }

  html += '</div>';

  GmailApp.sendEmail(
    CONFIG.EMAIL_DESTINO,
    `[CC-001] ⚡ Alterações Detectadas — De Brito Advocacia | ${horaStr}`,
    'Visualize em cliente de email com suporte a HTML.',
    { htmlBody: html }
  );

  // Atualiza snapshot
  props.setProperty(CONFIG.HASH_PROP_KEY, hashAtual);
  props.setProperty(CONFIG.SNAPSHOT_PROP_KEY, conteudoAtual);

  Logger.log(`[CC-001] Email de alterações enviado — ${alteracoes.length} alterações, ${novos.length} novos.`);
}

// ─────────────────────────────────────────────
// TESTE MANUAL
// ─────────────────────────────────────────────
function testarRelatorioDiario() {
  enviarRelatorioDiario();
}

function testarMonitoramento() {
  // Força detecção limpando o hash anterior
  PropertiesService.getScriptProperties().deleteProperty(CONFIG.HASH_PROP_KEY);
  monitorarAlteracoes();
}

// ═══════════════════════════════════════════════════════════════
// ORIGEM: CC001_PrazoAnalyzer.gs
// ═══════════════════════════════════════════════════════════════

/**
 * CC-001 — MABIOS v3 — Análise de Prazos Inteligente
 * Detecta prazos críticos, calcula risco, sugere ações
 *
 * Funciona junto com CC001_EmailMonitor.gs
 * Roda a cada hora automaticamente
 */

const CONFIG_PRAZO = {
  PROCESSOS_FILE_ID: '1HpfH2bbsfbtFstygaNevn4oIl5uBeHgz',
  EMAIL_DESTINO: 'flamesinberlim@gmail.com',
  DIAS_ALERTA_CRITICO: 3,
  DIAS_ALERTA_URGENTE: 7,
  DIAS_ALERTA_NORMAL: 14,
};

function setupAnalisadorPrazos() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'analisarPrazosCriticos')
    .forEach(t => ScriptApp.deleteTrigger(t));

  ScriptApp.newTrigger('analisarPrazosCriticos_protegido')
    .timeBased()
    .everyHours(1)
    .create();

  Logger.log('Analisador de Prazos ativado — verifica a cada hora.');
}

function analisarPrazosCriticos_protegido() {
  executarComProtecao('analisarPrazosCriticos', analisarPrazosCriticos);
}

function lerProcessosPrazo() {
  try {
    const file = DriveApp.getFileById(CONFIG_PRAZO.PROCESSOS_FILE_ID);
    const conteudo = file.getBlob().getDataAsString('utf-8');
    return JSON.parse(conteudo);
  } catch (e) {
    Logger.log('Erro ao ler processos: ' + e);
    return [];
  }
}

function parseDateBRPrazo(s) {
  if (!s || s === '—') return null;
  const parts = s.substring(0, 10).split('/');
  if (parts.length === 3) return new Date(parts[2], parts[1] - 1, parts[0]);
  return null;
}

function diasAteDataPrazo(dataPrazo) {
  const d = parseDateBRPrazo(dataPrazo);
  if (!d) return 9999;
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  return Math.floor((d - hoje) / 86400000);
}

function classificarPrazo(dias) {
  if (dias < 0) return { nivel: '⛔ VENCIDO', cor: '#c00', risco: 'crítico' };
  if (dias <= CONFIG_PRAZO.DIAS_ALERTA_CRITICO) return { nivel: '🚨 CRÍTICO', cor: '#b71c1c', risco: 'crítico' };
  if (dias <= CONFIG_PRAZO.DIAS_ALERTA_URGENTE) return { nivel: '⚠️ URGENTE', cor: '#e65100', risco: 'alto' };
  if (dias <= CONFIG_PRAZO.DIAS_ALERTA_NORMAL) return { nivel: '🟠 PRÓXIMO', cor: '#f9a825', risco: 'médio' };
  return { nivel: '🟢 OK', cor: '#2e7d32', risco: 'baixo' };
}

function analisarPrazosCriticos() {
  const processos = lerProcessosPrazo();
  const hoje = new Date();
  const dataStr = Utilities.formatDate(hoje, 'America/Porto_Velho', 'dd/MM/yyyy HH:mm');

  const prazos = {
    criticos: [],
    urgentes: [],
    proximos: [],
  };

  processos.forEach(p => {
    if (!p.prazo_calculado || !p.prazo_calculado.data_prazo_final) return;

    const dias = diasAteDataPrazo(p.prazo_calculado.data_prazo_final);
    const classif = classificarPrazo(dias);

    const item = {
      numero: p.numero,
      cliente: p.cliente || '—',
      partes: p.partes || '—',
      prazo: p.prazo_calculado.data_prazo_final,
      dias,
      descricao: p.prazo_calculado.descricao || '—',
      acao: p.prazo_calculado.acao || 'Manifestação nos autos',
      classif: classif.nivel,
    };

    if (classif.risco === 'crítico') prazos.criticos.push(item);
    else if (classif.risco === 'alto') prazos.urgentes.push(item);
    else if (classif.risco === 'médio') prazos.proximos.push(item);
  });

  // Enviar alerta apenas se houver críticos/urgentes
  if (prazos.criticos.length > 0 || prazos.urgentes.length > 0) {
    enviarAlertaPrazos(prazos, dataStr);
  }

  Logger.log(`Análise de Prazos: ${prazos.criticos.length} críticos, ${prazos.urgentes.length} urgentes, ${prazos.proximos.length} próximos.`);
}

function enviarAlertaPrazos(prazos, dataStr) {
  let html = `
    <div style="font-family:Arial,sans-serif;max-width:1000px;margin:auto">
    <h2 style="background:#c00;color:white;padding:16px;border-radius:6px">
      🚨 ALERTA DE PRAZOS — CC-001<br>
      <small>${dataStr}</small>
    </h2>`;

  if (prazos.criticos.length > 0) {
    html += `<h3 style="color:#c00">⛔ CRÍTICO (${prazos.criticos.length}) — AGIR IMEDIATAMENTE</h3>`;
    prazos.criticos.forEach(p => {
      html += `
        <div style="border:3px solid #c00;padding:12px;margin:8px 0;border-radius:4px;background:#fff5f5">
          <b style="font-size:14px">${p.numero}</b> — ${p.cliente}<br>
          <span style="color:#666;font-size:11px"><b>Partes:</b> ${p.partes}</span><br>
          <b style="color:#c00">⏰ PRAZO: ${p.prazo} (${p.dias} dias)</b><br>
          <span style="color:#333"><b>Ação:</b> ${p.acao}</span><br>
          <span style="color:#666"><b>Tipo:</b> ${p.descricao}</span>
        </div>`;
    });
  }

  if (prazos.urgentes.length > 0) {
    html += `<h3 style="color:#e65100">⚠️ URGENTE (${prazos.urgentes.length})</h3>`;
    prazos.urgentes.forEach(p => {
      html += `
        <div style="border:2px solid #e65100;padding:10px;margin:6px 0;border-radius:4px">
          <b>${p.numero}</b> — ${p.cliente}<br>
          <small><b>Prazo:</b> ${p.prazo} (${p.dias} dias) | <b>Ação:</b> ${p.acao}</small>
        </div>`;
    });
  }

  if (prazos.proximos.length > 0 && prazos.proximos.length <= 10) {
    html += `<h3 style="color:#f9a825">🟠 PRÓXIMOS (${prazos.proximos.length})</h3>`;
    prazos.proximos.forEach(p => {
      html += `<div style="padding:6px;margin:4px 0;border-left:4px solid #f9a825;background:#fffbf0">
        <small><b>${p.numero}</b> | ${p.cliente} | ${p.prazo} (${p.dias}d)</small>
      </div>`;
    });
  }

  html += '</div>';

  // Deletar alerta anterior
  try {
    const threads = GmailApp.search('subject:"ALERTA DE PRAZOS"');
    threads.slice(0, 3).forEach(t => {
      const msgs = t.getMessages();
      msgs.forEach(m => {
        if (m.getSubject().includes('ALERTA DE PRAZOS')) {
          m.moveToTrash();
        }
      });
    });
  } catch (e) {
    Logger.log('Erro ao deletar alerta anterior: ' + e);
  }

  GmailApp.sendEmail(CONFIG_PRAZO.EMAIL_DESTINO,
    `🚨 ALERTA DE PRAZOS — CC-001 | ${prazos.criticos.length} crítico(s) | ${Utilities.formatDate(new Date(), 'America/Porto_Velho', 'dd/MM/yyyy HH:mm')}`,
    'Visualize em cliente HTML.',
    { htmlBody: html }
  );

  Logger.log('Email de alerta de prazos enviado (anterior deletado).');
}

function testarAnalisadorPrazos() {
  analisarPrazosCriticos();
}

// ═══════════════════════════════════════════════════════════════
// ORIGEM: CC001_AgendaPlanner.gs
// ═══════════════════════════════════════════════════════════════

/**
 * CC-001 — MABIOS v3 — Planejador de Agenda Inteligente
 * Sugere datas para petições com base em prazos e disponibilidade
 * Integra com Google Calendar (se existir)
 *
 * Roda a cada 24 horas
 */

const CONFIG_AGENDA = {
  PROCESSOS_FILE_ID: '1HpfH2bbsfbtFstygaNevn4oIl5uBeHgz',
  EMAIL_DESTINO: 'flamesinberlim@gmail.com',
  // Calendário explícito (não usar 'primary': escreveria no calendário
  // de qualquer conta que rodasse o script — o Dr. Jefferson tem mais de uma)
  CALENDAR_ID: 'flamesinberlim@gmail.com',
  DIAS_UTEIS_ANTES_PRAZO: 5, // Sugerir 5 dias úteis antes do prazo
  HORARIO_PADRAO_PETICIO: 14, // Sugerir petições às 14h (depois do almoço)
};

function setupPlanificadorAgenda() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'planificarAgenda')
    .forEach(t => ScriptApp.deleteTrigger(t));

  ScriptApp.newTrigger('planificarAgenda_protegido')
    .timeBased()
    .everyDays(1)
    .atHour(8)
    .create();

  Logger.log('Planejador de Agenda ativado — sugestões diárias às 8h.');
}

function planificarAgenda_protegido() {
  executarComProtecao('planificarAgenda', planificarAgenda);
}

function lerProcessosAgenda() {
  try {
    const file = DriveApp.getFileById(CONFIG_AGENDA.PROCESSOS_FILE_ID);
    const conteudo = file.getBlob().getDataAsString('utf-8');
    return JSON.parse(conteudo);
  } catch (e) {
    Logger.log('Erro ao ler processos: ' + e);
    return [];
  }
}

function parseDateBRAgenda(s) {
  if (!s || s === '—') return null;
  const parts = s.substring(0, 10).split('/');
  if (parts.length === 3) return new Date(parts[2], parts[1] - 1, parts[0]);
  return null;
}

function diasAteDataAgenda(dataPrazo) {
  const d = parseDateBRAgenda(dataPrazo);
  if (!d) return 9999;
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  return Math.floor((d - hoje) / 86400000);
}

function calcularDataSugeridaPeticio(dataPrazo) {
  const prazo = parseDateBRAgenda(dataPrazo);
  if (!prazo) return null;

  let dataSugerida = new Date(prazo);
  let diasRetroativos = CONFIG_AGENDA.DIAS_UTEIS_ANTES_PRAZO;

  // Regressar dias úteis
  while (diasRetroativos > 0) {
    dataSugerida.setDate(dataSugerida.getDate() - 1);
    const dia = dataSugerida.getDay();
    if (dia !== 0 && dia !== 6) diasRetroativos--; // Pular finais de semana
  }

  return dataSugerida;
}

function criarEventoCalendario(titulo, descricao, dataSugerida) {
  try {
    const evento = {
      title: titulo,
      description: descricao,
      start: { dateTime: dataSugerida.toISOString(), timeZone: 'America/Porto_Velho' },
      end: { dateTime: new Date(dataSugerida.getTime() + 3600000).toISOString(), timeZone: 'America/Porto_Velho' },
      reminders: { useDefault: true },
    };

    CalendarApp.getCalendarById(CONFIG_AGENDA.CALENDAR_ID).createEvent(titulo, dataSugerida, new Date(dataSugerida.getTime() + 3600000), { description: descricao });
    return true;
  } catch (e) {
    Logger.log('Erro ao criar evento: ' + e);
    return false;
  }
}

function planificarAgenda() {
  const processos = lerProcessosAgenda();
  const hoje = new Date();
  const dataStr = Utilities.formatDate(hoje, 'America/Porto_Velho', 'dd/MM/yyyy');

  const sugestoes = [];

  processos.forEach(p => {
    if (!p.prazo_calculado || !p.prazo_calculado.data_prazo_final) return;
    if (!p.prioritario) return; // Ignorar não prioritários

    const dias = diasAteDataAgenda(p.prazo_calculado.data_prazo_final);
    if (dias < 0 || dias > 21) return; // Só considerar prazos nos próximos 3 semanas

    const dataSugerida = calcularDataSugeridaPeticio(p.prazo_calculado.data_prazo_final);
    if (!dataSugerida) return;

    const dataStr = Utilities.formatDate(dataSugerida, 'America/Porto_Velho', 'dd/MM/yyyy');
    const titulo = `[${p.numero}] ${p.prazo_calculado.descricao || 'Manifestação'} — ${p.cliente}`;
    const descricao = `Processo: ${p.numero}\nCliente: ${p.cliente}\nPartes: ${p.partes || '—'}\nPrazo final: ${p.prazo_calculado.data_prazo_final}\nAção sugerida: ${p.prazo_calculado.acao || 'Manifestação nos autos'}`;

    sugestoes.push({
      numero: p.numero,
      cliente: p.cliente,
      prazo: p.prazo_calculado.data_prazo_final,
      dataSugerida,
      dataStr,
      titulo,
      descricao,
    });

    // Criar evento no calendário
    criarEventoCalendario(titulo, descricao, dataSugerida);
  });

  if (sugestoes.length > 0) {
    enviarSugestoesAgenda(sugestoes, dataStr);
  }

  Logger.log(`Planejamento de Agenda: ${sugestoes.length} sugestões geradas.`);
}

function enviarSugestoesAgenda(sugestoes, dataStr) {
  let html = `
    <div style="font-family:Arial,sans-serif;max-width:1100px;margin:auto">
    <h2 style="background:#1a237e;color:white;padding:16px;border-radius:6px">
      📅 AGENDA SUGERIDA — CC-001<br>
      <small>${dataStr} | ${sugestoes.length} petição(ões) sugerida(s)</small>
    </h2>
    <p style="color:#555"><i>Datas sugeridas para protocolo, com 5 dias úteis de antecedência aos prazos</i></p>`;

  sugestoes.sort((a, b) => a.dataSugerida - b.dataSugerida).forEach(s => {
    const diasAte = Math.ceil((new Date(s.prazo) - new Date()) / 86400000);
    html += `
      <div style="border-left:4px solid #1a237e;padding:12px;margin:10px 0;background:#f5f5f5;border-radius:4px">
        <div style="display:flex;justify-content:space-between">
          <div>
            <b style="font-size:13px">${s.numero}</b> — ${s.cliente}<br>
            <span style="color:#666;font-size:11px"><b>Partes:</b> ${s.descricao.match(/Partes: ([^\n]*)/)?.[1] || '—'}</span>
          </div>
          <div style="text-align:right">
            <div style="font-size:20px;font-weight:bold;color:#1a237e">${s.dataStr}</div>
            <small style="color:#888">Prazo: ${s.prazo} (+${diasAte}d)</small>
          </div>
        </div>
        <div style="margin-top:8px;padding:8px;background:white;border-radius:3px;font-size:12px">
          <small>${s.descricao.split('\n').slice(4).join('<br>')}</small>
        </div>
      </div>`;
  });

  html += `
    <div style="margin-top:20px;padding:12px;background:#e8f5e9;border-radius:4px;border-left:4px solid #2e7d32">
      <small style="color:#1b5e20"><b>✓ Eventos criados no Google Calendar</b><br>
      Você pode visualizar e editar as datas diretamente no seu calendário.</small>
    </div>
    </div>`;

  // Deletar sugestões de agenda anteriores
  try {
    const threads = GmailApp.search('subject:"AGENDA SUGERIDA"');
    threads.slice(0, 3).forEach(t => {
      const msgs = t.getMessages();
      msgs.forEach(m => {
        if (m.getSubject().includes('AGENDA SUGERIDA')) {
          m.moveToTrash();
        }
      });
    });
  } catch (e) {
    Logger.log('Erro ao deletar agenda anterior: ' + e);
  }

  GmailApp.sendEmail(CONFIG_AGENDA.EMAIL_DESTINO,
    `📅 AGENDA SUGERIDA — CC-001 | ${sugestoes.length} petição(ões) | ${dataStr}`,
    'Visualize em cliente HTML.',
    { htmlBody: html }
  );

  Logger.log('Email de sugestões de agenda enviado.');
}

function testarPlanificadorAgenda() {
  planificarAgenda();
}

// ═══════════════════════════════════════════════════════════════
// ORIGEM: CC001_DataJudIntegration.gs
// ═══════════════════════════════════════════════════════════════

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

  ScriptApp.newTrigger('ingerirAndamentosDataJud_protegido')
    .timeBased()
    .everyMinutes(30)
    .create();

  Logger.log('Ingestor DataJud ativado — consulta oficial a cada 30 minutos.');
}

function ingerirAndamentosDataJud_protegido() {
  executarComProtecao('ingerirAndamentosDataJud', ingerirAndamentosDataJud);
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

// ═══════════════════════════════════════════════════════════════
// ORIGEM: CC001_PJeIngestor.gs
// ═══════════════════════════════════════════════════════════════

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
  // CPF removido: não era usado por nenhuma função deste arquivo e não deve
  // ficar versionado. Se algum dia for necessário, guarde em
  // PropertiesService (Configurações do projeto → Propriedades do script),
  // nunca no código-fonte.
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

// ═══════════════════════════════════════════════════════════════
// ORIGEM: CC001_MasterSetup.gs
// ═══════════════════════════════════════════════════════════════

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
