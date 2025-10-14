'use client';

import { useState } from 'react';

const mockAlerts = [
  {
    id: "INC-2024-001",
    severity: "critical",
    title: "Cyber-Enabled Wire Fraud",
    timestamp: "2024-10-14T14:23:15Z",
    status: "new",
    confidence: 0.94,
    user: "john.smith@acmebank.com",
    signals: ["New device from Russia", "Failed MFA attempts", "EDR malware beacon detected", "$150,000 wire to new beneficiary"],
  },
  {
    id: "INC-2024-002",
    severity: "high",
    title: "Account Takeover Attempt",
    timestamp: "2024-10-14T13:45:22Z",
    status: "investigating",
    confidence: 0.87,
    user: "maria.garcia@acmebank.com",
    signals: ["Login from unusual geo-location", "Password reset requested", "Browser fingerprint mismatch"],
  },
  {
    id: "INC-2024-003",
    severity: "medium",
    title: "Anomalous Transaction Pattern",
    timestamp: "2024-10-14T12:10:08Z",
    status: "new",
    confidence: 0.72,
    user: "robert.chen@acmebank.com",
    signals: ["Multiple small transfers", "Unusual time of activity (3 AM)", "New payee added"],
  },
  {
    id: "INC-2024-004",
    severity: "critical",
    title: "Privileged Account Compromise",
    timestamp: "2024-10-14T11:30:44Z",
    status: "investigating",
    confidence: 0.91,
    user: "admin@acmebank.com",
    signals: ["Lateral movement detected", "Privilege escalation attempt", "Access to sensitive data repositories"],
  }
];

export default function Home() {
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredAlerts = mockAlerts.filter(alert => {
    const severityMatch = severityFilter === 'all' || alert.severity === severityFilter;
    const statusMatch = statusFilter === 'all' || alert.status === statusFilter;
    return severityMatch && statusMatch;
  });

  const getSeverityStyles = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 border-red-500 text-red-900';
      case 'high': return 'bg-orange-100 border-orange-500 text-orange-900';
      case 'medium': return 'bg-blue-100 border-blue-500 text-blue-900';
      case 'low': return 'bg-green-100 border-green-500 text-green-900';
      default: return 'bg-gray-100 border-gray-500 text-gray-900';
    }
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-red-600 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-blue-500 text-white';
      case 'low': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'new': return 'bg-red-100 text-red-800 border border-red-300';
      case 'investigating': return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
      case 'resolved': return 'bg-green-100 text-green-800 border border-green-300';
      default: return 'bg-gray-100 text-gray-800 border border-gray-300';
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <h1 className="text-2xl font-bold">Security Alert Dashboard</h1>
            </div>
            <div className="text-sm">
              <span className="opacity-75">SOC Analyst:</span> Alex
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Title Section */}
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">Correlated Security Incidents</h2>
          <p className="text-gray-600">
            Showing {filteredAlerts.length} incidents from multiple data sources (IdP, EDR, Payments, Email)
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="new">New</option>
                <option value="investigating">Investigating</option>
                <option value="resolved">Resolved</option>
              </select>
            </div>
          </div>
        </div>

        {/* Alert Cards Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`rounded-lg border-l-4 shadow-lg hover:shadow-xl transition-shadow p-6 bg-white ${getSeverityStyles(alert.severity)}`}
            >
              {/* Card Header */}
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-xl font-bold">{alert.title}</h3>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getSeverityBadge(alert.severity)}`}>
                  {alert.severity.toUpperCase()}
                </span>
              </div>

              {/* Badges Row */}
              <div className="flex flex-wrap gap-2 mb-4">
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(alert.status)}`}>
                  {alert.status.toUpperCase()}
                </span>
                <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 border border-blue-300">
                  {alert.signals.length} signals
                </span>
                <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800 border border-purple-300">
                  Confidence: {(alert.confidence * 100).toFixed(0)}%
                </span>
              </div>

              {/* Alert Details */}
              <div className="space-y-2 mb-4 text-sm">
                <div><span className="font-semibold">ID:</span> {alert.id}</div>
                <div><span className="font-semibold">User:</span> {alert.user}</div>
                <div><span className="font-semibold">Time:</span> {new Date(alert.timestamp).toLocaleString()}</div>
              </div>

              {/* Signals */}
              <div className="mb-4">
                <h4 className="font-semibold text-sm mb-2">Detected Signals:</h4>
                <ul className="space-y-1">
                  {alert.signals.map((signal, idx) => (
                    <li key={idx} className="text-sm flex items-start">
                      <span className="mr-2">•</span>
                      <span>{signal}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-2 pt-4 border-t border-gray-200">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
                  Investigate
                </button>
                <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium">
                  Escalate
                </button>
                <button className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 text-sm font-medium">
                  Dismiss
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
