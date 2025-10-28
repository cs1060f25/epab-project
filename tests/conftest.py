"""
Test configuration and fixtures for database tests
"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from db import Base, Event, Alert, AuditLog


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL test container for testing"""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def test_database_url(postgres_container):
    """Get the database URL for the test container"""
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """Create SQLAlchemy engine for testing"""
    engine = create_engine(test_database_url)
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a database session for testing"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    yield session
    
    # Rollback any changes and close session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def clean_database(test_session):
    """Clean database between tests"""
    # Delete all records from all tables
    test_session.query(AuditLog).delete()
    test_session.query(Alert).delete()
    test_session.query(Event).delete()
    test_session.commit()
    
    yield test_session


@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        "event_type": "security",
        "source_system": "auth_service",
        "timestamp": "2024-01-15 14:30:00+00",
        "user_id": "user_12345",
        "device_id": "device_abc123",
        "event_data": {"login_attempt": "failed", "ip": "192.168.1.100"},
        "severity": "medium"
    }


@pytest.fixture
def sample_alert_data():
    """Sample alert data for testing"""
    return {
        "title": "Test Alert",
        "status": "open",
        "confidence_score": 85.5,
        "related_event_ids": ["event1", "event2"]
    }


@pytest.fixture
def sample_audit_log_data():
    """Sample audit log data for testing"""
    return {
        "user_id": "analyst_1",
        "action_type": "alert_created",
        "action_details": {"alert_id": "test-alert-1", "trigger": "test_scenario"}
    }