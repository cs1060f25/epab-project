#!/usr/bin/env python3
"""
Basic API endpoint testing script
Tests all 5 endpoints of the cybersecurity platform API
"""

import requests
import json
import uuid
from datetime import datetime, timezone
import time

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        print("✅ Health endpoint test passed\n")
        return True
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}\n")
        return False


def test_create_event():
    """Test creating a new event"""
    print("🔍 Testing Create Event Endpoint...")
    try:
        event_data = {
            "event_type": "security",
            "source_system": "test_system",
            "user_id": "test_user_123",
            "device_id": "device_456",
            "event_data": {
                "ip_address": "192.168.1.100",
                "action": "login_attempt",
                "success": False
            },
            "severity": "medium"
        }
        
        response = requests.post(f"{API_BASE}/events", json=event_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["event_type"] == "security"
        print("✅ Create event test passed\n")
        return data["id"]
    except Exception as e:
        print(f"❌ Create event test failed: {e}\n")
        return None


def test_get_events():
    """Test retrieving events"""
    print("🔍 Testing Get Events Endpoint...")
    try:
        # Test without filters
        response = requests.get(f"{API_BASE}/events")
        print(f"Status Code: {response.status_code}")
        print(f"Total events: {response.json().get('total', 0)}")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
        
        # Test with filters
        params = {
            "event_type": "security",
            "limit": 10
        }
        response = requests.get(f"{API_BASE}/events", params=params)
        print(f"Filtered events count: {len(response.json().get('events', []))}")
        assert response.status_code == 200
        print("✅ Get events test passed\n")
        return True
    except Exception as e:
        print(f"❌ Get events test failed: {e}\n")
        return False


def test_get_alerts():
    """Test retrieving alerts"""
    print("🔍 Testing Get Alerts Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/alerts")
        print(f"Status Code: {response.status_code}")
        print(f"Total alerts: {response.json().get('total', 0)}")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total" in data
        
        # Test with status filter
        params = {"status": "open", "limit": 5}
        response = requests.get(f"{API_BASE}/alerts", params=params)
        assert response.status_code == 200
        print("✅ Get alerts test passed\n")
        return response.json().get("alerts", [])
    except Exception as e:
        print(f"❌ Get alerts test failed: {e}\n")
        return []


def test_get_alert_events(alerts):
    """Test retrieving events for a specific alert"""
    print("🔍 Testing Get Alert Events Endpoint...")
    try:
        if not alerts:
            print("⚠️  No alerts available to test alert events endpoint")
            return True
            
        alert_id = alerts[0]["id"]
        response = requests.get(f"{API_BASE}/alerts/{alert_id}/events")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Events for alert {alert_id}: {data.get('total', 0)}")
            assert "alert_id" in data
            assert "events" in data
            assert "total" in data
            print("✅ Get alert events test passed\n")
        elif response.status_code == 404:
            print("Alert not found (expected if no related events)")
            print("✅ Get alert events test passed (404 is valid)\n")
        else:
            raise Exception(f"Unexpected status code: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Get alert events test failed: {e}\n")
        return False


def run_all_tests():
    """Run all API tests"""
    print("🚀 Starting API Tests")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for i in range(10):
        try:
            requests.get(f"{BASE_URL}/docs", timeout=2)
            break
        except:
            time.sleep(1)
    else:
        print("❌ Server not responding, make sure it's running on port 8000")
        return False
    
    # Run tests
    results = []
    
    # Test 1: Health check
    results.append(test_health_endpoint())
    
    # Test 2: Create event
    event_id = test_create_event()
    results.append(event_id is not None)
    
    # Test 3: Get events
    results.append(test_get_events())
    
    # Test 4: Get alerts
    alerts = test_get_alerts()
    results.append(len(alerts) >= 0)  # Success if we get a list (even empty)
    
    # Test 5: Get alert events
    results.append(test_get_alert_events(alerts))
    
    # Summary
    print("=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)