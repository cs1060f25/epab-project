# EPAB - Unified Cyber-Fraud Detection Platform

A unified AI-driven cybersecurity and fraud detection platform that correlates security telemetry and financial events to detect and respond to cyber-enabled fraud in real-time.

## Overview

Financial institutions face converging cyber and fraud risks, yet defenses remain siloed. This platform ingests both security telemetry (network, identity, endpoint, email, cloud) and financial events (payments, transfers, behavioral signals) to cross-correlate anomalies and coordinate automated response with human-in-the-loop controls and audit-grade explainability.

## Team

- **Eli Pinkus** - Project Lead, Engineering Lead
- **Amit Berger** - Product Lead

## Documentation

Full project documentation available at: [cs1060f25-epab-project Google Drive](https://drive.google.com/drive/u/0/folders/1HPHgI0nW2go5IIYanfdKkL4BBDnZNlZu)

## Links

- [Project Index](https://docs.google.com/document/d/1LXfzumkAeM307pnA2ue9x5RQv6t76Up342827AvHd-w/edit?tab=t.0#heading=h.l8gskcho34dj)
- [Product Requirements Document (PRD)](https://drive.google.com/drive/u/0/folders/1HPHgI0nW2go5IIYanfdKkL4BBDnZNlZu)

## Course

CS1060 Fall 2025 - Computer Science for Ethics, Law, and Society

---

# Database MVP - Setup Instructions

Minimal PostgreSQL database setup for cybersecurity and fraud detection platform.

## Quick Setup

### 1. Start Database
```bash
docker-compose up -d
```

### 2. Install Python Dependencies
```bash
pip install sqlalchemy psycopg2-binary
```

### 3. Test Connection
```bash
python db.py
```

## Database Access

- **Host**: localhost:5432
- **Database**: cyber_fraud_platform  
- **Username**: admin
- **Password**: securepass123

## Core Tables

### events
Security, identity, financial, endpoint, and email events with JSON metadata

### alerts  
Security alerts with confidence scores and related event references

### audit_log
System and user action tracking

## Sample Data

The database includes sample data demonstrating a cyber-fraud scenario:
- Failed login attempts → Successful compromise
- Identity verification bypass  
- Suspicious financial transactions
- Malware detection on endpoint
- Related security alerts

## Useful Queries

```sql
-- High-severity events by user
SELECT user_id, COUNT(*) FROM events 
WHERE severity IN ('high', 'critical') 
GROUP BY user_id;

-- Open alerts by confidence
SELECT title, confidence_score FROM alerts 
WHERE status = 'open' 
ORDER BY confidence_score DESC;

-- Recent audit actions
SELECT user_id, action_type, timestamp FROM audit_log 
ORDER BY timestamp DESC LIMIT 10;
```
