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
    details: {
      deviceId: 'fp-unknown-7f3a',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      fingerprint: 'canvas:3f7a2b1, webgl:nvidia-gtx, fonts:124'
    }
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
    details: {
      country: 'Russia',
      city: 'Moscow',
      method: 'password',
      success: true,
      mfaRequired: true
    }
  },
  {
    id: 'idp-002',
    timestamp: '2024-01-15T08:18:15Z',
    source: 'IdP',
    type: 'MFA Authentication',
    severity: 'normal',
    description: 'MFA push notification accepted',
    userId: 'alex.chen',
    ipAddress: '185.220.101.42',
    details: {
      method: 'push',
      device: 'iPhone 15 Pro',
      duration: '45s'
    }
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
    details: {
      process: 'powershell.exe',
      cmdline: 'powershell -enc JABlAG4AdgA6AHUAcwBlAHIAcAByAG8AZgBpAGwAZQA=',
      parentProcess: 'winword.exe',
      pid: 4532
    }
  },
  {
    id: 'edr-002',
    timestamp: '2024-01-15T08:23:30Z',
    source: 'Endpoint',
    type: 'Network Connection',
    severity: 'suspicious',
    description: 'Outbound connection to suspicious domain',
    userId: 'alex.chen',
    ipAddress: '10.0.1.100',
    details: {
      destination: 'temp-mail-service.ru',
      port: 443,
      protocol: 'HTTPS',
      bytes: 2048
    }
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
    details: {
      to: 'transfer.confirm@temp-mail.ru',
      subject: 'Wire Transfer Confirmation Required',
      attachments: 1,
      size: '24KB'
    }
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
    details: {
      amount: 50000,
      currency: 'USD',
      beneficiary: 'Crypto Exchange Ltd',
      beneficiaryAccount: 'CH9300762011623852957',
      reference: 'Investment Transfer'
    }
  },
  {
    id: 'txn-002',
    timestamp: '2024-01-15T08:45:00Z',
    source: 'Transaction',
    type: 'Wire Transfer Approved',
    severity: 'anomaly',
    description: 'Wire transfer approved by secondary authorization',
    userId: 'alex.chen',
    ipAddress: '185.220.101.42',
    details: {
      amount: 50000,
      approver: 'system.auto',
      reference: 'txn-001'
    }
  }
];

