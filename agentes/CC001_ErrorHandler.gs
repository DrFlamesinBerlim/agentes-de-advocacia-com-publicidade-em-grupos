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
