import React from 'react';

export default function App() {
  return (
    <div className="h-screen bg-dark-bg text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-dark-border p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">SOC Analyst Dashboard</h1>
            <p className="text-gray-400">CS12-1: Incident Timeline & Evidence Assembly</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-400">
              17 events loaded
            </span>
            <button className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium">
              Export JSON
            </button>
          </div>
        </div>
        
        <div className="flex">
          <input
            type="text"
            placeholder="Search events (e.g., 'Moscow login', 'wire transfer', 'suspicious')"
            className="flex-1 px-4 py-2 bg-dark-surface border border-dark-border rounded-l-lg focus:outline-none focus:border-blue-500 text-white"
          />
          <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-r-lg font-medium">
            Search
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 bg-dark-surface border-r border-dark-border p-4">
          <h3 className="text-lg font-semibold mb-3">Filters</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-2">Data Sources</h4>
              <div className="space-y-2">
                {['IdP', 'Endpoint', 'Email', 'Transaction', 'Device'].map(source => (
                  <label key={source} className="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" defaultChecked className="rounded bg-dark-bg border-dark-border" />
                    <span className="text-sm">{source}</span>
                  </label>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-300 mb-2">Severity</h4>
              <div className="space-y-2">
                {['normal', 'suspicious', 'anomaly'].map(severity => (
                  <label key={severity} className="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" defaultChecked className="rounded bg-dark-bg border-dark-border" />
                    <span className={`text-sm capitalize ${
                      severity === 'anomaly' ? 'text-red-400' :
                      severity === 'suspicious' ? 'text-yellow-400' :
                      'text-green-400'
                    }`}>
                      {severity}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>
          
          <div className="border-t border-dark-border pt-4 mt-6">
            <h4 className="text-sm font-medium text-gray-300 mb-2">Keyboard Shortcuts</h4>
            <div className="space-y-1 text-xs text-gray-400">
              <div><kbd className="px-1 py-0.5 bg-gray-700 rounded text-xs">j</kbd> / <kbd className="px-1 py-0.5 bg-gray-700 rounded text-xs">k</kbd> Navigate</div>
              <div><kbd className="px-1 py-0.5 bg-gray-700 rounded text-xs">/</kbd> Search</div>
              <div><kbd className="px-1 py-0.5 bg-gray-700 rounded text-xs">e</kbd> Export</div>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div className="w-1/2 overflow-y-auto p-4 space-y-4">
          <h2 className="text-lg font-semibold mb-4">
            Event Timeline (17 events)
          </h2>
          
          {/* Sample Event Cards */}
          <div className="border-l-4 border-l-red-500 bg-dark-surface border border-dark-border rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">📱</span>
                <span className="text-xs font-mono bg-gray-700 px-2 py-1 rounded">Device</span>
                <span className="text-xs font-medium px-2 py-1 rounded bg-red-900 text-red-200">ANOMALY</span>
              </div>
              <time className="text-xs text-gray-400 font-mono">08:15:00</time>
            </div>
            <h4 className="font-semibold text-white mb-1">New Device Fingerprint</h4>
            <p className="text-sm text-gray-300 mb-2">Unknown device fingerprint detected for user alex.chen</p>
            <div className="flex items-center justify-between text-xs text-gray-400">
              <div className="space-x-4">
                <span>👤 alex.chen</span>
                <span>🌐 185.220.101.42</span>
              </div>
              <button className="text-blue-400 hover:text-blue-300">View Raw Log →</button>
            </div>
          </div>

          <div className="border-l-4 border-l-red-500 bg-dark-surface border border-dark-border rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">🔐</span>
                <span className="text-xs font-mono bg-gray-700 px-2 py-1 rounded">IdP</span>
                <span className="text-xs font-medium px-2 py-1 rounded bg-red-900 text-red-200">ANOMALY</span>
              </div>
              <time className="text-xs text-gray-400 font-mono">08:17:30</time>
            </div>
            <h4 className="font-semibold text-white mb-1">Login Attempt</h4>
            <p className="text-sm text-gray-300 mb-2">Login from new geo-location: Moscow, Russia</p>
            <div className="flex items-center justify-between text-xs text-gray-400">
              <div className="space-x-4">
                <span>👤 alex.chen</span>
                <span>🌐 185.220.101.42</span>
              </div>
              <button className="text-blue-400 hover:text-blue-300">View Raw Log →</button>
            </div>
          </div>

          <div className="border-l-4 border-l-red-500 bg-dark-surface border border-dark-border rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">💰</span>
                <span className="text-xs font-mono bg-gray-700 px-2 py-1 rounded">Transaction</span>
                <span className="text-xs font-medium px-2 py-1 rounded bg-red-900 text-red-200">ANOMALY</span>
              </div>
              <time className="text-xs text-gray-400 font-mono">08:30:00</time>
            </div>
            <h4 className="font-semibold text-white mb-1">Wire Transfer Initiated</h4>
            <p className="text-sm text-gray-300 mb-2">High-value wire transfer initiated - $50,000</p>
            <div className="flex items-center justify-between text-xs text-gray-400">
              <div className="space-x-4">
                <span>👤 alex.chen</span>
                <span>🌐 185.220.101.42</span>
              </div>
              <button className="text-blue-400 hover:text-blue-300">View Raw Log →</button>
            </div>
          </div>
        </div>

        {/* Details Panel */}
        <div className="flex-1 bg-dark-surface border-l border-dark-border p-6">
          <div className="text-center text-gray-400">
            <div className="text-4xl mb-2">📋</div>
            <p>Select an event to view details</p>
            <p className="text-sm mt-1">Use <kbd className="px-1 py-0.5 bg-gray-700 rounded text-xs">j</kbd>/<kbd className="px-1 py-0.5 bg-gray-700 rounded text-xs">k</kbd> to navigate</p>
          </div>
        </div>
      </div>
    </div>
  );
}