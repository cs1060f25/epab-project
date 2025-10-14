#!/usr/bin/env python3
"""
CS12-1 Prototype 4: Jupyter Notebook Interactive Investigation Environment
Demo script showing investigation capabilities
"""

import pandas as pd
import json
from datetime import datetime

# Sample security events data
security_events = [
    {
        'id': 'dev-001',
        'timestamp': '2024-01-15T08:15:00Z',
        'source': 'Device',
        'type': 'New Device Fingerprint',
        'severity': 'anomaly',
        'description': 'Unknown device fingerprint detected for user alex.chen',
        'user_id': 'alex.chen',
        'ip_address': '185.220.101.42'
    },
    {
        'id': 'idp-001',
        'timestamp': '2024-01-15T08:17:30Z',
        'source': 'IdP',
        'type': 'Login Attempt',
        'severity': 'anomaly',
        'description': 'Login from new geo-location: Moscow, Russia',
        'user_id': 'alex.chen',
        'ip_address': '185.220.101.42'
    },
    {
        'id': 'txn-001',
        'timestamp': '2024-01-15T08:30:00Z',
        'source': 'Transaction',
        'type': 'Wire Transfer Initiated',
        'severity': 'anomaly',
        'description': 'High-value wire transfer initiated - $50,000',
        'user_id': 'alex.chen',
        'ip_address': '185.220.101.42'
    }
]

def analyze_incident():
    """Demonstrate investigation analysis capabilities"""
    df = pd.DataFrame(security_events)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print("CS12-1 Prototype 4: Jupyter Investigation Environment")
    print("=" * 60)
    print(f"Loaded {len(df)} security events")
    print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Anomalies detected: {len(df[df['severity'] == 'anomaly'])}")
    
    # Simple correlation analysis
    moscow_ip = '185.220.101.42'
    moscow_events = df[df['ip_address'] == moscow_ip]
    print(f"\nEvents from Moscow IP ({moscow_ip}): {len(moscow_events)}")
    
    for _, event in moscow_events.iterrows():
        print(f"  • {event['timestamp'].strftime('%H:%M')} - {event['type']}")
    
    print("\n✅ Full interactive analysis available in Jupyter notebook")
    return df

if __name__ == "__main__":
    analyze_incident()