#!/usr/bin/env python3
"""
Comprehensive Test Suite for Cybersecurity & Fraud Detection Platform API
Tests all endpoints with extensive coverage including edge cases, error handling, and validation
"""

import pytest
import requests
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import time

# Test Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class TestConfig:
    """Test configuration and setup"""
    
    @staticmethod
    def wait_for_server(max_attempts: int = 30, delay: float = 1.0) -> bool:
        """Wait for server to be ready"""
        for i in range(max_attempts):
            try:
                response = requests.get(f"{BASE_URL}/docs", timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(delay)
        return False

    @staticmethod
    def setup_test_data() -> Dict[str, Any]:
        """Create test data for use across tests"""
        return {
            "valid_event": {
                "event_type": "security",
                "source_system": "test_system_comprehensive",
                "user_id": "test_user_comprehensive",
                "device_id": "device_comprehensive",
                "event_data": {
                    "ip_address": "192.168.1.100",
                    "action": "login_attempt",
                    "success": False,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "severity": "high"
            },
            "edge_case_event": {
                "event_type": "financial",
                "source_system": "edge_test_system",
                "user_id": None,
                "device_id": None,
                "event_data": None,
                "severity": "info"
            }
        }


class TestHealthEndpoint:
    """Test cases for /api/health endpoint"""
    
    def test_health_endpoint_success(self):
        """Test health endpoint returns successful response"""
        response = requests.get(f"{API_BASE}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert data["status"] in ["healthy", "unhealthy"]
        assert data["database"] in ["connected", "disconnected"]
    
    def test_health_endpoint_response_structure(self):
        """Test health endpoint response structure matches schema"""
        response = requests.get(f"{API_BASE}/health")
        data = response.json()
        
        required_fields = ["status", "database"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Ensure no extra fields
        assert len(data) == len(required_fields), "Response contains unexpected fields"
    
    def test_health_endpoint_headers(self):
        """Test health endpoint returns correct headers"""
        response = requests.get(f"{API_BASE}/health")
        
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]


class TestEventsEndpoint:
    """Test cases for events endpoints"""
    
    def setup_method(self):
        """Setup test data before each test"""
        self.test_data = TestConfig.setup_test_data()
    
    def test_create_event_success(self):
        """Test successful event creation"""
        response = requests.post(f"{API_BASE}/events", json=self.test_data["valid_event"])
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        required_fields = ["id", "event_type", "source_system", "timestamp", "severity", "created_at"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify data integrity
        assert data["event_type"] == self.test_data["valid_event"]["event_type"]
        assert data["source_system"] == self.test_data["valid_event"]["source_system"]
        assert data["severity"] == self.test_data["valid_event"]["severity"]
        
        # Verify UUID format
        assert uuid.UUID(data["id"])
        
        return data["id"]
    
    def test_create_event_with_minimal_data(self):
        """Test event creation with minimal required data"""
        minimal_event = {
            "event_type": "endpoint",
            "source_system": "minimal_test",
            "severity": "low"
        }
        
        response = requests.post(f"{API_BASE}/events", json=minimal_event)
        assert response.status_code == 201
        
        data = response.json()
        assert data["event_type"] == "endpoint"
        assert data["source_system"] == "minimal_test"
        assert data["severity"] == "low"
        assert data["user_id"] is None
        assert data["device_id"] is None
    
    def test_create_event_invalid_event_type(self):
        """Test event creation with invalid event type"""
        invalid_event = self.test_data["valid_event"].copy()
        invalid_event["event_type"] = "invalid_type"
        
        response = requests.post(f"{API_BASE}/events", json=invalid_event)
        assert response.status_code == 422
        
        data = response.json()
        assert "detail" in data
    
    def test_create_event_invalid_severity(self):
        """Test event creation with invalid severity"""
        invalid_event = self.test_data["valid_event"].copy()
        invalid_event["severity"] = "invalid_severity"
        
        response = requests.post(f"{API_BASE}/events", json=invalid_event)
        assert response.status_code == 422
    
    def test_create_event_missing_required_fields(self):
        """Test event creation with missing required fields"""
        incomplete_events = [
            {},  # Empty
            {"event_type": "security"},  # Missing source_system and severity
            {"source_system": "test"},  # Missing event_type and severity
            {"severity": "high"}  # Missing event_type and source_system
        ]
        
        for incomplete_event in incomplete_events:
            response = requests.post(f"{API_BASE}/events", json=incomplete_event)
            assert response.status_code == 422
    
    def test_create_event_with_large_payload(self):
        """Test event creation with large event_data payload"""
        large_event = self.test_data["valid_event"].copy()
        large_event["event_data"] = {f"field_{i}": f"value_{i}" * 100 for i in range(100)}
        
        response = requests.post(f"{API_BASE}/events", json=large_event)
        assert response.status_code == 201
    
    def test_get_events_no_filters(self):
        """Test retrieving events without filters"""
        # First create some test events
        for i in range(3):
            test_event = self.test_data["valid_event"].copy()
            test_event["user_id"] = f"test_user_{i}"
            requests.post(f"{API_BASE}/events", json=test_event)
        
        response = requests.get(f"{API_BASE}/events")
        assert response.status_code == 200
        
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert isinstance(data["events"], list)
        assert isinstance(data["total"], int)
        assert data["total"] >= 3
    
    def test_get_events_with_event_type_filter(self):
        """Test retrieving events with event_type filter"""
        # Create events of different types
        event_types = ["security", "financial", "identity"]
        for event_type in event_types:
            test_event = self.test_data["valid_event"].copy()
            test_event["event_type"] = event_type
            requests.post(f"{API_BASE}/events", json=test_event)
        
        # Test filtering by event_type
        response = requests.get(f"{API_BASE}/events", params={"event_type": "security"})
        assert response.status_code == 200
        
        data = response.json()
        for event in data["events"]:
            assert event["event_type"] == "security"
    
    def test_get_events_with_user_id_filter(self):
        """Test retrieving events with user_id filter"""
        test_user_id = "specific_test_user_123"
        test_event = self.test_data["valid_event"].copy()
        test_event["user_id"] = test_user_id
        requests.post(f"{API_BASE}/events", json=test_event)
        
        response = requests.get(f"{API_BASE}/events", params={"user_id": test_user_id})
        assert response.status_code == 200
        
        data = response.json()
        for event in data["events"]:
            assert event["user_id"] == test_user_id
    
    def test_get_events_with_date_filters(self):
        """Test retrieving events with date range filters"""
        now = datetime.now(timezone.utc)
        start_date = (now - timedelta(hours=1)).isoformat()
        end_date = (now + timedelta(hours=1)).isoformat()
        
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": 50
        }
        
        response = requests.get(f"{API_BASE}/events", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "events" in data
        assert "total" in data
    
    def test_get_events_with_limit(self):
        """Test retrieving events with limit parameter"""
        # Create multiple events
        for i in range(10):
            test_event = self.test_data["valid_event"].copy()
            test_event["user_id"] = f"limit_test_user_{i}"
            requests.post(f"{API_BASE}/events", json=test_event)
        
        response = requests.get(f"{API_BASE}/events", params={"limit": 5})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["events"]) <= 5
    
    def test_get_events_invalid_limit(self):
        """Test retrieving events with invalid limit values"""
        invalid_limits = [0, -1, 1001, "invalid"]
        
        for limit in invalid_limits:
            response = requests.get(f"{API_BASE}/events", params={"limit": limit})
            assert response.status_code == 422
    
    def test_get_events_invalid_date_format(self):
        """Test retrieving events with invalid date format"""
        invalid_dates = ["not-a-date", "2023-13-45", "2023/01/01"]
        
        for invalid_date in invalid_dates:
            response = requests.get(f"{API_BASE}/events", params={"start_date": invalid_date})
            assert response.status_code == 422


class TestAlertsEndpoint:
    """Test cases for alerts endpoints"""
    
    def test_get_alerts_no_filters(self):
        """Test retrieving alerts without filters"""
        response = requests.get(f"{API_BASE}/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "alerts" in data
        assert "total" in data
        assert isinstance(data["alerts"], list)
        assert isinstance(data["total"], int)
        
        # Verify alert structure if alerts exist
        if data["alerts"]:
            alert = data["alerts"][0]
            required_fields = ["id", "title", "status", "created_at", "event_count"]
            for field in required_fields:
                assert field in alert
    
    def test_get_alerts_with_status_filter(self):
        """Test retrieving alerts with status filter"""
        valid_statuses = ["open", "investigating", "resolved"]
        
        for status in valid_statuses:
            response = requests.get(f"{API_BASE}/alerts", params={"status": status})
            assert response.status_code == 200
            
            data = response.json()
            for alert in data["alerts"]:
                assert alert["status"] == status
    
    def test_get_alerts_invalid_status_filter(self):
        """Test retrieving alerts with invalid status filter"""
        response = requests.get(f"{API_BASE}/alerts", params={"status": "invalid_status"})
        assert response.status_code == 422
    
    def test_get_alerts_with_limit(self):
        """Test retrieving alerts with limit parameter"""
        response = requests.get(f"{API_BASE}/alerts", params={"limit": 10})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["alerts"]) <= 10
    
    def test_get_alerts_invalid_limit(self):
        """Test retrieving alerts with invalid limit values"""
        invalid_limits = [0, -1, 501, "invalid"]
        
        for limit in invalid_limits:
            response = requests.get(f"{API_BASE}/alerts", params={"limit": limit})
            assert response.status_code == 422


class TestAlertEventsEndpoint:
    """Test cases for alert events endpoint"""
    
    def test_get_alert_events_valid_alert(self):
        """Test retrieving events for a valid alert"""
        # First get available alerts
        alerts_response = requests.get(f"{API_BASE}/alerts")
        alerts_data = alerts_response.json()
        
        if alerts_data["alerts"]:
            alert_id = alerts_data["alerts"][0]["id"]
            response = requests.get(f"{API_BASE}/alerts/{alert_id}/events")
            
            # Should return 200 regardless of whether events exist
            assert response.status_code == 200
            
            data = response.json()
            assert "alert_id" in data
            assert "events" in data
            assert "total" in data
            assert data["alert_id"] == alert_id
            assert isinstance(data["events"], list)
            assert isinstance(data["total"], int)
    
    def test_get_alert_events_nonexistent_alert(self):
        """Test retrieving events for a nonexistent alert"""
        fake_alert_id = str(uuid.uuid4())
        response = requests.get(f"{API_BASE}/alerts/{fake_alert_id}/events")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_get_alert_events_invalid_uuid(self):
        """Test retrieving events with invalid alert UUID format"""
        invalid_uuids = ["not-a-uuid", "12345", "invalid-uuid-format"]
        
        for invalid_uuid in invalid_uuids:
            response = requests.get(f"{API_BASE}/alerts/{invalid_uuid}/events")
            assert response.status_code == 422


class TestAPIErrorHandling:
    """Test cases for API error handling and edge cases"""
    
    def test_nonexistent_endpoint(self):
        """Test accessing nonexistent endpoint"""
        response = requests.get(f"{API_BASE}/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test using wrong HTTP methods"""
        # Try PUT on events endpoint (should be POST)
        response = requests.put(f"{API_BASE}/events", json={})
        assert response.status_code == 405
        
        # Try POST on health endpoint (should be GET)
        response = requests.post(f"{API_BASE}/health")
        assert response.status_code == 405
    
    def test_invalid_json_payload(self):
        """Test sending invalid JSON"""
        headers = {"Content-Type": "application/json"}
        invalid_json = '{"invalid": json}'
        
        response = requests.post(f"{API_BASE}/events", data=invalid_json, headers=headers)
        assert response.status_code == 422
    
    def test_malformed_request_headers(self):
        """Test requests with malformed headers"""
        headers = {"Content-Type": "text/plain"}
        valid_event = TestConfig.setup_test_data()["valid_event"]
        
        response = requests.post(f"{API_BASE}/events", json=valid_event, headers=headers)
        # Should still work as FastAPI handles content-type override
        assert response.status_code in [201, 422]
    
    def test_large_request_payload(self):
        """Test extremely large request payload"""
        large_event = TestConfig.setup_test_data()["valid_event"]
        # Create a very large event_data
        large_event["event_data"] = {"large_field": "x" * 10000}
        
        response = requests.post(f"{API_BASE}/events", json=large_event)
        # Should either succeed or fail gracefully
        assert response.status_code in [201, 413, 422, 500]
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import threading
        import concurrent.futures
        
        def create_event(index):
            event = TestConfig.setup_test_data()["valid_event"]
            event["user_id"] = f"concurrent_user_{index}"
            response = requests.post(f"{API_BASE}/events", json=event)
            return response.status_code
        
        # Send 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_event, i) for i in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 201 for status in results)


class TestAPIValidation:
    """Test cases for input validation"""
    
    def setup_method(self):
        """Setup test data before each test"""
        self.test_data = TestConfig.setup_test_data()
    
    def test_event_type_validation(self):
        """Test event_type field validation"""
        valid_types = ["security", "identity", "financial", "endpoint", "email"]
        
        for event_type in valid_types:
            event = self.test_data["valid_event"].copy()
            event["event_type"] = event_type
            response = requests.post(f"{API_BASE}/events", json=event)
            assert response.status_code == 201
    
    def test_severity_validation(self):
        """Test severity field validation"""
        valid_severities = ["info", "low", "medium", "high", "critical"]
        
        for severity in valid_severities:
            event = self.test_data["valid_event"].copy()
            event["severity"] = severity
            response = requests.post(f"{API_BASE}/events", json=event)
            assert response.status_code == 201
    
    def test_string_field_lengths(self):
        """Test string field length validation"""
        # Test extremely long strings
        long_string = "x" * 1000
        
        event = self.test_data["valid_event"].copy()
        event["source_system"] = long_string
        response = requests.post(f"{API_BASE}/events", json=event)
        # Should either succeed or fail with validation error
        assert response.status_code in [201, 422]
    
    def test_null_and_empty_values(self):
        """Test handling of null and empty values"""
        test_cases = [
            {"user_id": None},
            {"user_id": ""},
            {"device_id": None},
            {"device_id": ""},
            {"event_data": None},
            {"event_data": {}}
        ]
        
        for test_case in test_cases:
            event = self.test_data["valid_event"].copy()
            event.update(test_case)
            response = requests.post(f"{API_BASE}/events", json=event)
            assert response.status_code == 201


class TestAPIPerformance:
    """Test cases for API performance"""
    
    def test_response_time_health_check(self):
        """Test health check response time"""
        start_time = time.time()
        response = requests.get(f"{API_BASE}/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Should respond within 2 seconds
    
    def test_response_time_get_events(self):
        """Test get events response time"""
        start_time = time.time()
        response = requests.get(f"{API_BASE}/events", params={"limit": 100})
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Should respond within 5 seconds
    
    def test_pagination_performance(self):
        """Test pagination performance with different limits"""
        limits = [10, 50, 100, 500]
        
        for limit in limits:
            start_time = time.time()
            response = requests.get(f"{API_BASE}/events", params={"limit": limit})
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 10.0  # Should respond within 10 seconds


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive API Test Suite")
    print("=" * 60)
    
    # Wait for server
    if not TestConfig.wait_for_server():
        print("❌ Server not responding. Make sure it's running on port 8000")
        return False
    
    # Test classes to run
    test_classes = [
        TestHealthEndpoint,
        TestEventsEndpoint,
        TestAlertsEndpoint,
        TestAlertEventsEndpoint,
        TestAPIErrorHandling,
        TestAPIValidation,
        TestAPIPerformance
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 40)
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Setup if available
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                # Run test
                getattr(test_instance, test_method)()
                print(f"✅ {test_method}")
                passed_tests += 1
                
            except Exception as e:
                print(f"❌ {test_method}: {str(e)}")
                failed_tests.append(f"{test_class.__name__}.{test_method}: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Comprehensive Test Results Summary")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\n🔍 Failed Tests:")
        for failed_test in failed_tests:
            print(f"  - {failed_test}")
    
    if passed_tests == total_tests:
        print("\n🎉 All comprehensive tests passed! API is robust and working correctly.")
    else:
        print(f"\n⚠️  {len(failed_tests)} tests failed. Review the failures above.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)