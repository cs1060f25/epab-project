export const mockAlerts = [
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
    ],
    signalCount: 4,
    description: "Multiple risk signals detected: unauthorized device, endpoint compromise, and high-value transaction."
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
    ],
    signalCount: 3,
    description: "Suspicious login activity detected with geographic and device anomalies."
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
    ],
    signalCount: 3,
    description: "Transaction behavior deviates from established baseline pattern."
  },
  {
    id: "INC-2024-004",
    severity: "critical",
    title: "Privileged Account Compromise",
    timestamp: "2024-10-14T11:30:44Z",
    status: "investigating",
    confidence: 0.91,
    user: "admin@acmebank.com",
    signals: [
      "Lateral movement detected",
      "Privilege escalation attempt",
      "Access to sensitive data repositories",
      "Connection to known C2 server"
    ],
    signalCount: 4,
    description: "Admin account showing signs of compromise with active threat actor behavior."
  },
  {
    id: "INC-2024-005",
    severity: "low",
    title: "Suspicious Email Activity",
    timestamp: "2024-10-14T10:15:30Z",
    status: "resolved",
    confidence: 0.58,
    user: "jane.wilson@acmebank.com",
    signals: [
      "Phishing email clicked",
      "Suspicious attachment opened"
    ],
    signalCount: 2,
    description: "User interacted with potential phishing content. Endpoint scan clean."
  },
  {
    id: "INC-2024-006",
    severity: "high",
    title: "Data Exfiltration Risk",
    timestamp: "2024-10-14T09:22:18Z",
    status: "new",
    confidence: 0.83,
    user: "david.thompson@acmebank.com",
    signals: [
      "Large data download",
      "USB device connected",
      "After-hours access"
    ],
    signalCount: 3,
    description: "Unusual data access pattern suggesting potential insider threat or compromised credentials."
  }
];
