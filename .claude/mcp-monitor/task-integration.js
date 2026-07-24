const fs = require('fs');
const path = require('path');

class MCPTaskTracker {
  constructor() {
    this.tasksDir = path.join(__dirname, 'tasks');
    if (!fs.existsSync(this.tasksDir)) {
      fs.mkdirSync(this.tasksDir, { recursive: true });
    }
  }

  createCheckTask(results) {
    const taskId = `mcp-check-${Date.now()}`;
    const task = {
      id: taskId,
      type: 'mcp-health-check',
      title: `MCP Health Check Report`,
      status: 'completed',
      timestamp: new Date().toISOString(),
      results: {
        healthy_mcps: results.filter(r => r.status === 'healthy').length,
        failed_mcps: results.filter(r => r.status === 'failed').length,
        total_mcps: results.length
      },
      details: results
    };

    fs.writeFileSync(
      path.join(this.tasksDir, `${taskId}.json`),
      JSON.stringify(task, null, 2)
    );

    return task;
  }

  createAlertTask(alerts) {
    if (alerts.length === 0) return null;

    const taskId = `mcp-alert-${Date.now()}`;
    const task = {
      id: taskId,
      type: 'mcp-alert',
      title: `MCP Issues Detected - ${alerts.length} alert(s)`,
      status: 'open',
      priority: alerts.some(a => a.severity === 'critical') ? 'high' : 'medium',
      timestamp: new Date().toISOString(),
      alerts: alerts,
      required_action: true
    };

    fs.writeFileSync(
      path.join(this.tasksDir, `${taskId}.json`),
      JSON.stringify(task, null, 2)
    );

    return task;
  }

  listTasks() {
    const tasks = [];
    if (!fs.existsSync(this.tasksDir)) return tasks;

    const files = fs.readdirSync(this.tasksDir);
    for (const file of files) {
      const task = JSON.parse(
        fs.readFileSync(path.join(this.tasksDir, file), 'utf-8')
      );
      tasks.push(task);
    }

    return tasks.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }

  getTaskSummary() {
    const tasks = this.listTasks();
    return {
      total_tasks: tasks.length,
      completed_checks: tasks.filter(t => t.type === 'mcp-health-check').length,
      open_alerts: tasks.filter(t => t.type === 'mcp-alert' && t.status === 'open').length,
      high_priority: tasks.filter(t => t.priority === 'high').length
    };
  }
}

module.exports = MCPTaskTracker;
