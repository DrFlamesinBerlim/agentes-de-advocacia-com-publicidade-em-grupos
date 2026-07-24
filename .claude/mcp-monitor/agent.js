#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const Monitor = require('./monitor');
const MCPTaskTracker = require('./task-integration');

const tracker = new MCPTaskTracker();

async function generateReport() {
  console.log('\n' + '='.repeat(60));
  console.log('🤖 MCP Monitor Agent - Health Check Routine');
  console.log('='.repeat(60));

  try {
    // Executar checks
    const { results, history } = await Monitor.checkAllMCPs();

    // Gerar relatório
    const report = await Monitor.generateReport(results, history);

    // Criar tarefa de check
    const checkTask = tracker.createCheckTask(results);
    console.log(`\n✅ Check task created: ${checkTask.id}`);

    // Criar tarefas de alerta se necessário
    if (report.alerts.length > 0) {
      const alertTask = tracker.createAlertTask(report.alerts);
      console.log(`⚠️  Alert task created: ${alertTask.id}`);
      console.log(`   Priority: ${alertTask.priority}`);
      console.log(`   Alerts: ${alertTask.alerts.length}`);
    }

    // Resumo final
    const summary = tracker.getTaskSummary();
    console.log('\n' + '-'.repeat(60));
    console.log('📊 MONITOR SUMMARY:');
    console.log('-'.repeat(60));
    console.log(`Total Tasks Tracked:    ${summary.total_tasks}`);
    console.log(`Completed Checks:       ${summary.completed_checks}`);
    console.log(`Open Alerts:            ${summary.open_alerts}`);
    console.log(`High Priority:          ${summary.high_priority}`);
    console.log(`\nMCP Status:`);
    console.log(`  ✅ Healthy:           ${report.details.filter(r => r.status === 'healthy').length}`);
    console.log(`  ❌ Failed:            ${report.details.filter(r => r.status === 'failed').length}`);

    if (report.alerts.length > 0) {
      console.log('\n⚠️  ALERTS:');
      report.alerts.forEach(alert => {
        console.log(`  - ${alert.mcp}: ${alert.failure_count} failures (${alert.severity})`);
      });
    }

    console.log('\n' + '='.repeat(60));
    console.log(`Next check scheduled in 18 hours`);
    console.log('='.repeat(60) + '\n');

    return report;
  } catch (error) {
    console.error('❌ Monitor error:', error.message);
    process.exit(1);
  }
}

// Executar se chamado diretamente
if (require.main === module) {
  generateReport().catch(console.error);
}

module.exports = { generateReport };
