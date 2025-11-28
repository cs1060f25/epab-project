#!/usr/bin/env python3
"""
Pytest-based Test Suite for Cybersecurity & Fraud Detection Platform API
Professional test suite using pytest fixtures and parametrized tests
"""

import pytest
import requests
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Generator
import time

# Test Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


@pytest.fixture(scope="session", autouse=True)
def ensure_server_running():
    """Ensure the API server is running before running tests"""
    max_attempts = 30
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=2)
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    pytest.fail("API server is not running on port 8000")


@pytest.fixture
def valid_event_data() -> Dict[str, Any]:
    """Fixture providing valid event data for testing"""
    return {
        "event_type": "security",
        "source_system": "pytest_test_system",
        "user_id": "pytest_user_123",
        "device_id": "pytest_device_456",
        "event_data": {
            "ip_address": "192.168.1.100",
            "action": "login_attempt",
            "success": False,
            "test_timestamp": datetime.now(timezone.utc).isoformat()
        },
        "severity": "high"
    }


@pytest.fixture
def minimal_event_data() -> Dict[str, Any]:
    """Fixture providing minimal valid event data"""
    return {
        "event_type": "endpoint",
        "source_system": "pytest_minimal_system",
        "severity": "low"
    }


@pytest.fixture
def created_event_id(valid_event_data) -> Generator[str, None, None]:
    """Fixture that creates an event and returns its ID, cleans up after test"""
    response = requests.post(f"{API_BASE}/events", json=valid_event_data)
    assert response.status_code == 201
    event_id = response.json()["id"]
    yield event_id
    # Cleanup could be added here if the API supported DELETE


