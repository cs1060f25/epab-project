# CS12-1 Prototype 1: Power User Dashboard

**Incident Timeline & Evidence Assembly with Natural Language Assistant**

## Overview
A sophisticated SOC analyst dashboard designed for power users investigating cyber-enabled fraud. Features a dark-themed interface with dense information display, keyboard shortcuts, and advanced filtering capabilities.

## Design Dimensions
- **Tech Stack**: React + Next.js + TypeScript + Tailwind CSS
- **Design Language**: Dark mode, dense information display, keyboard shortcuts
- **User Type**: Power user (security analyst)
- **Interaction**: Point-and-click GUI with keyboard navigation
- **Architecture**: SPA with client-side rendering

## Features
- Dark themed timeline with event cards
- Advanced filtering sidebar (event type, source, severity, time range)
- Natural language search bar with autocomplete suggestions
- Split view: timeline on left, raw log viewer on right
- Keyboard shortcuts (j/k for navigation, / for search, etc.)
- Hoverable tooltips showing event correlations
- Export to JSON functionality

## Mock Data
Contains 20+ security events across 5 data sources over 24 hours:
- **IdP**: Authentication events, MFA, geo-location anomalies
- **Endpoint**: Process execution, network connections, file access
- **Email**: Sent/received messages, external domains
- **Transaction**: Wire transfers, balance checks, approvals
- **Device**: Fingerprinting, registrations, USB devices

## Keyboard Shortcuts
- `j` / `k` - Navigate up/down through events
- `/` - Focus search bar
- `f` - Focus filters
- `e` - Export data to JSON
- `r` - Refresh page

## Installation & Usage
```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## What Worked
- Dense information display suits power users
- Keyboard navigation enables fast incident investigation
- Split-pane layout allows simultaneous timeline and detail viewing
- Dark theme reduces eye strain during long investigation sessions
- Advanced filtering helps focus on relevant events

## Design Decisions
- Chose dark theme for long-session usage
- Keyboard shortcuts for power user efficiency
- Event cards show essential info at a glance
- JSON export for integration with other tools
- Chronological timeline preserves incident sequence