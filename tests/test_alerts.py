"""
Tests for Alerts table functionality
"""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import func
from db import Alert, Event
import uuid


@pytest.mark.database
class TestAlertModel:
    """Test Alert model functionality"""
    
    def test_create_alert(self, clean_database, sample_alert_data):
        """Test creating a basic alert"""
        session = clean_database
        
        alert = Alert(**sample_alert_data)
        session.add(alert)
        session.commit()
        
        assert alert.id is not None
        assert isinstance(alert.id, uuid.UUID)
        assert alert.title == "Test Alert"
        assert alert.status == "open"
        assert alert.confidence_score == Decimal('85.5')
        assert alert.related_event_ids == ["event1", "event2"]
        assert alert.created_at is not None
    
    def test_alert_with_minimal_data(self, clean_database):
        """Test creating alert with only required fields"""
        session = clean_database
        
        alert = Alert(
            title="Minimal Alert",
            status="open"
        )
        session.add(alert)
        session.commit()
        
        assert alert.id is not None
        assert alert.confidence_score is None
        assert alert.related_event_ids is None
    
    def test_alert_status_constraint(self, clean_database):
        """Test alert status constraint validation"""
        session = clean_database
        
        # Valid statuses should work
        valid_statuses = ['open', 'investigating', 'resolved']
        
        for status in valid_statuses:
            alert = Alert(
                title=f"Alert {status}",
                status=status
            )
            session.add(alert)
        
        session.commit()
        
        # Invalid status should fail
        with pytest.raises(Exception):
            invalid_alert = Alert(
                title="Invalid Alert",
                status="invalid_status"
            )
            session.add(invalid_alert)
            session.commit()
    
    def test_confidence_score_constraint(self, clean_database):
        """Test confidence score constraint validation"""
        session = clean_database
        
        # Valid confidence scores
        valid_scores = [0.0, 50.5, 100.0]
        
        for score in valid_scores:
            alert = Alert(
                title=f"Alert {score}",
                status="open",
                confidence_score=score
            )
            session.add(alert)
        
        session.commit()
        
        # Invalid confidence scores should fail
        invalid_scores = [-1.0, 101.0]
        
        for score in invalid_scores:
            with pytest.raises(Exception):
                invalid_alert = Alert(
                    title=f"Invalid Alert {score}",
                    status="open",
                    confidence_score=score
                )
                session.add(invalid_alert)
                session.commit()
    
    def test_related_event_ids_array(self, clean_database):
        """Test related_event_ids array functionality"""
        session = clean_database
        
        # Create alert with multiple related event IDs
        event_ids = ["event1", "event2", "event3"]
        alert = Alert(
            title="Multi-Event Alert",
            status="open",
            related_event_ids=event_ids
        )
        session.add(alert)
        session.commit()
        
        retrieved_alert = session.query(Alert).filter(Alert.id == alert.id).first()
        assert retrieved_alert.related_event_ids == event_ids
        assert len(retrieved_alert.related_event_ids) == 3
        assert "event2" in retrieved_alert.related_event_ids
    
    def test_alert_precision_decimal(self, clean_database):
        """Test confidence score decimal precision"""
        session = clean_database
        
        alert = Alert(
            title="Precision Test",
            status="open",
            confidence_score=Decimal('95.67')
        )
        session.add(alert)
        session.commit()
        
        retrieved_alert = session.query(Alert).filter(Alert.id == alert.id).first()
        assert retrieved_alert.confidence_score == Decimal('95.67')


