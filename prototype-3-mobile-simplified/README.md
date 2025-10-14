# CS12-1 Prototype 3: Mobile-First Simplified (INTENTIONAL FAILURE)

**Incident Timeline & Evidence Assembly - Poor Design Example**

## Overview
A deliberately flawed mobile-first interface that demonstrates poor design choices for security analysis. This prototype intentionally fails to meet the needs of SOC analysts investigating complex cyber-enabled fraud incidents.

## Why This Prototype FAILS

### 1. Information Density Too Low
- Each event card shows minimal information
- Critical details hidden or omitted entirely
- No access to raw logs or technical details
- Impossible to see correlation patterns

### 2. Poor for Security Analysis
- Can't view multiple events simultaneously
- No timeline context or chronological flow
- Limited filtering options
- No export or sharing capabilities

### 3. Mobile-Only Design Flaws
- Maintains mobile constraints on desktop
- Wastes screen real estate on larger displays
- Touch-first navigation doesn't leverage keyboard shortcuts
- No multi-pane views possible

### 4. Investigation Workflow Problems
- No way to bookmark or flag important events
- Can't build incident narratives
- No collaboration features
- No integration with other security tools

## Design Lessons Learned

1. **Know Your Users**: SOC analysts are power users with specific needs
2. **Information Density Matters**: Security analysis requires seeing multiple data points
3. **Context is Critical**: Events must be viewed in relation to each other
4. **Tool Integration**: Security workflows span multiple systems
5. **Speed Over Aesthetics**: Efficiency matters more than visual appeal

This prototype serves as a cautionary example of how design choices that work well for consumer apps can completely fail in specialized professional contexts.