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
  ScriptApp.newTrigger('enviarRelatorioDiario')
    .timeBased()
    .everyDays(1)
    .atHour(CONFIG.HORA_RELATORIO_DIARIO)
    .create();

  // Monitoramento de alterações a cada hora
  ScriptApp.newTrigger('monitorarAlteracoes')
    .timeBased()
    .everyHours(1)
    .create();

  Logger.log('Gatilhos criados com sucesso. CC-001 ativo permanentemente.');
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
      const prazoStr = p.prazo && p.prazo.data_prazo_final
        ? `<br><span style="color:#c00;font-weight:bold">⚠️ PRAZO: ${p.prazo.data_prazo_final} — ${p.prazo.descricao || ''}</span>`
        : '';
      return `<tr>
        <td style="font-family:monospace;font-size:12px">${p.numero}</td>
        <td>${p.cliente || '—'}</td>
        <td>${p.ultima_mov || '—'}</td>
        <td style="text-align:center"><b>${p.dias}d</b></td>
        <td>${(p.mov_desc || '—').substring(0, 80)}${prazoStr}</td>
      </tr>`;
    }).join('');
    return `<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;width:100%;font-size:13px">
      <thead style="background:${cor};color:white">
        <tr><th>Processo</th><th>Cliente</th><th>Última Mov.</th><th>Dias</th><th>Movimentação</th></tr>
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

  let corpo = `
    <div style="font-family:Arial,sans-serif;max-width:1100px;margin:auto">
    <h2 style="background:#1a237e;color:white;padding:16px;border-radius:6px">
      ⚖️ CC-001 — Relatório Diário de Processos<br>
      <small style="font-size:14px">De Brito Advocacia | Dr. Jefferson Silva de Brito | OAB/RO 2952</small><br>
      <small style="font-size:13px">Data: ${dataStr} | Total: ${processos.length} processos</small>
    </h2>`;

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

  GmailApp.sendEmail(
    CONFIG.EMAIL_DESTINO,
    `[CC-001] Relatório Diário — De Brito Advocacia | ${dataStr}`,
    'Visualize em cliente de email com suporte a HTML.',
    { htmlBody: html }
  );

  // Salva snapshot atual para comparação horária
  const props = PropertiesService.getScriptProperties();
  const conteudo = JSON.stringify(processos);
  props.setProperty(CONFIG.HASH_PROP_KEY, calcularHash(conteudo));
  props.setProperty(CONFIG.SNAPSHOT_PROP_KEY, conteudo);

  Logger.log(`[CC-001] Relatório diário enviado — ${processos.length} processos — ${dataStr}`);
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
