#!/usr/bin/env node

const { program } = require('commander');
const chalk = require('chalk');

const mockAlerts = [
  {
    id: "INC-2024-001",
    severity: "critical",
    title: "Cyber-Enabled Wire Fraud",
    timestamp: "2024-10-14T14:23:15Z",
    status: "new",
    confidence: 0.94,
    user: "john.smith@acmebank.com",
    signals: [
      "New device from Russia",
      "Failed MFA attempts",
      "EDR malware beacon detected",
      "$150,000 wire to new beneficiary"
    ]
  },
  {
    id: "INC-2024-002",
    severity: "high",
    title: "Account Takeover Attempt",
    timestamp: "2024-10-14T13:45:22Z",
    status: "investigating",
    confidence: 0.87,
    user: "maria.garcia@acmebank.com",
    signals: [
      "Login from unusual geo-location",
      "Password reset requested",
      "Browser fingerprint mismatch"
    ]
  },
  {
    id: "INC-2024-003",
    severity: "medium",
    title: "Anomalous Transaction Pattern",
    timestamp: "2024-10-14T12:10:08Z",
    status: "new",
    confidence: 0.72,
    user: "robert.chen@acmebank.com",
    signals: [
      "Multiple small transfers",
      "Unusual time of activity (3 AM)",
      "New payee added"
    ]
  }
];

const getSeverityColor = (severity) => {
  switch (severity) {
    case 'critical': return chalk.red;
    case 'high': return chalk.yellow;
    case 'medium': return chalk.blue;
    case 'low': return chalk.green;
    default: return chalk.white;
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case 'new': return chalk.red;
    case 'investigating': return chalk.yellow;
    case 'resolved': return chalk.green;
    default: return chalk.white;
  }
};

program
  .name('sec-alerts')
  .description('CLI for Unified Security Alert Dashboard')
  .version('1.0.0');

program
  .command('list')
  .description('List all security alerts')
  .option('-s, --severity <severity>', 'Filter by severity (critical, high, medium, low)')
  .option('-t, --status <status>', 'Filter by status (new, investigating, resolved)')
  .action((options) => {
    let filtered = mockAlerts;

    if (options.severity) {
      filtered = filtered.filter(a => a.severity === options.severity);
    }
    if (options.status) {
      filtered = filtered.filter(a => a.status === options.status);
    }

    console.log(chalk.bold.cyan('\n🛡️  UNIFIED SECURITY ALERT DASHBOARD\n'));
    console.log(chalk.gray(`Showing ${filtered.length} correlated incidents\n`));

    filtered.forEach((alert, idx) => {
      const severityColor = getSeverityColor(alert.severity);
      const statusColor = getStatusColor(alert.status);

      console.log(severityColor.bold(`[${alert.severity.toUpperCase()}]`), chalk.bold(alert.title));
      console.log(chalk.gray(`  ID: ${alert.id} | User: ${alert.user}`));
      console.log(statusColor(`  Status: ${alert.status.toUpperCase()}`), chalk.cyan(`| Confidence: ${(alert.confidence * 100).toFixed(0)}%`));
      console.log(chalk.gray(`  Time: ${new Date(alert.timestamp).toLocaleString()}`));
      console.log(chalk.gray(`  Signals (${alert.signals.length}):`));
      alert.signals.forEach(signal => {
        console.log(chalk.gray(`    • ${signal}`));
      });
      console.log('');
    });
  });

program
  .command('investigate <id>')
  .description('Investigate a specific alert')
  .action((id) => {
    const alert = mockAlerts.find(a => a.id === id);
    if (!alert) {
      console.log(chalk.red(`Alert ${id} not found`));
      return;
    }
    console.log(chalk.cyan.bold('\n🔍 INVESTIGATING ALERT\n'));
    console.log(JSON.stringify(alert, null, 2));
    console.log(chalk.green('\n✓ Investigation timeline would be shown here...'));
  });

program
  .command('stats')
  .description('Show alert statistics')
  .action(() => {
    const critical = mockAlerts.filter(a => a.severity === 'critical').length;
    const high = mockAlerts.filter(a => a.severity === 'high').length;
    const medium = mockAlerts.filter(a => a.severity === 'medium').length;
    const newAlerts = mockAlerts.filter(a => a.status === 'new').length;

    console.log(chalk.bold.cyan('\n📊 ALERT STATISTICS\n'));
    console.log(chalk.red.bold(`Critical: ${critical}`));
    console.log(chalk.yellow.bold(`High: ${high}`));
    console.log(chalk.blue.bold(`Medium: ${medium}`));
    console.log(chalk.gray(`\nNew Alerts: ${newAlerts}`));
    console.log('');
  });

program.parse();