class TestHealthEndpoint:
    """Test cases for /api/health endpoint"""
    
    def test_health_check_success(self):
        """Test health endpoint returns successful response"""
        response = requests.get(f"{API_BASE}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["database"] in ["connected", "disconnected"]
    
    def test_health_check_response_time(self):
        """Test health endpoint responds quickly"""
        start_time = time.time()
        response = requests.get(f"{API_BASE}/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds
    
    def test_health_check_headers(self):
        """Test health endpoint returns correct headers"""
        response = requests.get(f"{API_BASE}/health")
        
        assert response.status_code == 200
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]


class TestEventsCreation:
    """Test cases for creating events"""
    
    def test_create_event_valid_data(self, valid_event_data):
        """Test successful event creation with valid data"""
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        required_fields = ["id", "event_type", "source_system", "timestamp", "severity", "created_at"]
        for field in required_fields:
            assert field in data
        
        # Verify data integrity
        assert data["event_type"] == valid_event_data["event_type"]
        assert data["source_system"] == valid_event_data["source_system"]
        assert data["severity"] == valid_event_data["severity"]
        assert data["user_id"] == valid_event_data["user_id"]
        
        # Verify UUID format
        assert uuid.UUID(data["id"])
    
    def test_create_event_minimal_data(self, minimal_event_data):
        """Test event creation with minimal required data"""
        response = requests.post(f"{API_BASE}/events", json=minimal_event_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["event_type"] == minimal_event_data["event_type"]
        assert data["source_system"] == minimal_event_data["source_system"]
        assert data["severity"] == minimal_event_data["severity"]
        assert data["user_id"] is None
        assert data["device_id"] is None
    
    @pytest.mark.parametrize("event_type", [
        "security", "identity", "financial", "endpoint", "email"
    ])
    def test_create_event_valid_types(self, valid_event_data, event_type):
        """Test event creation with all valid event types"""
        valid_event_data["event_type"] = event_type
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        
        assert response.status_code == 201
        assert response.json()["event_type"] == event_type
    
    @pytest.mark.parametrize("severity", [
        "info", "low", "medium", "high", "critical"
    ])
    def test_create_event_valid_severities(self, valid_event_data, severity):
        """Test event creation with all valid severity levels"""
        valid_event_data["severity"] = severity
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        
        assert response.status_code == 201
        assert response.json()["severity"] == severity
    
    @pytest.mark.parametrize("invalid_event_type", [
        "invalid_type", "SECURITY", "network", "", None
    ])
    def test_create_event_invalid_types(self, valid_event_data, invalid_event_type):
        """Test event creation with invalid event types"""
        valid_event_data["event_type"] = invalid_event_type
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        
        assert response.status_code == 422
    
    @pytest.mark.parametrize("invalid_severity", [
        "invalid", "CRITICAL", "urgent", "", None
    ])
    def test_create_event_invalid_severities(self, valid_event_data, invalid_severity):
        """Test event creation with invalid severity levels"""
        valid_event_data["severity"] = invalid_severity
        response = requests.post(f"{API_BASE}/events", json=valid_severity)
        
        assert response.status_code == 422
    
    @pytest.mark.parametrize("missing_field", [
        "event_type", "source_system", "severity"
    ])
    def test_create_event_missing_required_fields(self, valid_event_data, missing_field):
        """Test event creation with missing required fields"""
        incomplete_event = valid_event_data.copy()
        del incomplete_event[missing_field]
        
        response = requests.post(f"{API_BASE}/events", json=incomplete_event)
        assert response.status_code == 422
    
    def test_create_event_large_payload(self, valid_event_data):
        """Test event creation with large event_data payload"""
        valid_event_data["event_data"] = {f"field_{i}": f"value_{i}" * 100 for i in range(100)}
        
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        assert response.status_code == 201
    
    def test_create_event_special_characters(self, valid_event_data):
        """Test event creation with special characters in string fields"""
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        valid_event_data["user_id"] = f"user_{special_chars}"
        valid_event_data["device_id"] = f"device_{special_chars}"
        
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        assert response.status_code == 201
    
    def test_create_event_unicode_characters(self, valid_event_data):
        """Test event creation with unicode characters"""
        valid_event_data["user_id"] = "用户_テスト_🔒"
        valid_event_data["device_id"] = "设备_デバイス_📱"
        
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        assert response.status_code == 201


class TestEventsRetrieval:
    """Test cases for retrieving events"""
    
    def test_get_events_no_filters(self):
        """Test retrieving events without any filters"""
        response = requests.get(f"{API_BASE}/events")
        
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert isinstance(data["events"], list)
        assert isinstance(data["total"], int)
        assert data["total"] >= 0
    
    def test_get_events_with_limit(self):
        """Test retrieving events with limit parameter"""
        response = requests.get(f"{API_BASE}/events", params={"limit": 5})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) <= 5
    
    @pytest.mark.parametrize("limit", [1, 10, 50, 100, 500, 1000])
    def test_get_events_valid_limits(self, limit):
        """Test retrieving events with various valid limit values"""
        response = requests.get(f"{API_BASE}/events", params={"limit": limit})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) <= limit
    
    @pytest.mark.parametrize("invalid_limit", [0, -1, 1001, "invalid", 1.5])
    def test_get_events_invalid_limits(self, invalid_limit):
        """Test retrieving events with invalid limit values"""
        response = requests.get(f"{API_BASE}/events", params={"limit": invalid_limit})
        assert response.status_code == 422
    
    def test_get_events_filter_by_type(self, created_event_id):
        """Test retrieving events filtered by event type"""
        response = requests.get(f"{API_BASE}/events", params={"event_type": "security"})
        
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]:
            assert event["event_type"] == "security"
    
    def test_get_events_filter_by_user_id(self, created_event_id):
        """Test retrieving events filtered by user ID"""
        user_id = "pytest_user_123"
        response = requests.get(f"{API_BASE}/events", params={"user_id": user_id})
        
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]:
            assert event["user_id"] == user_id
    
    def test_get_events_filter_by_date_range(self):
        """Test retrieving events filtered by date range"""
        now = datetime.now(timezone.utc)
        start_date = (now - timedelta(hours=1)).isoformat()
        end_date = (now + timedelta(hours=1)).isoformat()
        
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.get(f"{API_BASE}/events", params=params)
        assert response.status_code == 200
    
    @pytest.mark.parametrize("invalid_date", [
        "not-a-date", "2023-13-45", "2023/01/01", "invalid", ""
    ])
    def test_get_events_invalid_date_formats(self, invalid_date):
        """Test retrieving events with invalid date formats"""
        response = requests.get(f"{API_BASE}/events", params={"start_date": invalid_date})
        assert response.status_code == 422
    
    def test_get_events_nonexistent_filter(self):
        """Test retrieving events with nonexistent filter values"""
        response = requests.get(f"{API_BASE}/events", params={
            "event_type": "nonexistent_type",
            "user_id": "nonexistent_user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["events"]) == 0


class TestAlertsEndpoint:
    """Test cases for alerts endpoints"""
    
    def test_get_alerts_success(self):
        """Test successful retrieval of alerts"""
        response = requests.get(f"{API_BASE}/alerts")
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total" in data
        assert isinstance(data["alerts"], list)
        assert isinstance(data["total"], int)
    
    def test_get_alerts_response_structure(self):
        """Test alerts response structure"""
        response = requests.get(f"{API_BASE}/alerts")
        data = response.json()
        
        if data["alerts"]:
            alert = data["alerts"][0]
            required_fields = ["id", "title", "status", "created_at", "event_count"]
            for field in required_fields:
                assert field in alert
    
    @pytest.mark.parametrize("status", ["open", "investigating", "resolved"])
    def test_get_alerts_valid_status_filter(self, status):
        """Test retrieving alerts with valid status filters"""
        response = requests.get(f"{API_BASE}/alerts", params={"status": status})
        
        assert response.status_code == 200
        data = response.json()
        for alert in data["alerts"]:
            assert alert["status"] == status
    
    @pytest.mark.parametrize("invalid_status", ["invalid", "OPEN", "closed", ""])
    def test_get_alerts_invalid_status_filter(self, invalid_status):
        """Test retrieving alerts with invalid status filters"""
        response = requests.get(f"{API_BASE}/alerts", params={"status": invalid_status})
        assert response.status_code == 422
    
    @pytest.mark.parametrize("limit", [1, 10, 50, 100, 500])
    def test_get_alerts_valid_limits(self, limit):
        """Test retrieving alerts with various valid limit values"""
        response = requests.get(f"{API_BASE}/alerts", params={"limit": limit})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) <= limit
    
    @pytest.mark.parametrize("invalid_limit", [0, -1, 501, "invalid"])
    def test_get_alerts_invalid_limits(self, invalid_limit):
        """Test retrieving alerts with invalid limit values"""
        response = requests.get(f"{API_BASE}/alerts", params={"limit": invalid_limit})
        assert response.status_code == 422


class TestAlertEventsEndpoint:
    """Test cases for alert events endpoint"""
    
    def test_get_alert_events_valid_alert(self):
        """Test retrieving events for a valid alert (if any exist)"""
        # First get available alerts
        alerts_response = requests.get(f"{API_BASE}/alerts")
        alerts_data = alerts_response.json()
        
        if alerts_data["alerts"]:
            alert_id = alerts_data["alerts"][0]["id"]
            response = requests.get(f"{API_BASE}/alerts/{alert_id}/events")
            
            assert response.status_code == 200
            data = response.json()
            assert "alert_id" in data
            assert "events" in data
            assert "total" in data
            assert data["alert_id"] == alert_id
        else:
            pytest.skip("No alerts available for testing")
    
    def test_get_alert_events_nonexistent_alert(self):
        """Test retrieving events for a nonexistent alert"""
        fake_alert_id = str(uuid.uuid4())
        response = requests.get(f"{API_BASE}/alerts/{fake_alert_id}/events")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.parametrize("invalid_uuid", [
        "not-a-uuid", "12345", "invalid-uuid-format", ""
    ])
    def test_get_alert_events_invalid_uuid(self, invalid_uuid):
        """Test retrieving events with invalid alert UUID format"""
        response = requests.get(f"{API_BASE}/alerts/{invalid_uuid}/events")
        assert response.status_code == 422


class TestAPIErrorHandling:
    """Test cases for API error handling"""
    
    def test_nonexistent_endpoint(self):
        """Test accessing nonexistent endpoint"""
        response = requests.get(f"{API_BASE}/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.parametrize("method,endpoint", [
        ("PUT", "/events"),
        ("DELETE", "/events"),
        ("POST", "/health"),
        ("PUT", "/health"),
        ("DELETE", "/health")
    ])
    def test_method_not_allowed(self, method, endpoint):
        """Test using wrong HTTP methods"""
        response = requests.request(method, f"{API_BASE}{endpoint}")
        assert response.status_code == 405
    
    def test_invalid_json_payload(self):
        """Test sending invalid JSON"""
        headers = {"Content-Type": "application/json"}
        invalid_json = '{"invalid": json}'
        
        response = requests.post(f"{API_BASE}/events", data=invalid_json, headers=headers)
        assert response.status_code == 422
    
    def test_empty_request_body(self):
        """Test sending empty request body"""
        response = requests.post(f"{API_BASE}/events", json={})
        assert response.status_code == 422
    
    def test_malformed_content_type(self, valid_event_data):
        """Test requests with malformed content type"""
        headers = {"Content-Type": "text/plain"}
        
        response = requests.post(f"{API_BASE}/events", json=valid_event_data, headers=headers)
        # FastAPI should handle this gracefully
        assert response.status_code in [201, 422]


