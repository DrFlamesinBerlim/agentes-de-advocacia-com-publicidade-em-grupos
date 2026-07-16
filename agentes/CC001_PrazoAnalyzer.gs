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

  ScriptApp.newTrigger('analisarPrazosCriticos')
    .timeBased()
    .everyHours(1)
    .create();

  Logger.log('Analisador de Prazos ativado — verifica a cada hora.');
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

  GmailApp.sendEmail(CONFIG_PRAZO.EMAIL_DESTINO,
    `🚨 ALERTA DE PRAZOS — CC-001 | ${prazos.criticos.length} crítico(s) | ${Utilities.formatDate(new Date(), 'America/Porto_Velho', 'dd/MM/yyyy HH:mm')}`,
    'Visualize em cliente HTML.',
    { htmlBody: html }
  );

  Logger.log('Email de alerta de prazos enviado.');
}

function testarAnalisadorPrazos() {
  analisarPrazosCriticos();
}
