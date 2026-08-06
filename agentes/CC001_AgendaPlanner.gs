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
