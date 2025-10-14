'use client';

import { useState } from 'react';

interface SecurityEvent {
  id: string;
  timestamp: string;
  source: string;
  type: string;
  severity: 'normal' | 'suspicious' | 'anomaly';
  description: string;
  userId?: string;
  ipAddress?: string;
  details: Record<string, any>;
}

const mockEvents: SecurityEvent[] = [
  {
    id: 'dev-001',
    timestamp: '2024-01-15T08:15:00Z',
    source: 'Device',
    type: 'New Device Fingerprint',
    severity: 'anomaly',
    description: 'Unknown device fingerprint detected for user alex.chen',
    userId: 'alex.chen',
    ipAddress: '185.220.101.42',
    details: { deviceId: 'fp-unknown-7f3a', location: 'Moscow, Russia' }
  },
  {
    id: 'idp-001',
    timestamp: '2024-01-15T08:17:30Z',
    source: 'IdP',
    type: 'Login Attempt',
    severity: 'anomaly',
    description: 'Login from new geo-location: Moscow, Russia',
    userId: 'alex.chen',
    ipAddress: '185.220.101.42',
    details: { country: 'Russia', city: 'Moscow', method: 'password', success: true }
  },
  {
    id: 'edr-001',
    timestamp: '2024-01-15T08:22:00Z',
    source: 'Endpoint',
    type: 'Process Creation',
    severity: 'anomaly',
    description: 'Suspicious process execution detected',
    userId: 'alex.chen',
    ipAddress: '10.0.1.100',
    details: { process: 'powershell.exe', parentProcess: 'winword.exe' }
  },
  {
    id: 'txn-001',
    timestamp: '2024-01-15T08:30:00Z',
    source: 'Transaction',
    type: 'Wire Transfer Initiated',
    severity: 'anomaly',
    description: 'High-value wire transfer initiated - $50,000',
    userId: 'alex.chen',
    ipAddress: '185.220.101.42',
    details: { amount: 50000, currency: 'USD', beneficiary: 'Crypto Exchange Ltd' }
  },
  {
    id: 'email-001',
    timestamp: '2024-01-15T08:25:00Z',
    source: 'Email',
    type: 'Email Sent',
    severity: 'suspicious',
    description: 'Email sent to external domain',
    userId: 'alex.chen',
    ipAddress: '10.0.1.100',
    details: { to: 'transfer.confirm@temp-mail.ru', subject: 'Wire Transfer Confirmation Required' }
  }
];

