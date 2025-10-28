"""
Integration tests for database operations across multiple tables
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from db import Event, Alert, AuditLog
import uuid


@pytest.mark.integration
class TestCrossTableOperations:
    """Test operations that span multiple tables"""
    
    def test_complete_fraud_detection_workflow(self, clean_database):
        """Test a complete fraud detection workflow across all tables"""
        session = clean_database
        
        # Step 1: Create suspicious events
        events = [
            Event(
                event_type="security",
                source_system="auth_service",
                timestamp=datetime.now(timezone.utc),
                user_id="user_12345",
                device_id="device_abc123",
                event_data={"login_attempt": "failed", "ip": "192.168.1.100"},
                severity="medium"
            ),
            Event(
                event_type="security",
                source_system="auth_service", 
                timestamp=datetime.now(timezone.utc) + timedelta(minutes=1),
                user_id="user_12345",
                device_id="device_xyz789",
                event_data={"login_attempt": "success", "ip": "203.0.113.45"},
                severity="high"
            ),
            Event(
                event_type="financial",
                source_system="payment_gateway",
                timestamp=datetime.now(timezone.utc) + timedelta(minutes=5),
                user_id="user_12345",
                device_id="device_xyz789",
                event_data={"transaction_amount": 5000.0, "risk_score": 85},
                severity="high"
            )
        ]
        
        for event in events:
            session.add(event)
        session.commit()
        
        # Step 2: Create alert based on events
        event_ids = [str(event.id) for event in events]
        alert = Alert(
            title="Potential Account Takeover - user_12345",
            status="open",
            confidence_score=92.5,
            related_event_ids=event_ids
        )
        session.add(alert)
        session.commit()
        
        # Step 3: Create audit log for alert creation
        audit_log = AuditLog(
            user_id="security_system",
            action_type="alert_auto_generated",
            action_details={
                "alert_id": str(alert.id),
                "trigger_events": len(event_ids),
                "risk_score": 92.5,
                "auto_escalate": True
            }
        )
        session.add(audit_log)
        session.commit()
        
        # Verification: Query the complete workflow
        # 1. Verify events exist
        user_events = session.query(Event).filter(Event.user_id == "user_12345").all()
        assert len(user_events) == 3
        
        # 2. Verify alert references correct events
        created_alert = session.query(Alert).filter(Alert.id == alert.id).first()
        assert len(created_alert.related_event_ids) == 3
        for event_id in created_alert.related_event_ids:
            assert any(str(event.id) == event_id for event in user_events)
        
        # 3. Verify audit trail
        alert_audit = session.query(AuditLog).filter(
            AuditLog.action_type == "alert_auto_generated"
        ).first()
        assert alert_audit.action_details["alert_id"] == str(alert.id)
        assert alert_audit.action_details["trigger_events"] == 3
    
    def test_alert_investigation_lifecycle(self, clean_database):
        """Test complete alert investigation lifecycle"""
        session = clean_database
        
        # Create initial event
        event = Event(
            event_type="endpoint",
            source_system="edr_system",
            timestamp=datetime.now(timezone.utc),
            user_id="user_12345",
            device_id="device_abc123",
            event_data={"process": "malware.exe", "threat_level": "high"},
            severity="critical"
        )
        session.add(event)
        session.commit()
        
        # Create alert
        alert = Alert(
            title="Malware Detection - device_abc123",
            status="open",
            confidence_score=95.0,
            related_event_ids=[str(event.id)]
        )
        session.add(alert)
        session.commit()
        
        # Investigation workflow with audit trail
        investigation_steps = [
            ("analyst_1", "alert_assigned", {"alert_id": str(alert.id), "assigned_to": "analyst_1"}),
            ("analyst_1", "alert_status_change", {"alert_id": str(alert.id), "old_status": "open", "new_status": "investigating"}),
            ("analyst_1", "evidence_collection", {"sources": ["endpoint_logs", "network_traffic"], "items_collected": 25}),
            ("analyst_1", "threat_analysis", {"malware_family": "trojan", "c2_servers": ["evil.com"], "impact_assessment": "medium"}),
            ("analyst_1", "containment_action", {"actions": ["isolate_endpoint", "block_c2"], "success": True}),
            ("analyst_1", "alert_resolution", {"resolution": "confirmed_threat", "remediation_complete": True})
        ]
        
        for user_id, action_type, details in investigation_steps:
            audit_log = AuditLog(
                user_id=user_id,
                action_type=action_type,
                action_details=details
            )
            session.add(audit_log)
        
        # Update alert status to resolved
        alert.status = "resolved"
        session.commit()
        
        # Verification
        # 1. Alert should be resolved
        final_alert = session.query(Alert).filter(Alert.id == alert.id).first()
        assert final_alert.status == "resolved"
        
        # 2. Complete audit trail should exist
        alert_audit_trail = session.query(AuditLog).filter(
            AuditLog.action_details['alert_id'].astext == str(alert.id)
        ).order_by(AuditLog.timestamp).all()
        assert len(alert_audit_trail) >= 2  # At least assignment and status change
        
        # 3. Investigation should be complete
        investigation_complete = session.query(AuditLog).filter(
            AuditLog.action_type == "alert_resolution"
        ).first()
        assert investigation_complete.action_details["remediation_complete"] is True
    
    def test_bulk_event_processing(self, clean_database):
        """Test processing large volumes of events with associated alerts"""
        session = clean_database
        
        # Simulate high-volume event ingestion
        base_time = datetime.now(timezone.utc)
        events = []
        
        # Create 100 events across different users and types
        for i in range(100):
            event = Event(
                event_type=["security", "financial", "endpoint"][i % 3],
                source_system=f"system_{i % 5}",
                timestamp=base_time + timedelta(seconds=i),
                user_id=f"user_{i % 10}",
                device_id=f"device_{i % 20}",
                event_data={"event_number": i, "batch": "bulk_test"},
                severity=["info", "low", "medium", "high", "critical"][i % 5]
            )
            events.append(event)
        
        session.add_all(events)
        session.commit()
        
        # Create alerts for high/critical severity events
        high_severity_events = [e for e in events if e.severity in ["high", "critical"]]
        
        alerts = []
        for i, event in enumerate(high_severity_events):
            alert = Alert(
                title=f"High Severity Alert {i}",
                status="open",
                confidence_score=80.0 + (i % 20),  # 80-99
                related_event_ids=[str(event.id)]
            )
            alerts.append(alert)
        
        session.add_all(alerts)
        session.commit()
        
        # Create audit logs for bulk processing
        audit_log = AuditLog(
            user_id="bulk_processor",
            action_type="bulk_event_processing",
            action_details={
                "events_processed": len(events),
                "alerts_generated": len(alerts),
                "processing_time_ms": 1500,
                "batch_id": "bulk_test"
            }
        )
        session.add(audit_log)
        session.commit()
        
        # Verification
        # 1. All events were created
        total_events = session.query(Event).count()
        assert total_events == 100
        
        # 2. Correct number of alerts generated
        total_alerts = session.query(Alert).count()
        expected_alerts = len([e for e in events if e.severity in ["high", "critical"]])
        assert total_alerts == expected_alerts
        
        # 3. Bulk processing was logged
        bulk_audit = session.query(AuditLog).filter(
            AuditLog.action_type == "bulk_event_processing"
        ).first()
        assert bulk_audit.action_details["events_processed"] == 100
    
    def test_data_retention_and_cleanup(self, clean_database):
        """Test data retention policies and cleanup operations"""
        session = clean_database
        
        # Create old and new data
        old_time = datetime.now(timezone.utc) - timedelta(days=90)
        recent_time = datetime.now(timezone.utc) - timedelta(days=1)
        
        # Old data (should be cleaned up)
        old_events = [
            Event(
                event_type="security",
                source_system="old_system",
                timestamp=old_time,
                user_id="old_user",
                severity="info"
            ),
            Event(
                event_type="financial", 
                source_system="old_system",
                timestamp=old_time + timedelta(hours=1),
                user_id="old_user",
                severity="low"
            )
        ]
        
        # Recent data (should be retained)
        recent_events = [
            Event(
                event_type="security",
                source_system="new_system",
                timestamp=recent_time,
                user_id="active_user",
                severity="high"
            ),
            Event(
                event_type="endpoint",
                source_system="new_system", 
                timestamp=recent_time + timedelta(hours=1),
                user_id="active_user",
                severity="critical"
            )
        ]
        
        session.add_all(old_events + recent_events)
        session.commit()
        
        # Create alerts for both old and new events
        old_alert = Alert(
            title="Old Alert",
            status="resolved",
            related_event_ids=[str(old_events[0].id)]
        )
        # Set created_at to old time
        session.add(old_alert)
        session.flush()
        session.execute(
            f"UPDATE alerts SET created_at = '{old_time.isoformat()}' WHERE id = '{old_alert.id}'"
        )
        
        recent_alert = Alert(
            title="Recent Alert",
            status="open",
            related_event_ids=[str(recent_events[0].id)]
        )
        session.add(recent_alert)
        session.commit()
        
        # Simulate cleanup operation
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Count data before cleanup
        events_before = session.query(Event).count()
        alerts_before = session.query(Alert).count()
        
        # Simulate cleanup (in real system, this would be a scheduled job)
        old_events_count = session.query(Event).filter(Event.timestamp < cutoff_date).count()
        old_alerts_count = session.query(Alert).filter(Alert.created_at < cutoff_date).count()
        
        # Log cleanup operation
        cleanup_audit = AuditLog(
            user_id="cleanup_service",
            action_type="data_retention_cleanup",
            action_details={
                "cutoff_date": cutoff_date.isoformat(),
                "events_eligible": old_events_count,
                "alerts_eligible": old_alerts_count,
                "cleanup_performed": False  # Simulation only
            }
        )
        session.add(cleanup_audit)
        session.commit()
        
        # Verification
        assert events_before == 4
        assert alerts_before == 2
        assert old_events_count == 2  # Events older than 30 days
        assert old_alerts_count == 1  # Alerts older than 30 days
        
        # Verify cleanup was logged
        cleanup_log = session.query(AuditLog).filter(
            AuditLog.action_type == "data_retention_cleanup"
        ).first()
        assert cleanup_log.action_details["events_eligible"] == 2


@pytest.mark.integration 
class TestConcurrencyAndPerformance:
    """Test database operations under concurrent access"""
    
    def test_concurrent_alert_creation(self, clean_database):
        """Test creating multiple alerts simultaneously"""
        session = clean_database
        
        # Create a base event
        base_event = Event(
            event_type="security",
            source_system="test_system",
            timestamp=datetime.now(timezone.utc),
            user_id="test_user",
            severity="high"
        )
        session.add(base_event)
        session.commit()
        
        # Simulate concurrent alert creation
        alerts = []
        for i in range(10):
            alert = Alert(
                title=f"Concurrent Alert {i}",
                status="open",
                confidence_score=80.0 + i,
                related_event_ids=[str(base_event.id)]
            )
            alerts.append(alert)
        
        # Add all alerts in one transaction
        session.add_all(alerts)
        session.commit()
        
        # Verify all alerts were created
        created_alerts = session.query(Alert).filter(
            Alert.title.like("Concurrent Alert%")
        ).all()
        assert len(created_alerts) == 10
        
        # Verify they all reference the same event
        for alert in created_alerts:
            assert str(base_event.id) in alert.related_event_ids
    
    def test_large_json_data_handling(self, clean_database):
        """Test handling of large JSON payloads"""
        session = clean_database
        
        # Create event with large JSON payload
        large_payload = {
            "network_connections": [
                {
                    "source_ip": f"192.168.1.{i}",
                    "dest_ip": f"10.0.0.{i % 255}",
                    "port": 80 + (i % 65000),
                    "timestamp": (datetime.now(timezone.utc) + timedelta(seconds=i)).isoformat(),
                    "bytes_transferred": i * 1024,
                    "protocol": "TCP" if i % 2 == 0 else "UDP"
                }
                for i in range(1000)  # 1000 network connections
            ],
            "process_list": [
                {
                    "pid": 1000 + i,
                    "name": f"process_{i}.exe",
                    "cpu_usage": (i % 100) / 100.0,
                    "memory_mb": i % 2048,
                    "start_time": (datetime.now(timezone.utc) - timedelta(minutes=i)).isoformat()
                }
                for i in range(500)  # 500 processes
            ],
            "metadata": {
                "collection_method": "automated_edr",
                "agent_version": "v2.1.0",
                "total_items": 1500,
                "collection_duration_ms": 5000
            }
        }
        
        event = Event(
            event_type="endpoint",
            source_system="edr_comprehensive",
            timestamp=datetime.now(timezone.utc),
            user_id="test_user",
            device_id="workstation_001",
            event_data=large_payload,
            severity="medium"
        )
        session.add(event)
        session.commit()
        
        # Verify large JSON was stored and can be queried
        retrieved_event = session.query(Event).filter(Event.id == event.id).first()
        assert len(retrieved_event.event_data["network_connections"]) == 1000
        assert len(retrieved_event.event_data["process_list"]) == 500
        assert retrieved_event.event_data["metadata"]["total_items"] == 1500
        
        # Test JSON querying on large payload
        events_with_tcp = session.query(Event).filter(
            Event.event_data['network_connections'].op('@>')('[{"protocol": "TCP"}]')
        ).all()
        assert len(events_with_tcp) == 1