"""
Tests for AuditLog table functionality
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import func
from db import AuditLog
import uuid


@pytest.mark.database
class TestAuditLogModel:
    """Test AuditLog model functionality"""
    
    def test_create_audit_log(self, clean_database, sample_audit_log_data):
        """Test creating a basic audit log entry"""
        session = clean_database
        
        audit_log = AuditLog(**sample_audit_log_data)
        session.add(audit_log)
        session.commit()
        
        assert audit_log.id is not None
        assert isinstance(audit_log.id, uuid.UUID)
        assert audit_log.user_id == "analyst_1"
        assert audit_log.action_type == "alert_created"
        assert audit_log.action_details["alert_id"] == "test-alert-1"
        assert audit_log.timestamp is not None
    
    def test_audit_log_with_minimal_data(self, clean_database):
        """Test creating audit log with only required fields"""
        session = clean_database
        
        audit_log = AuditLog(
            user_id="test_user",
            action_type="login"
        )
        session.add(audit_log)
        session.commit()
        
        assert audit_log.id is not None
        assert audit_log.action_details is None
        assert audit_log.timestamp is not None
    
    def test_audit_log_with_complex_json(self, clean_database):
        """Test audit log with complex JSON action details"""
        session = clean_database
        
        complex_details = {
            "alert_id": "alert-123",
            "trigger_conditions": {
                "failed_logins": 5,
                "time_window": "5_minutes",
                "source_ips": ["192.168.1.100", "10.0.0.1"]
            },
            "affected_users": ["user1", "user2", "user3"],
            "severity_level": "high",
            "automated_response": {
                "account_locked": True,
                "notification_sent": True,
                "escalation_triggered": False
            }
        }
        
        audit_log = AuditLog(
            user_id="security_system",
            action_type="automated_alert_response",
            action_details=complex_details
        )
        session.add(audit_log)
        session.commit()
        
        retrieved_log = session.query(AuditLog).filter(AuditLog.id == audit_log.id).first()
        assert retrieved_log.action_details["trigger_conditions"]["failed_logins"] == 5
        assert "user2" in retrieved_log.action_details["affected_users"]
        assert retrieved_log.action_details["automated_response"]["account_locked"] is True
    
    def test_audit_log_timestamp_auto_generation(self, clean_database):
        """Test that timestamp is automatically set"""
        session = clean_database
        
        before_creation = datetime.now(timezone.utc)
        
        audit_log = AuditLog(
            user_id="test_user",
            action_type="test_action"
        )
        session.add(audit_log)
        session.commit()
        
        after_creation = datetime.now(timezone.utc)
        
        # Timestamp should be set and within our time window
        assert audit_log.timestamp is not None
        assert before_creation <= audit_log.timestamp <= after_creation


@pytest.mark.database
class TestAuditLogQueries:
    """Test AuditLog query functionality"""
    
    def test_query_by_user_id(self, clean_database):
        """Test querying audit logs by user_id"""
        session = clean_database
        
        # Create audit logs for different users
        users_actions = [
            ("analyst_1", "alert_created"),
            ("analyst_2", "alert_resolved"),
            ("analyst_1", "investigation_started"),
            ("admin_1", "user_permission_changed")
        ]
        
        for user_id, action_type in users_actions:
            audit_log = AuditLog(
                user_id=user_id,
                action_type=action_type
            )
            session.add(audit_log)
        
        session.commit()
        
        # Query logs for analyst_1
        analyst_1_logs = session.query(AuditLog).filter(AuditLog.user_id == "analyst_1").all()
        assert len(analyst_1_logs) == 2
        
        # Query logs for admin users
        admin_logs = session.query(AuditLog).filter(
            AuditLog.user_id.like("admin_%")
        ).all()
        assert len(admin_logs) == 1
    
    def test_query_by_action_type(self, clean_database):
        """Test querying audit logs by action type"""
        session = clean_database
        
        # Create audit logs with different action types
        action_types = [
            "alert_created",
            "alert_resolved",
            "user_login",
            "alert_created",
            "investigation_started"
        ]
        
        for i, action_type in enumerate(action_types):
            audit_log = AuditLog(
                user_id=f"user_{i}",
                action_type=action_type
            )
            session.add(audit_log)
        
        session.commit()
        
        # Query alert-related actions
        alert_actions = session.query(AuditLog).filter(
            AuditLog.action_type.like("alert_%")
        ).all()
        assert len(alert_actions) == 3
        
        # Query specific action type
        created_alerts = session.query(AuditLog).filter(
            AuditLog.action_type == "alert_created"
        ).all()
        assert len(created_alerts) == 2
    
    def test_query_by_time_range(self, clean_database):
        """Test querying audit logs by time range"""
        session = clean_database
        
        base_time = datetime.now(timezone.utc)
        
        # Create audit logs at different times
        for i in range(5):
            audit_log = AuditLog(
                user_id=f"user_{i}",
                action_type="test_action"
            )
            session.add(audit_log)
            session.flush()  # Get the ID
            
            # Set specific timestamp
            timestamp = base_time.replace(hour=base_time.hour + i)
            session.execute(
                f"UPDATE audit_log SET timestamp = '{timestamp.isoformat()}' WHERE id = '{audit_log.id}'"
            )
        
        session.commit()
        
        # Query logs within 2.5 hours from base_time
        cutoff_time = base_time.replace(hour=base_time.hour + 2, minute=30)
        recent_logs = session.query(AuditLog).filter(
            AuditLog.timestamp <= cutoff_time
        ).all()
        
        assert len(recent_logs) == 3  # hours 0, 1, 2
    
    def test_aggregate_queries(self, clean_database):
        """Test aggregate queries on audit logs"""
        session = clean_database
        
        # Create test data
        test_data = [
            ("analyst_1", "alert_created"),
            ("analyst_1", "alert_resolved"),
            ("analyst_2", "alert_created"),
            ("analyst_2", "investigation_started"),
            ("admin_1", "user_permission_changed"),
            ("admin_1", "system_config_changed")
        ]
        
        for user_id, action_type in test_data:
            audit_log = AuditLog(
                user_id=user_id,
                action_type=action_type
            )
            session.add(audit_log)
        
        session.commit()
        
        # Count actions by user
        user_counts = session.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.user_id).all()
        
        user_dict = {user_id: count for user_id, count in user_counts}
        assert user_dict.get("analyst_1") == 2
        assert user_dict.get("analyst_2") == 2
        assert user_dict.get("admin_1") == 2
        
        # Count by action type
        action_counts = session.query(
            AuditLog.action_type,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action_type).all()
        
        action_dict = {action_type: count for action_type, count in action_counts}
        assert action_dict.get("alert_created") == 2
        assert action_dict.get("alert_resolved") == 1
    
    def test_json_queries(self, clean_database):
        """Test querying JSON data in audit logs"""
        session = clean_database
        
        # Create audit logs with JSON details
        logs_data = [
            {
                "user_id": "analyst_1",
                "action_type": "alert_created",
                "details": {"alert_id": "alert-001", "severity": "high", "auto_generated": True}
            },
            {
                "user_id": "analyst_2", 
                "action_type": "alert_resolved",
                "details": {"alert_id": "alert-002", "resolution": "false_positive", "time_to_resolve": 3600}
            },
            {
                "user_id": "admin_1",
                "action_type": "user_permission_changed",
                "details": {"target_user": "analyst_3", "permission": "admin", "granted": True}
            }
        ]
        
        for data in logs_data:
            audit_log = AuditLog(
                user_id=data["user_id"],
                action_type=data["action_type"],
                action_details=data["details"]
            )
            session.add(audit_log)
        
        session.commit()
        
        # Query logs with high severity alerts
        high_severity_logs = session.query(AuditLog).filter(
            AuditLog.action_details['severity'].astext == 'high'
        ).all()
        assert len(high_severity_logs) == 1
        
        # Query auto-generated alerts
        auto_generated_logs = session.query(AuditLog).filter(
            AuditLog.action_details['auto_generated'].astext == 'true'
        ).all()
        assert len(auto_generated_logs) == 1
        
        # Query permission changes
        permission_logs = session.query(AuditLog).filter(
            AuditLog.action_details.has_key('permission')
        ).all()
        assert len(permission_logs) == 1


@pytest.mark.database
class TestAuditLogSecurity:
    """Test audit log security and compliance features"""
    
    def test_audit_log_immutability_simulation(self, clean_database):
        """Test that audit logs should be treated as immutable (simulation)"""
        session = clean_database
        
        # Create an audit log
        original_details = {"original": "data", "timestamp": "2024-01-15T10:00:00Z"}
        audit_log = AuditLog(
            user_id="test_user",
            action_type="test_action",
            action_details=original_details
        )
        session.add(audit_log)
        session.commit()
        
        original_id = audit_log.id
        original_timestamp = audit_log.timestamp
        
        # In a real system, you would prevent updates to audit logs
        # Here we just verify the original data remains intact
        retrieved_log = session.query(AuditLog).filter(AuditLog.id == original_id).first()
        assert retrieved_log.action_details == original_details
        assert retrieved_log.timestamp == original_timestamp
    
    def test_audit_trail_completeness(self, clean_database):
        """Test that audit trail captures all required information"""
        session = clean_database
        
        # Simulate a complete workflow with audit logging
        workflow_steps = [
            ("security_analyst", "alert_triggered", {"trigger": "multiple_failed_logins"}),
            ("security_analyst", "investigation_started", {"alert_id": "alert-001"}),
            ("security_analyst", "evidence_collected", {"sources": ["logs", "network_data"]}),
            ("senior_analyst", "investigation_escalated", {"reason": "potential_breach"}),
            ("incident_commander", "incident_declared", {"severity": "major"}),
            ("incident_commander", "containment_initiated", {"actions": ["isolate_system"]})
        ]
        
        for user_id, action_type, details in workflow_steps:
            audit_log = AuditLog(
                user_id=user_id,
                action_type=action_type,
                action_details=details
            )
            session.add(audit_log)
        
        session.commit()
        
        # Verify complete audit trail
        all_logs = session.query(AuditLog).order_by(AuditLog.timestamp).all()
        assert len(all_logs) == 6
        
        # Verify chronological order
        for i in range(1, len(all_logs)):
            assert all_logs[i-1].timestamp <= all_logs[i].timestamp
        
        # Verify all steps are captured
        action_types = [log.action_type for log in all_logs]
        expected_actions = [step[1] for step in workflow_steps]
        assert action_types == expected_actions
    
    def test_user_action_tracking(self, clean_database):
        """Test comprehensive user action tracking"""
        session = clean_database
        
        # Simulate various user actions
        user_actions = [
            ("analyst_1", "login", {"ip": "192.168.1.100", "success": True}),
            ("analyst_1", "view_alert", {"alert_id": "alert-001"}),
            ("analyst_1", "update_alert_status", {"alert_id": "alert-001", "new_status": "investigating"}),
            ("analyst_1", "run_query", {"query_type": "user_activity", "parameters": {"user_id": "suspect_user"}}),
            ("analyst_1", "export_data", {"format": "csv", "record_count": 150}),
            ("analyst_1", "logout", {"session_duration": 3600})
        ]
        
        for user_id, action_type, details in user_actions:
            audit_log = AuditLog(
                user_id=user_id,
                action_type=action_type,
                action_details=details
            )
            session.add(audit_log)
        
        session.commit()
        
        # Query user's complete session
        user_session = session.query(AuditLog).filter(
            AuditLog.user_id == "analyst_1"
        ).order_by(AuditLog.timestamp).all()
        
        assert len(user_session) == 6
        assert user_session[0].action_type == "login"
        assert user_session[-1].action_type == "logout"
        
        # Verify data access is logged
        data_access_logs = session.query(AuditLog).filter(
            AuditLog.action_type.in_(["view_alert", "run_query", "export_data"])
        ).all()
        assert len(data_access_logs) == 3