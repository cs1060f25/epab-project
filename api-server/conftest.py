"""
Pytest configuration and shared fixtures for API tests
"""

import pytest
import requests
import time
from typing import Dict, Any

# Test Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


def pytest_addoption(parser):
    """Add command line options for pytest"""
    parser.addoption(
        "--api-url", 
        action="store", 
        default=BASE_URL,
        help="API base URL for testing"
    )
    parser.addoption(
        "--skip-server-check",
        action="store_true",
        default=False,
        help="Skip server availability check"
    )


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "security: marks tests as security tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")


@pytest.fixture(scope="session")
def api_base_url(request):
    """Fixture to get API base URL from command line or config"""
    return request.config.getoption("--api-url") + "/api"


@pytest.fixture(scope="session", autouse=True)
def ensure_server_running(request, api_base_url):
    """Ensure the API server is running before running tests"""
    if request.config.getoption("--skip-server-check"):
        return
    
    base_url = api_base_url.replace("/api", "")
    max_attempts = 30
    
    for i in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/docs", timeout=2)
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    pytest.fail(f"API server is not responding at {base_url}")


@pytest.fixture
def api_client(api_base_url):
    """Fixture providing an API client with base URL"""
    class APIClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
        
        def get(self, endpoint: str, **kwargs):
            return requests.get(f"{self.base_url}{endpoint}", **kwargs)
        
        def post(self, endpoint: str, **kwargs):
            return requests.post(f"{self.base_url}{endpoint}", **kwargs)
        
        def put(self, endpoint: str, **kwargs):
            return requests.put(f"{self.base_url}{endpoint}", **kwargs)
        
        def delete(self, endpoint: str, **kwargs):
            return requests.delete(f"{self.base_url}{endpoint}", **kwargs)
    
    return APIClient(api_base_url)


@pytest.fixture
def sample_event_data():
    """Fixture providing sample event data for testing"""
    return {
        "event_type": "security",
        "source_system": "pytest_test_system",
        "user_id": "pytest_user_123",
        "device_id": "pytest_device_456",
        "event_data": {
            "ip_address": "192.168.1.100",
            "action": "login_attempt",
            "success": False
        },
        "severity": "high"
    }


@pytest.fixture
def minimal_event_data():
    """Fixture providing minimal valid event data"""
    return {
        "event_type": "endpoint",
        "source_system": "pytest_minimal_system",
        "severity": "low"
    }


@pytest.fixture
def created_event(api_client, sample_event_data):
    """Fixture that creates an event and returns the response data"""
    response = api_client.post("/events", json=sample_event_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def multiple_events(api_client, sample_event_data):
    """Fixture that creates multiple events for testing"""
    events = []
    event_types = ["security", "financial", "identity"]
    severities = ["low", "medium", "high"]
    
    for i, (event_type, severity) in enumerate(zip(event_types, severities)):
        event_data = sample_event_data.copy()
        event_data.update({
            "event_type": event_type,
            "severity": severity,
            "user_id": f"test_user_{i}",
            "device_id": f"test_device_{i}"
        })
        
        response = api_client.post("/events", json=event_data)
        assert response.status_code == 201
        events.append(response.json())
    
    return events


@pytest.fixture(scope="session")
def test_data_cleanup():
    """Fixture to track test data for cleanup (if cleanup endpoints existed)"""
    created_items = []
    
    def add_item(item_type: str, item_id: str):
        created_items.append((item_type, item_id))
    
    yield add_item
    
    # Cleanup would happen here if delete endpoints existed
    # For now, we rely on database cleanup between test runs


@pytest.fixture
def performance_timer():
    """Fixture to measure test execution time"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


@pytest.fixture(params=[
    "security", "identity", "financial", "endpoint", "email"
])
def valid_event_type(request):
    """Parametrized fixture for all valid event types"""
    return request.param


@pytest.fixture(params=[
    "info", "low", "medium", "high", "critical"
])
def valid_severity(request):
    """Parametrized fixture for all valid severity levels"""
    return request.param


@pytest.fixture(params=[
    "open", "investigating", "resolved"
])
def valid_alert_status(request):
    """Parametrized fixture for all valid alert statuses"""
    return request.param


# Custom assertions for API testing
def assert_valid_uuid(uuid_string: str):
    """Assert that a string is a valid UUID"""
    import uuid
    try:
        uuid.UUID(uuid_string)
    except ValueError:
        pytest.fail(f"'{uuid_string}' is not a valid UUID")


def assert_valid_datetime(datetime_string: str):
    """Assert that a string is a valid ISO datetime"""
    from datetime import datetime
    try:
        datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"'{datetime_string}' is not a valid ISO datetime")


def assert_event_structure(event_data: Dict[str, Any]):
    """Assert that an event has the correct structure"""
    required_fields = ["id", "event_type", "source_system", "timestamp", "severity", "created_at"]
    
    for field in required_fields:
        assert field in event_data, f"Missing required field: {field}"
    
    assert_valid_uuid(event_data["id"])
    assert_valid_datetime(event_data["timestamp"])
    assert_valid_datetime(event_data["created_at"])
    
    assert event_data["event_type"] in ["security", "identity", "financial", "endpoint", "email"]
    assert event_data["severity"] in ["info", "low", "medium", "high", "critical"]


def assert_alert_structure(alert_data: Dict[str, Any]):
    """Assert that an alert has the correct structure"""
    required_fields = ["id", "title", "status", "created_at", "event_count"]
    
    for field in required_fields:
        assert field in alert_data, f"Missing required field: {field}"
    
    assert_valid_uuid(alert_data["id"])
    assert_valid_datetime(alert_data["created_at"])
    
    assert alert_data["status"] in ["open", "investigating", "resolved"]
    assert isinstance(alert_data["event_count"], int)
    assert alert_data["event_count"] >= 0


# Make custom assertions available to tests
pytest.assert_valid_uuid = assert_valid_uuid
pytest.assert_valid_datetime = assert_valid_datetime
pytest.assert_event_structure = assert_event_structure
pytest.assert_alert_structure = assert_alert_structure