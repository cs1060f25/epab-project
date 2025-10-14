# CS12-1 Prototype 2: Conversational CLI

**Incident Timeline & Evidence Assembly with Natural Language Assistant**

## Overview
A terminal-based investigation tool for SOC analysts who prefer command-line interfaces. Features conversational commands, ASCII timeline visualization, and rich colored output for investigating cyber-enabled fraud incidents.

## Design Dimensions
- **Tech Stack**: Python + Click CLI + Rich library for formatting
- **Design Language**: Terminal-native, ASCII art visualizations
- **User Type**: Power user who prefers CLI
- **Interaction**: Conversational command-line interface
- **Architecture**: Single Python script with local data

## Features
- Interactive CLI that prints timeline in terminal
- Rich library for colored, formatted output
- Natural language commands like: "show login anomalies" or "filter by endpoint"
- ASCII timeline visualization with symbols for different event types
- Commands: timeline, query <text>, filter <source>, details <event_id>, export
- Colored output: red for anomalies, green for normal, yellow for suspicious
- Quick inline help with --help

## Key Commands
```
soc> timeline                    # Show full timeline
soc> query Moscow login          # Search for Moscow login events
soc> filter Endpoint            # Filter by source
soc> details edr-001            # Show event details
soc> export                     # Export to JSON
soc> help                       # Show help
soc> quit                       # Exit
```

## What Worked
- Terminal-native interface familiar to security professionals
- Rich formatting makes events easy to distinguish
- ASCII timeline provides clear chronological view
- Natural language search enables quick investigation
- Single Python script is portable and fast
- Color coding immediately highlights threats