class TestAPIValidation:
    """Test cases for comprehensive input validation"""
    
    @pytest.mark.parametrize("field,value", [
        ("user_id", None),
        ("user_id", ""),
        ("device_id", None),
        ("device_id", ""),
        ("event_data", None),
        ("event_data", {})
    ])
    def test_optional_field_validation(self, valid_event_data, field, value):
        """Test validation of optional fields"""
        valid_event_data[field] = value
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        assert response.status_code == 201
    
    def test_extremely_long_strings(self, valid_event_data):
        """Test handling of extremely long strings"""
        long_string = "x" * 10000
        valid_event_data["source_system"] = long_string
        
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        # Should either succeed or fail with validation error
        assert response.status_code in [201, 422]
    
    def test_nested_json_depth(self, valid_event_data):
        """Test handling of deeply nested JSON in event_data"""
        nested_data = {"level1": {"level2": {"level3": {"level4": {"level5": "deep_value"}}}}}
        valid_event_data["event_data"] = nested_data
        
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        assert response.status_code == 201


class TestAPIPerformance:
    """Test cases for API performance"""
    
    def test_response_time_create_event(self, valid_event_data):
        """Test event creation response time"""
        start_time = time.time()
        response = requests.post(f"{API_BASE}/events", json=valid_event_data)
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 3.0  # Should respond within 3 seconds
    
    def test_response_time_get_events(self):
        """Test get events response time"""
        start_time = time.time()
        response = requests.get(f"{API_BASE}/events", params={"limit": 100})
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds
    
    @pytest.mark.slow
    def test_concurrent_event_creation(self, valid_event_data):
        """Test handling concurrent event creation"""
        import concurrent.futures
        
        def create_event(index):
            event = valid_event_data.copy()
            event["user_id"] = f"concurrent_user_{index}"
            response = requests.post(f"{API_BASE}/events", json=event)
            return response.status_code
        
        # Send 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_event, i) for i in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 201 for status in results)


# Mark slow tests
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])