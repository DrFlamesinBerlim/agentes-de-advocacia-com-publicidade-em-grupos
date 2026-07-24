const fs = require('fs');
const path = require('path');

class MCPDashboard {
  constructor() {
    this.logsDir = path.join(__dirname, 'logs');
    this.statusFile = path.join(this.logsDir, 'mcp-status.json');
  }

  loadCurrentStatus() {
    if (!fs.existsSync(this.statusFile)) {
      return {};
    }
    return JSON.parse(fs.readFileSync(this.statusFile, 'utf-8'));
  }

  generateHTMLDashboard() {
    const status = this.loadCurrentStatus();
    const timestamp = new Date().toISOString();

    const mcpRows = Object.entries(status).map(([name, checks]) => {
      const lastCheck = checks[checks.length - 1];
      const recentChecks = checks.slice(-5);
      const healthyCount = recentChecks.filter(c => c.status === 'healthy').length;
      const uptime = ((healthyCount / recentChecks.length) * 100).toFixed(1);

      const statusColor = lastCheck.status === 'healthy' ? '#4CAF50' : '#f44336';
      const statusIcon = lastCheck.status === 'healthy' ? '✅' : '❌';

      return `
        <tr>
          <td>${name}</td>
          <td><span style="color: ${statusColor}; font-weight: bold;">${statusIcon} ${lastCheck.status}</span></td>
          <td>${lastCheck.response_time || 'N/A'}ms</td>
          <td>${uptime}%</td>
          <td>${new Date(lastCheck.timestamp).toLocaleString()}</td>
        </tr>
      `;
    }).join('');

    const html = `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MCP Health Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }
    .header h1 {
      font-size: 28px;
      margin-bottom: 10px;
    }
    .header p {
      opacity: 0.9;
      font-size: 14px;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      padding: 30px;
      background: #f5f5f5;
      border-bottom: 1px solid #ddd;
    }
    .stat-card {
      background: white;
      padding: 20px;
      border-radius: 8px;
      text-align: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stat-card .number {
      font-size: 32px;
      font-weight: bold;
      color: #667eea;
      margin: 10px 0;
    }
    .stat-card .label {
      font-size: 12px;
      color: #666;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 0;
    }
    th {
      background: #f5f5f5;
      padding: 15px;
      text-align: left;
      font-weight: 600;
      color: #333;
      border-bottom: 2px solid #ddd;
      font-size: 12px;
      text-transform: uppercase;
    }
    td {
      padding: 15px;
      border-bottom: 1px solid #eee;
      font-size: 14px;
    }
    tr:hover {
      background: #f9f9f9;
    }
    .footer {
      padding: 20px 30px;
      background: #f5f5f5;
      border-top: 1px solid #ddd;
      font-size: 12px;
      color: #666;
      text-align: right;
    }
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
    }
    .badge.healthy {
      background: #c8e6c9;
      color: #2e7d32;
    }
    .badge.failed {
      background: #ffcdd2;
      color: #c62828;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🤖 MCP Health Monitor Dashboard</h1>
      <p>Real-time health status of all MCP servers</p>
    </div>

    <div class="stats">
      <div class="stat-card">
        <div class="label">Total MCPs</div>
        <div class="number">${Object.keys(status).length}</div>
      </div>
      <div class="stat-card">
        <div class="label">Healthy</div>
        <div class="number" style="color: #4CAF50;">
          ${Object.values(status).filter(checks => checks[checks.length - 1]?.status === 'healthy').length}
        </div>
      </div>
      <div class="stat-card">
        <div class="label">Failed</div>
        <div class="number" style="color: #f44336;">
          ${Object.values(status).filter(checks => checks[checks.length - 1]?.status === 'failed').length}
        </div>
      </div>
      <div class="stat-card">
        <div class="label">Last Update</div>
        <div class="number" style="font-size: 14px; color: #666;">
          ${new Date(timestamp).toLocaleTimeString('pt-BR')}
        </div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>MCP Name</th>
          <th>Status</th>
          <th>Response Time</th>
          <th>Uptime (5 checks)</th>
          <th>Last Check</th>
        </tr>
      </thead>
      <tbody>
        ${mcpRows}
      </tbody>
    </table>

    <div class="footer">
      📊 Dashboard gerado em ${new Date(timestamp).toLocaleString('pt-BR')} | Auto-refresh a cada 18 horas
    </div>
  </div>
</body>
</html>
    `;

    return html;
  }

  saveDashboard() {
    const dashboardPath = path.join(this.logsDir, 'dashboard.html');
    const html = this.generateHTMLDashboard();
    fs.writeFileSync(dashboardPath, html);
    console.log(`📊 Dashboard salvo em: ${dashboardPath}`);
    return dashboardPath;
  }
}

if (require.main === module) {
  const dashboard = new MCPDashboard();
  dashboard.saveDashboard();
}

module.exports = MCPDashboard;
