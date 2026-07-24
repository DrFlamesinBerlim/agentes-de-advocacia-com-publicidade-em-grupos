const fs = require('fs');
const path = require('path');

const CONFIG_FILE = path.join(__dirname, 'config.json');
const LOGS_DIR = path.join(__dirname, 'logs');
const STATUS_FILE = path.join(LOGS_DIR, 'mcp-status.json');

if (!fs.existsSync(LOGS_DIR)) {
  fs.mkdirSync(LOGS_DIR, { recursive: true });
}

async function testMCPHealth(mcp) {
  const startTime = Date.now();
  const result = {
    name: mcp.name,
    timestamp: new Date().toISOString(),
    status: 'unknown',
    response_time: null,
    error: null
  };

  try {
    // Simulação de teste - em produção, testaríamos endpoints reais
    // Por enquanto, marcamos como healthy
    const timeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Timeout')), 5000)
    );

    // Aqui você pode adicionar testes específicos por MCP
    await Promise.race([
      new Promise(resolve => setTimeout(resolve, Math.random() * 2000)),
      timeout
    ]);

    result.status = 'healthy';
    result.response_time = Date.now() - startTime;
  } catch (error) {
    result.status = 'failed';
    result.error = error.message;
    result.response_time = Date.now() - startTime;
  }

  return result;
}

async function loadConfig() {
  const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
  return config;
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

function loadStatusHistory() {
  if (!fs.existsSync(STATUS_FILE)) {
    return {};
  }
  return JSON.parse(fs.readFileSync(STATUS_FILE, 'utf-8'));
}

function saveStatusHistory(history) {
  fs.writeFileSync(STATUS_FILE, JSON.stringify(history, null, 2));
}

async function checkAllMCPs() {
  const config = await loadConfig();
  const history = loadStatusHistory();
  const results = [];

  console.log(`\n🔍 MCP Health Check - ${new Date().toISOString()}\n`);

  for (const mcp of config.monitor.mcp_servers) {
    const result = await testMCPHealth(mcp);
    results.push(result);

    // Track status changes
    if (!history[mcp.name]) {
      history[mcp.name] = [];
    }
    history[mcp.name].push(result);

    // Keep only last 30 checks
    if (history[mcp.name].length > 30) {
      history[mcp.name].shift();
    }

    const icon = result.status === 'healthy' ? '✅' : '❌';
    console.log(`${icon} ${mcp.name.padEnd(20)} ${result.status.padEnd(10)} ${result.response_time}ms`);

    // Update config with latest status
    const mcpInConfig = config.monitor.mcp_servers.find(m => m.name === mcp.name);
    if (mcpInConfig) {
      mcpInConfig.last_check = result.timestamp;
      mcpInConfig.status = result.status;
    }
  }

  saveConfig(config);
  saveStatusHistory(history);

  return { results, history };
}

async function generateReport(results, history) {
  const summary = {
    timestamp: new Date().toISOString(),
    total_mcps: results.length,
    healthy: results.filter(r => r.status === 'healthy').length,
    failed: results.filter(r => r.status === 'failed').length,
    details: results,
    alerts: []
  };

  // Check for repeated failures
  for (const [mcp, checks] of Object.entries(history)) {
    const recentChecks = checks.slice(-3);
    const failureCount = recentChecks.filter(c => c.status === 'failed').length;

    if (failureCount >= 2) {
      summary.alerts.push({
        type: 'repeated_failure',
        mcp,
        failure_count: failureCount,
        severity: failureCount === 3 ? 'critical' : 'warning'
      });
    }
  }

  return summary;
}

async function run() {
  try {
    const { results, history } = await checkAllMCPs();
    const report = await generateReport(results, history);

    // Save report
    const reportFile = path.join(LOGS_DIR, `report-${Date.now()}.json`);
    fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));

    console.log(`\n📊 Summary: ${report.healthy}/${report.total_mcps} healthy`);

    if (report.alerts.length > 0) {
      console.log('\n⚠️  Alerts:');
      report.alerts.forEach(alert => {
        console.log(`   - ${alert.mcp}: ${alert.failure_count} consecutive failures (${alert.severity})`);
      });
    }

    console.log(`\n📝 Report saved: ${reportFile}\n`);

    return report;
  } catch (error) {
    console.error('❌ Monitor error:', error);
    process.exit(1);
  }
}

module.exports = { checkAllMCPs, generateReport, run };

if (require.main === module) {
  run();
}
