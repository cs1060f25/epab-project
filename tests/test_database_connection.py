"""
Tests for database connection and basic functionality
"""
import pytest
from sqlalchemy import text
from db import get_db_session, Event, Alert, AuditLog


@pytest.mark.database
class TestDatabaseConnection:
    """Test database connection and basic operations"""
    
    def test_database_connection(self, test_session):
        """Test that we can connect to the database"""
        result = test_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    def test_tables_exist(self, test_session):
        """Test that all required tables exist"""
        # Check events table
        result = test_session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'events')"))
        assert result.scalar() is True
        
        # Check alerts table
        result = test_session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alerts')"))
        assert result.scalar() is True
        
        # Check audit_log table
        result = test_session.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'audit_log')"))
        assert result.scalar() is True
    
    def test_uuid_extension_enabled(self, test_session):
        """Test that UUID extension is available"""
        result = test_session.execute(text("SELECT uuid_generate_v4()"))
        uuid_value = result.scalar()
        assert uuid_value is not None
        assert len(str(uuid_value)) == 36  # Standard UUID length
    
    def test_indexes_exist(self, test_session):
        """Test that required indexes exist"""
        indexes_query = text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE tablename IN ('events', 'alerts', 'audit_log')
        """)
        
        result = test_session.execute(indexes_query)
        indexes = [row[0] for row in result]
        
        # Check for key indexes
        expected_indexes = [
            'idx_events_timestamp',
            'idx_events_user_id',
            'idx_events_event_type',
            'idx_events_severity',
            'idx_alerts_status',
            'idx_alerts_created_at',
            'idx_audit_log_timestamp',
            'idx_audit_log_user_id',
            'idx_audit_log_action_type'
        ]
        
        for expected_index in expected_indexes:
            assert expected_index in indexes
    
    def test_table_constraints(self, test_session):
        """Test that table constraints are properly set"""
        # Test event_type constraint
        constraints_query = text("""
            SELECT conname, consrc 
            FROM pg_constraint 
            WHERE conrelid = 'events'::regclass 
            AND contype = 'c'
        """)
        
        result = test_session.execute(constraints_query)
        constraints = {row[0]: row[1] for row in result}
        
        # Should have check constraints for event_type and severity
        assert any('event_type' in str(constraint) for constraint in constraints.values())
        assert any('severity' in str(constraint) for constraint in constraints.values())


@pytest.mark.database
class TestDatabaseOperations:
    """Test basic database operations"""
    
    def test_insert_and_query_operations(self, clean_database):
        """Test basic insert and query operations"""
        session = clean_database
        
        # Insert test data
        event = Event(
            event_type="security",
            source_system="test_system",
            timestamp="2024-01-15 14:30:00+00",
            user_id="test_user",
            device_id="test_device",
            event_data={"test": "data"},
            severity="medium"
        )
        session.add(event)
        session.commit()
        
        # Query the data
        retrieved_event = session.query(Event).filter(Event.user_id == "test_user").first()
        assert retrieved_event is not None
        assert retrieved_event.event_type == "security"
        assert retrieved_event.event_data["test"] == "data"
    
    def test_transaction_rollback(self, test_session):
        """Test that failed transactions are properly rolled back"""
        session = test_session
        
        # Insert valid data
        event = Event(
            event_type="security",
            source_system="test_system",
            timestamp="2024-01-15 14:30:00+00",
            user_id="test_user",
            severity="medium"
        )
        session.add(event)
        
        # Try to insert invalid data (should fail due to constraint)
        with pytest.raises(Exception):
            invalid_event = Event(
                event_type="invalid_type",  # This should violate check constraint
                source_system="test_system",
                timestamp="2024-01-15 14:30:00+00",
                user_id="test_user",
                severity="medium"
            )
            session.add(invalid_event)
            session.commit()
        
        # Rollback should have occurred
        session.rollback()
        
        # Original event should not be in database
        count = session.query(Event).filter(Event.user_id == "test_user").count()
        assert count == 0