@pytest.mark.database
class TestAlertQueries:
    """Test Alert query functionality"""
    
    def test_query_by_status(self, clean_database):
        """Test querying alerts by status"""
        session = clean_database
        
        # Create alerts with different statuses
        statuses = ["open", "investigating", "resolved", "open"]
        for i, status in enumerate(statuses):
            alert = Alert(
                title=f"Alert {i}",
                status=status
            )
            session.add(alert)
        
        session.commit()
        
        # Query open alerts
        open_alerts = session.query(Alert).filter(Alert.status == "open").all()
        assert len(open_alerts) == 2
        
        # Query non-resolved alerts
        active_alerts = session.query(Alert).filter(
            Alert.status.in_(["open", "investigating"])
        ).all()
        assert len(active_alerts) == 3
    
    def test_query_by_confidence_score(self, clean_database):
        """Test querying alerts by confidence score"""
        session = clean_database
        
        # Create alerts with different confidence scores
        scores = [25.0, 50.0, 75.0, 90.0, 95.0]
        for i, score in enumerate(scores):
            alert = Alert(
                title=f"Alert {i}",
                status="open",
                confidence_score=score
            )
            session.add(alert)
        
        session.commit()
        
        # Query high confidence alerts (>= 80)
        high_confidence = session.query(Alert).filter(
            Alert.confidence_score >= 80.0
        ).all()
        assert len(high_confidence) == 2
        
        # Query medium confidence alerts (50-80)
        medium_confidence = session.query(Alert).filter(
            Alert.confidence_score >= 50.0,
            Alert.confidence_score < 80.0
        ).all()
        assert len(medium_confidence) == 2
    
    def test_query_by_time_range(self, clean_database):
        """Test querying alerts by creation time"""
        session = clean_database
        
        base_time = datetime.now(timezone.utc)
        
        # Create alerts at different times
        for i in range(3):
            alert = Alert(
                title=f"Alert {i}",
                status="open"
            )
            # Manually set created_at for testing
            session.add(alert)
            session.flush()  # Get the ID
            session.execute(
                f"UPDATE alerts SET created_at = '{base_time.replace(hour=base_time.hour + i).isoformat()}' WHERE id = '{alert.id}'"
            )
        
        session.commit()
        
        # Query alerts created within the first 1.5 hours
        cutoff_time = base_time.replace(hour=base_time.hour + 1, minute=30)
        recent_alerts = session.query(Alert).filter(
            Alert.created_at <= cutoff_time
        ).all()
        
        # Should include alerts from hour 0 and 1, but not hour 2
        assert len(recent_alerts) == 2
    
    def test_aggregate_queries(self, clean_database):
        """Test aggregate queries on alerts"""
        session = clean_database
        
        # Create test data
        test_data = [
            ("open", 85.0),
            ("open", 92.0),
            ("investigating", 75.0),
            ("investigating", 88.0),
            ("resolved", 95.0)
        ]
        
        for status, confidence in test_data:
            alert = Alert(
                title=f"Alert {status}",
                status=status,
                confidence_score=confidence
            )
            session.add(alert)
        
        session.commit()
        
        # Count alerts by status
        status_counts = session.query(
            Alert.status,
            func.count(Alert.id).label('count')
        ).group_by(Alert.status).all()
        
        status_dict = {status: count for status, count in status_counts}
        assert status_dict.get("open") == 2
        assert status_dict.get("investigating") == 2
        assert status_dict.get("resolved") == 1
        
        # Average confidence score by status
        avg_confidence = session.query(
            Alert.status,
            func.avg(Alert.confidence_score).label('avg_confidence')
        ).group_by(Alert.status).all()
        
        avg_dict = {status: float(avg) for status, avg in avg_confidence}
        assert abs(avg_dict.get("open") - 88.5) < 0.1  # (85 + 92) / 2
        assert abs(avg_dict.get("investigating") - 81.5) < 0.1  # (75 + 88) / 2


@pytest.mark.database
class TestAlertEventRelationships:
    """Test relationships between alerts and events"""
    
    def test_alert_with_real_event_ids(self, clean_database):
        """Test creating alerts with real event IDs"""
        session = clean_database
        
        # Create some events first
        events = []
        for i in range(3):
            event = Event(
                event_type="security",
                source_system="test_system",
                timestamp=datetime.now(timezone.utc),
                user_id=f"user_{i}",
                severity="high"
            )
            session.add(event)
            events.append(event)
        
        session.commit()
        
        # Create alert referencing these events
        event_ids = [str(event.id) for event in events]
        alert = Alert(
            title="Multi-Event Security Alert",
            status="open",
            confidence_score=90.0,
            related_event_ids=event_ids
        )
        session.add(alert)
        session.commit()
        
        # Verify the relationship
        retrieved_alert = session.query(Alert).filter(Alert.id == alert.id).first()
        assert len(retrieved_alert.related_event_ids) == 3
        
        # Verify all event IDs are valid UUIDs that exist
        for event_id in retrieved_alert.related_event_ids:
            uuid_obj = uuid.UUID(event_id)  # Should not raise exception
            event_exists = session.query(Event).filter(Event.id == uuid_obj).first()
            assert event_exists is not None
    
    def test_query_alerts_with_specific_events(self, clean_database):
        """Test querying alerts that reference specific events"""
        session = clean_database
        
        # Create events
        target_event = Event(
            event_type="security",
            source_system="test_system",
            timestamp=datetime.now(timezone.utc),
            user_id="target_user",
            severity="critical"
        )
        other_event = Event(
            event_type="financial",
            source_system="test_system",
            timestamp=datetime.now(timezone.utc),
            user_id="other_user",
            severity="medium"
        )
        session.add_all([target_event, other_event])
        session.commit()
        
        # Create alerts
        alert1 = Alert(
            title="Alert 1",
            status="open",
            related_event_ids=[str(target_event.id)]
        )
        alert2 = Alert(
            title="Alert 2",
            status="open",
            related_event_ids=[str(other_event.id)]
        )
        alert3 = Alert(
            title="Alert 3",
            status="open",
            related_event_ids=[str(target_event.id), str(other_event.id)]
        )
        session.add_all([alert1, alert2, alert3])
        session.commit()
        
        # Query alerts that reference the target event
        target_event_str = str(target_event.id)
        alerts_with_target = session.query(Alert).filter(
            Alert.related_event_ids.any(target_event_str)
        ).all()
        
        assert len(alerts_with_target) == 2  # alert1 and alert3
        alert_titles = [alert.title for alert in alerts_with_target]
        assert "Alert 1" in alert_titles
        assert "Alert 3" in alert_titles