export default function NotebookPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [analysisResults, setAnalysisResults] = useState<any>(null);

  const runAnalysis = () => {
    const anomalies = mockEvents.filter(e => e.severity === 'anomaly').length;
    const suspicious = mockEvents.filter(e => e.severity === 'suspicious').length;
    const moscowIP = '185.220.101.42';
    const moscowEvents = mockEvents.filter(e => e.ipAddress === moscowIP);
    
    setAnalysisResults({
      totalEvents: mockEvents.length,
      anomalies,
      suspicious,
      moscowEvents: moscowEvents.length,
      timeSpan: '30 minutes',
      riskScore: anomalies * 10 + suspicious * 5
    });
    setCurrentStep(1);
  };

  const runCorrelation = () => {
    setCurrentStep(2);
  };

  const generateReport = () => {
    setCurrentStep(3);
  };

  return (
    <div className="notebook-container">
      <header style={{ marginBottom: '30px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '10px' }}>
          🔬 CS12-1 Prototype 4: Interactive Investigation Notebook
        </h1>
        <p style={{ color: '#64748b', fontSize: '16px' }}>
          Data Science Approach to Incident Timeline & Evidence Assembly
        </p>
      </header>

      {/* Markdown Cell - Introduction */}
      <div className="cell markdown-cell">
        <div className="cell-header">
          <span>📝</span>
          <span>Markdown</span>
        </div>
        <div className="cell-content">
          <h2 style={{ marginBottom: '15px' }}>Investigation: CS12-1-alex-chen-20240115</h2>
          <p style={{ marginBottom: '10px' }}><strong>Incident Type:</strong> Cyber-enabled fraud investigation</p>
          <p style={{ marginBottom: '10px' }}><strong>Subject:</strong> alex.chen</p>
          <p style={{ marginBottom: '10px' }}><strong>Date:</strong> 2024-01-15</p>
          <p><strong>Objective:</strong> Analyze security events for potential fraud indicators using data science methods</p>
        </div>
      </div>

      {/* Code Cell - Data Loading */}
      <div className="cell code-cell">
        <div className="cell-header">
          <span>⚡</span>
          <span>Code</span>
          <button className="run-button" onClick={runAnalysis}>
            ▶ Run
          </button>
        </div>
        <div className="cell-content">
          <div className="code-block">
{`# Load and analyze security event data
import pandas as pd
import numpy as np
from datetime import datetime

# Load security events
events_data = load_security_events('alex.chen', '2024-01-15')
df = pd.DataFrame(events_data)

print(f"📊 Loaded {len(df)} security events")
print(f"📅 Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"🔍 Sources: {', '.join(df['source'].unique())}")

# Calculate severity distribution
severity_counts = df['severity'].value_counts()
print("\\n🎯 Severity Distribution:")
for severity, count in severity_counts.items():
    print(f"  {severity}: {count} events")`}
          </div>
          
          {analysisResults && (
            <div className="output-block">
              <div style={{ color: '#059669', fontWeight: 'bold', marginBottom: '10px' }}>📊 Analysis Output:</div>
              <div>📊 Loaded {analysisResults.totalEvents} security events</div>
              <div>📅 Time range: 2024-01-15 08:15:00 to 2024-01-15 08:30:00</div>
              <div>🔍 Sources: Device, IdP, Endpoint, Transaction, Email</div>
              <div style={{ marginTop: '10px' }}>🎯 Severity Distribution:</div>
              <div style={{ marginLeft: '20px' }}>anomaly: {analysisResults.anomalies} events</div>
              <div style={{ marginLeft: '20px' }}>suspicious: {analysisResults.suspicious} events</div>
              <div style={{ marginLeft: '20px' }}>normal: {analysisResults.totalEvents - analysisResults.anomalies - analysisResults.suspicious} events</div>
            </div>
          )}
        </div>
      </div>

      {/* Statistics Display */}
      {analysisResults && (
        <div className="cell output-cell">
          <div className="cell-header">
            <span>📈</span>
            <span>Analysis Results</span>
          </div>
          <div className="cell-content">
            <div className="stats-grid">
              <div className="stat-card">
                <h4>Total Events</h4>
                <div className="value">{analysisResults.totalEvents}</div>
              </div>
              <div className="stat-card">
                <h4>Anomalies</h4>
                <div className="value" style={{ color: '#dc2626' }}>{analysisResults.anomalies}</div>
              </div>
              <div className="stat-card">
                <h4>Suspicious</h4>
                <div className="value" style={{ color: '#d97706' }}>{analysisResults.suspicious}</div>
              </div>
              <div className="stat-card">
                <h4>Risk Score</h4>
                <div className="value" style={{ color: '#7c3aed' }}>{analysisResults.riskScore}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timeline Visualization */}
      {currentStep >= 1 && (
        <div className="cell code-cell">
          <div className="cell-header">
            <span>📊</span>
            <span>Visualization</span>
            <button className="run-button" onClick={runCorrelation}>
              ▶ Run
            </button>
          </div>
          <div className="cell-content">
            <div className="code-block">
{`# Create interactive timeline visualization
import plotly.express as px
import plotly.graph_objects as go

# Color mapping for severity
severity_colors = {
    'normal': '#059669',
    'suspicious': '#d97706', 
    'anomaly': '#dc2626'
}

# Create timeline scatter plot
fig = px.scatter(
    df, 
    x='timestamp', 
    y='source',
    color='severity',
    size=[15]*len(df),
    hover_data=['type', 'description'],
    title='🔍 Security Incident Timeline - alex.chen',
    color_discrete_map=severity_colors
)

fig.update_layout(width=900, height=400)
fig.show()`}
            </div>
            
            <div className="timeline-viz">
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '48px', marginBottom: '10px' }}>📈</div>
                <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '5px' }}>
                  Interactive Timeline Visualization
                </div>
                <div style={{ color: '#64748b', fontSize: '14px' }}>
                  Events plotted by time and source with severity color coding
                </div>
                <div style={{ marginTop: '15px', fontSize: '12px', color: '#64748b' }}>
                  🔴 Anomaly • 🟡 Suspicious • 🟢 Normal
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Correlation Analysis */}
      {currentStep >= 2 && (
        <div className="cell code-cell">
          <div className="cell-header">
            <span>🔗</span>
            <span>Correlation Analysis</span>
            <button className="run-button" onClick={generateReport}>
              ▶ Run
            </button>
          </div>
          <div className="cell-content">
            <div className="code-block">
{`# Analyze correlations and patterns
moscow_ip = '185.220.101.42'
moscow_events = df[df['ip_address'] == moscow_ip]

print("🚨 CRITICAL FINDINGS:")
print(f"🌍 Events from Moscow IP ({moscow_ip}): {len(moscow_events)}")

for _, event in moscow_events.iterrows():
    print(f"  • {event['timestamp']} - {event['type']} ({event['severity']})")

# Anomaly scoring
def calculate_risk_score(event):
    score = 0
    if event['severity'] == 'anomaly': score += 10
    if event['severity'] == 'suspicious': score += 5
    if 'moscow' in str(event['details']).lower(): score += 5
    if event['ip_address'] == moscow_ip: score += 5
    return score

df['risk_score'] = df.apply(calculate_risk_score, axis=1)
high_risk = df[df['risk_score'] >= 15]

print(f"\\n⚠️ HIGH RISK EVENTS: {len(high_risk)}")`}
            </div>
            
            {analysisResults && (
              <div className="output-block">
                <div style={{ color: '#dc2626', fontWeight: 'bold', marginBottom: '10px' }}>🚨 CRITICAL FINDINGS:</div>
                <div>🌍 Events from Moscow IP (185.220.101.42): {analysisResults.moscowEvents}</div>
                <div style={{ marginLeft: '20px', marginTop: '5px' }}>• 08:15:00 - New Device Fingerprint (anomaly)</div>
                <div style={{ marginLeft: '20px' }}>• 08:17:30 - Login Attempt (anomaly)</div>
                <div style={{ marginLeft: '20px' }}>• 08:30:00 - Wire Transfer Initiated (anomaly)</div>
                <div style={{ marginTop: '10px', color: '#d97706', fontWeight: 'bold' }}>⚠️ HIGH RISK EVENTS: 4</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Event Details Table */}
      {currentStep >= 2 && (
        <div className="cell output-cell">
          <div className="cell-header">
            <span>📋</span>
            <span>Event Details</span>
          </div>
          <div className="cell-content">
            <table className="events-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Source</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Description</th>
                  <th>IP Address</th>
                </tr>
              </thead>
              <tbody>
                {mockEvents.map(event => (
                  <tr key={event.id}>
                    <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </td>
                    <td>{event.source}</td>
                    <td>{event.type}</td>
                    <td className={`severity-${event.severity}`}>
                      {event.severity.toUpperCase()}
                    </td>
                    <td style={{ maxWidth: '300px' }}>{event.description}</td>
                    <td style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                      {event.ipAddress}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Report Generation */}
      {currentStep >= 3 && (
        <div className="cell markdown-cell">
          <div className="cell-header">
            <span>📄</span>
            <span>Investigation Report</span>
          </div>
          <div className="cell-content">
            <h3 style={{ marginBottom: '15px', color: '#dc2626' }}>🚨 SECURITY INCIDENT REPORT</h3>
            
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ marginBottom: '10px' }}>Executive Summary</h4>
              <p style={{ marginBottom: '10px' }}>
                Analysis of {analysisResults?.totalEvents} security events reveals a coordinated cyber-enabled fraud attack against user alex.chen.
              </p>
              <p>
                <strong>Risk Level: HIGH</strong> - Multiple anomalies detected from foreign IP address with high-value financial transaction.
              </p>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ marginBottom: '10px' }}>Key Findings</h4>
              <ul style={{ marginLeft: '20px' }}>
                <li>Unauthorized access from Moscow, Russia (185.220.101.42)</li>
                <li>Suspicious PowerShell execution detected</li>
                <li>$50,000 wire transfer to cryptocurrency exchange</li>
                <li>All events occurred within 30-minute window</li>
              </ul>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ marginBottom: '10px' }}>Recommended Actions</h4>
              <div style={{ background: '#fef2f2', padding: '15px', borderRadius: '6px', border: '1px solid #fecaca' }}>
                <ol style={{ marginLeft: '20px' }}>
                  <li><strong>Immediate:</strong> Freeze account and block IP 185.220.101.42</li>
                  <li><strong>Urgent:</strong> Halt wire transfer if still pending</li>
                  <li><strong>Security:</strong> Force password reset and enable enhanced MFA</li>
                  <li><strong>Investigation:</strong> Full endpoint forensics analysis required</li>
                </ol>
              </div>
            </div>

            <div style={{ fontSize: '12px', color: '#64748b', borderTop: '1px solid #e2e8f0', paddingTop: '15px' }}>
              <em>Report generated using CS12-1 Prototype 4: Interactive Investigation Notebook</em>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ marginTop: '40px', textAlign: 'center', color: '#64748b', fontSize: '14px' }}>
        <p><strong>CS12-1 Prototype 4:</strong> Jupyter Notebook Interactive Investigation Environment</p>
        <p>Demonstrates data science approach to cybersecurity incident analysis</p>
      </div>
    </div>
  );
}