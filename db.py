#!/usr/bin/env python3
"""
Database connection and ORM models for Cybersecurity & Fraud Detection Platform
"""

from sqlalchemy import create_engine, Column, String, DateTime, Text, DECIMAL, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMP
from datetime import datetime
import uuid

# Database configuration
DATABASE_URL = "postgresql://admin:securepass123@localhost:5432/cyber_fraud_platform"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String, nullable=False)
    source_system = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    user_id = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    event_data = Column(JSONB, nullable=True)
    severity = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False)
    confidence_score = Column(DECIMAL(5, 2), nullable=True)
    related_event_ids = Column(ARRAY(String), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    user_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    action_details = Column(JSONB, nullable=True)


def get_db_session():
    """Get a database session"""
    session = SessionLocal()
    try:
        return session
    except Exception as e:
        session.close()
        raise e


def test_connection():
    """Test database connection and run sample queries"""
    try:
        session = get_db_session()
        
        print("Testing database connection...")
        
        # Test 1: Count events by severity
        print("\n=== Events by Severity ===")
        for severity in ['info', 'low', 'medium', 'high', 'critical']:
            count = session.query(Event).filter(Event.severity == severity).count()
            print(f"{severity.upper()}: {count}")
        
        # Test 2: Recent alerts
        print("\n=== Recent Alerts ===")
        recent_alerts = session.query(Alert).order_by(Alert.created_at.desc()).limit(5).all()
        for alert in recent_alerts:
            print(f"- {alert.title} [{alert.status}] - Confidence: {alert.confidence_score}%")
        
        # Test 3: High-risk events for specific user
        print("\n=== High-Risk Events for user_12345 ===")
        high_risk_events = session.query(Event).filter(
            Event.user_id == 'user_12345',
            Event.severity.in_(['high', 'critical'])
        ).order_by(Event.timestamp).all()
        
        for event in high_risk_events:
            print(f"- {event.timestamp}: {event.event_type} ({event.severity}) - {event.source_system}")
        
        # Test 4: Audit log summary
        print("\n=== Recent Audit Actions ===")
        recent_audit = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(3).all()
        for log in recent_audit:
            print(f"- {log.timestamp}: {log.user_id} -> {log.action_type}")
        
        session.close()
        print("\n✅ Database connection and queries successful!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    test_connection()