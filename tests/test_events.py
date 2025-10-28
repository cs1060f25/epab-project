"""
Tests for Events table functionality
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import func
from db import Event
import uuid


@pytest.mark.database
class TestEventModel:
    """Test Event model functionality"""
    
    def test_create_event(self, clean_database, sample_event_data):
        """Test creating a basic event"""
        session = clean_database
        
        event = Event(**sample_event_data)
        session.add(event)
        session.commit()
        
        assert event.id is not None
        assert isinstance(event.id, uuid.UUID)
        assert event.event_type == "security"
        assert event.source_system == "auth_service"
        assert event.user_id == "user_12345"
        assert event.severity == "medium"
        assert event.created_at is not None
    
    def test_event_with_minimal_data(self, clean_database):
        """Test creating event with only required fields"""
        session = clean_database
        
        event = Event(
            event_type="security",
            source_system="test_system",
            timestamp=datetime.now(timezone.utc),
            severity="info"
        )
        session.add(event)
        session.commit()
        
        assert event.id is not None
        assert event.user_id is None
        assert event.device_id is None
        assert event.event_data is None
    
    def test_event_with_json_data(self, clean_database):
        """Test event with complex JSON data"""
        session = clean_database
        
        complex_data = {
            "login_attempt": "failed",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
            "failed_attempts": 3,
            "location": {
                "country": "US",
                "city": "New York"
            },
            "risk_factors": ["unusual_location", "multiple_failures"]
        }
        
        event = Event(
            event_type="security",
            source_system="auth_service",
            timestamp=datetime.now(timezone.utc),
            user_id="user_12345",
            event_data=complex_data,
            severity="high"
        )
        session.add(event)
        session.commit()
        
        retrieved_event = session.query(Event).filter(Event.id == event.id).first()
        assert retrieved_event.event_data["login_attempt"] == "failed"
        assert retrieved_event.event_data["location"]["city"] == "New York"
        assert "unusual_location" in retrieved_event.event_data["risk_factors"]
    
    def test_event_type_constraint(self, clean_database):
        """Test event_type constraint validation"""
        session = clean_database
        
        # Valid event types should work
        valid_types = ['security', 'identity', 'financial', 'endpoint', 'email']
        
        for event_type in valid_types:
            event = Event(
                event_type=event_type,
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                severity="info"
            )
            session.add(event)
        
        session.commit()
        
        # Invalid event type should fail
        with pytest.raises(Exception):
            invalid_event = Event(
                event_type="invalid_type",
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                severity="info"
            )
            session.add(invalid_event)
            session.commit()
    
    def test_severity_constraint(self, clean_database):
        """Test severity constraint validation"""
        session = clean_database
        
        # Valid severities should work
        valid_severities = ['info', 'low', 'medium', 'high', 'critical']
        
        for severity in valid_severities:
            event = Event(
                event_type="security",
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                severity=severity
            )
            session.add(event)
        
        session.commit()
        
        # Invalid severity should fail
        with pytest.raises(Exception):
            invalid_event = Event(
                event_type="security",
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                severity="invalid_severity"
            )
            session.add(invalid_event)
            session.commit()


@pytest.mark.database
class TestEventQueries:
    """Test Event query functionality"""
    
    def test_query_by_user_id(self, clean_database):
        """Test querying events by user_id"""
        session = clean_database
        
        # Create events for different users
        users = ["user_1", "user_2", "user_1"]
        for i, user_id in enumerate(users):
            event = Event(
                event_type="security",
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                severity="info"
            )
            session.add(event)
        
        session.commit()
        
        # Query events for user_1
        user_1_events = session.query(Event).filter(Event.user_id == "user_1").all()
        assert len(user_1_events) == 2
        
        # Query events for user_2
        user_2_events = session.query(Event).filter(Event.user_id == "user_2").all()
        assert len(user_2_events) == 1
    
    def test_query_by_severity(self, clean_database):
        """Test querying events by severity"""
        session = clean_database
        
        # Create events with different severities
        severities = ["info", "medium", "high", "critical", "high"]
        for severity in severities:
            event = Event(
                event_type="security",
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                severity=severity
            )
            session.add(event)
        
        session.commit()
        
        # Query high severity events
        high_severity_events = session.query(Event).filter(Event.severity == "high").all()
        assert len(high_severity_events) == 2
        
        # Query high and critical events
        critical_events = session.query(Event).filter(
            Event.severity.in_(["high", "critical"])
        ).all()
        assert len(critical_events) == 3
    
    def test_query_by_event_type(self, clean_database):
        """Test querying events by event type"""
        session = clean_database
        
        # Create events of different types
        event_types = ["security", "financial", "security", "endpoint"]
        for event_type in event_types:
            event = Event(
                event_type=event_type,
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                severity="info"
            )
            session.add(event)
        
        session.commit()
        
        # Query security events
        security_events = session.query(Event).filter(Event.event_type == "security").all()
        assert len(security_events) == 2
        
        # Query financial events
        financial_events = session.query(Event).filter(Event.event_type == "financial").all()
        assert len(financial_events) == 1
    
    def test_query_with_time_range(self, clean_database):
        """Test querying events within a time range"""
        session = clean_database
        
        base_time = datetime.now(timezone.utc)
        
        # Create events at different times
        events_data = [
            (base_time, "info"),
            (base_time.replace(hour=base_time.hour + 1), "medium"),
            (base_time.replace(hour=base_time.hour + 2), "high"),
        ]
        
        for timestamp, severity in events_data:
            event = Event(
                event_type="security",
                source_system="test_system",
                timestamp=timestamp,
                severity=severity
            )
            session.add(event)
        
        session.commit()
        
        # Query events within 1.5 hours from base_time
        cutoff_time = base_time.replace(hour=base_time.hour + 1, minute=30)
        recent_events = session.query(Event).filter(
            Event.timestamp <= cutoff_time
        ).all()
        
        assert len(recent_events) == 2
    
    def test_aggregate_queries(self, clean_database):
        """Test aggregate queries on events"""
        session = clean_database
        
        # Create test data
        test_data = [
            ("user_1", "high"),
            ("user_1", "medium"),
            ("user_2", "high"),
            ("user_2", "high"),
            ("user_3", "critical")
        ]
        
        for user_id, severity in test_data:
            event = Event(
                event_type="security",
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                user_id=user_id,
                severity=severity
            )
            session.add(event)
        
        session.commit()
        
        # Count events by severity
        severity_counts = session.query(
            Event.severity,
            func.count(Event.id).label('count')
        ).group_by(Event.severity).all()
        
        severity_dict = {severity: count for severity, count in severity_counts}
        assert severity_dict.get("high") == 3
        assert severity_dict.get("medium") == 1
        assert severity_dict.get("critical") == 1
        
        # Count events by user
        user_counts = session.query(
            Event.user_id,
            func.count(Event.id).label('count')
        ).group_by(Event.user_id).all()
        
        user_dict = {user_id: count for user_id, count in user_counts}
        assert user_dict.get("user_1") == 2
        assert user_dict.get("user_2") == 2
        assert user_dict.get("user_3") == 1
    
    def test_json_queries(self, clean_database):
        """Test querying JSON data in events"""
        session = clean_database
        
        # Create events with JSON data
        events_data = [
            {"login_attempt": "success", "ip": "192.168.1.100"},
            {"login_attempt": "failed", "ip": "192.168.1.100"},
            {"login_attempt": "failed", "ip": "10.0.0.1"},
            {"transaction_amount": 1000.0, "risk_score": 85}
        ]
        
        for i, data in enumerate(events_data):
            event = Event(
                event_type="security" if "login_attempt" in data else "financial",
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                user_id=f"user_{i}",
                event_data=data,
                severity="medium"
            )
            session.add(event)
        
        session.commit()
        
        # Query events with failed login attempts
        failed_logins = session.query(Event).filter(
            Event.event_data['login_attempt'].astext == 'failed'
        ).all()
        assert len(failed_logins) == 2
        
        # Query events from specific IP
        ip_events = session.query(Event).filter(
            Event.event_data['ip'].astext == '192.168.1.100'
        ).all()
        assert len(ip_events) == 2