export default function HomePage() {
  const [events] = useState<SecurityEvent[]>(mockEvents);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const filteredEvents = events.filter(event =>
    event.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    event.source.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'anomaly': return 'border-l-red-500 text-red-400';
      case 'suspicious': return 'border-l-yellow-500 text-yellow-400';
      case 'normal': return 'border-l-green-500 text-green-400';
      default: return 'border-l-gray-500 text-gray-400';
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'IdP': return '🔐';
      case 'Endpoint': return '💻';
      case 'Email': return '📧';
      case 'Transaction': return '💰';
      case 'Device': return '📱';
      default: return '❓';
    }
  };

  const exportData = () => {
    const data = {
      exportedAt: new Date().toISOString(),
      query: searchQuery,
      totalEvents: filteredEvents.length,
      events: filteredEvents
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `incident-timeline-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-screen bg-dark-bg text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-700 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">SOC Analyst Dashboard</h1>
            <p className="text-gray-400">CS12-1: Incident Timeline & Evidence Assembly</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-400">
              {filteredEvents.length} of {events.length} events
            </span>
            <button
              onClick={exportData}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium"
            >
              Export JSON
            </button>
          </div>
        </div>
        
        <div className="flex">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search events (e.g., 'Moscow login', 'wire transfer', 'suspicious')"
            className="flex-1 px-4 py-2 bg-gray-800 border border-gray-600 rounded-l-lg focus:outline-none focus:border-blue-500 text-white"
          />
          <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-r-lg font-medium">
            Search
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 bg-gray-900 border-r border-gray-700 p-4 space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-3">Filters</h3>
            
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Data Sources</h4>
                <div className="space-y-2">
                  {['IdP', 'Endpoint', 'Email', 'Transaction', 'Device'].map(source => (
                    <label key={source} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="rounded bg-gray-800 border-gray-600"
                      />
                      <span className="text-sm">{source}</span>
                      <span className="text-xs text-gray-400">
                        ({events.filter(e => e.source === source).length})
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Severity</h4>
                <div className="space-y-2">
                  {['normal', 'suspicious', 'anomaly'].map(severity => (
                    <label key={severity} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="rounded bg-gray-800 border-gray-600"
                      />
                      <span className={`text-sm capitalize ${
                        severity === 'anomaly' ? 'text-red-400' :
                        severity === 'suspicious' ? 'text-yellow-400' :
                        'text-green-400'
                      }`}>
                        {severity}
                      </span>
                      <span className="text-xs text-gray-400">
                        ({events.filter(e => e.severity === severity).length})
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-700 pt-4">
            <h4 className="text-sm font-medium text-gray-300 mb-2">Keyboard Shortcuts</h4>
            <div className="space-y-1 text-xs text-gray-400">
              <div><span className="kbd">j</span> / <span className="kbd">k</span> Navigate</div>
              <div><span className="kbd">/</span> Search</div>
              <div><span className="kbd">e</span> Export</div>
              <div><span className="kbd">r</span> Refresh</div>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="w-1/2 overflow-y-auto p-4 space-y-4">
          <h2 className="text-lg font-semibold mb-4">
            Event Timeline ({filteredEvents.length} events)
          </h2>
          {filteredEvents.map((event) => (
            <div
              key={event.id}
              className={`border-l-4 ${getSeverityColor(event.severity)} bg-gray-900 border border-gray-700 rounded-lg p-4 cursor-pointer transition-all hover:bg-gray-800 ${
                selectedEvent?.id === event.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => setSelectedEvent(event)}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getSourceIcon(event.source)}</span>
                  <span className="text-xs font-mono bg-gray-700 px-2 py-1 rounded">
                    {event.source}
                  </span>
                  <span className={`text-xs font-medium px-2 py-1 rounded ${
                    event.severity === 'anomaly' ? 'bg-red-900 text-red-200' :
                    event.severity === 'suspicious' ? 'bg-yellow-900 text-yellow-200' :
                    'bg-green-900 text-green-200'
                  }`}>
                    {event.severity.toUpperCase()}
                  </span>
                </div>
                <time className="text-xs text-gray-400 font-mono">
                  {new Date(event.timestamp).toLocaleString()}
                </time>
              </div>
              
              <h4 className="font-semibold text-white mb-1">{event.type}</h4>
              <p className="text-sm text-gray-300 mb-2">{event.description}</p>
              
              <div className="flex items-center justify-between text-xs text-gray-400">
                <div className="space-x-4">
                  {event.userId && (
                    <span>👤 {event.userId}</span>
                  )}
                  {event.ipAddress && (
                    <span>🌐 {event.ipAddress}</span>
                  )}
                </div>
                <button
                  className="text-blue-400 hover:text-blue-300"
                  onClick={(e) => {
                    e.stopPropagation();
                    alert('Raw log view would open here');
                  }}
                >
                  View Raw Log →
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Details Panel */}
        <div className="flex-1 bg-gray-900 border-l border-gray-700 p-6 overflow-y-auto">
          {selectedEvent ? (
            <div className="max-w-3xl">
              <div className="mb-6">
                <div className="flex items-center space-x-3 mb-2">
                  <h2 className="text-2xl font-bold text-white">{selectedEvent.type}</h2>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    selectedEvent.severity === 'anomaly' ? 'bg-red-900 text-red-200' :
                    selectedEvent.severity === 'suspicious' ? 'bg-yellow-900 text-yellow-200' :
                    'bg-green-900 text-green-200'
                  }`}>
                    {selectedEvent.severity.toUpperCase()}
                  </span>
                </div>
                <p className="text-gray-300 text-lg">{selectedEvent.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-6">
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-400">Event ID</label>
                    <p className="font-mono text-blue-400">{selectedEvent.id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-400">Timestamp</label>
                    <p className="font-mono">{new Date(selectedEvent.timestamp).toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-400">Source System</label>
                    <p>{selectedEvent.source}</p>
                  </div>
                </div>
                <div className="space-y-3">
                  {selectedEvent.userId && (
                    <div>
                      <label className="text-sm font-medium text-gray-400">User ID</label>
                      <p className="font-mono text-yellow-400">{selectedEvent.userId}</p>
                    </div>
                  )}
                  {selectedEvent.ipAddress && (
                    <div>
                      <label className="text-sm font-medium text-gray-400">IP Address</label>
                      <p className="font-mono text-green-400">{selectedEvent.ipAddress}</p>
                    </div>
                  )}
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Event Details</h3>
                <div className="bg-gray-800 border border-gray-600 rounded-lg p-4">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap overflow-x-auto">
                    {JSON.stringify(selectedEvent.details, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-400">
                <div className="text-4xl mb-2">📋</div>
                <p>Select an event to view details</p>
                <p className="text-sm mt-1">Use <span className="kbd">j</span>/<span className="kbd">k</span> to navigate</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}