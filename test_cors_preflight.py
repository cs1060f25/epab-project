#!/usr/bin/env python3
"""
Test cases to discover and verify the CORS preflight bug in FastAPI app
CS12-48: Missing OPTIONS method in allow_methods configuration

The bug: CORSMiddleware is configured but allow_methods doesn't include "OPTIONS",
causing preflight requests to fail.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add api-server to path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api-server'))

from main import app

client = TestClient(app)


def test_options_request_to_events_endpoint():
    """Test that OPTIONS preflight request to /api/events returns 200"""
    # Send OPTIONS request with Origin header
    # EXPECTED: 200 OK with CORS headers
    # ACTUAL: Will likely fail due to missing OPTIONS in allow_methods
    
    response = client.options(
        "/api/events",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    
    print(f"OPTIONS /api/events response:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    # This test will reveal if OPTIONS is properly handled
    if response.status_code == 200:
        print("✅ OPTIONS request succeeded")
        assert "access-control-allow-origin" in response.headers
    else:
        print(f"❌ OPTIONS request failed with {response.status_code}")
        print("BUG CONFIRMED: OPTIONS preflight request is not properly handled")
        # Don't assert failure yet - we want to document the bug first
    
    return response


def test_cors_headers_present_in_options_response():
    """Test that OPTIONS response includes required CORS headers"""
    # Send OPTIONS to /api/events from origin http://localhost:3000
    # EXPECTED: Response includes:
    #   - Access-Control-Allow-Origin: http://localhost:3000 (or *)
    #   - Access-Control-Allow-Methods: POST, GET, OPTIONS, etc.
    #   - Access-Control-Allow-Headers: Content-Type, etc.
    # ACTUAL: Missing due to OPTIONS not being in allow_methods
    
    response = client.options(
        "/api/events",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
    )
    
    headers = response.headers
    print(f"\nCORS Headers Analysis:")
    print(f"Access-Control-Allow-Origin: {headers.get('access-control-allow-origin', 'MISSING')}")
    print(f"Access-Control-Allow-Methods: {headers.get('access-control-allow-methods', 'MISSING')}")
    print(f"Access-Control-Allow-Headers: {headers.get('access-control-allow-headers', 'MISSING')}")
    print(f"Access-Control-Allow-Credentials: {headers.get('access-control-allow-credentials', 'MISSING')}")
    
    expected_headers = [
        "access-control-allow-origin",
        "access-control-allow-methods", 
        "access-control-allow-headers"
    ]
    
    missing_headers = []
    for header in expected_headers:
        if header not in headers:
            missing_headers.append(header)
    
    if missing_headers:
        print(f"❌ Missing CORS headers: {missing_headers}")
        print("BUG CONFIRMED: CORS preflight headers are missing")
    else:
        print("✅ All required CORS headers present")
        # Verify OPTIONS is in allow-methods
        allow_methods = headers.get('access-control-allow-methods', '').lower()
        if 'options' not in allow_methods:
            print("❌ OPTIONS method not in Access-Control-Allow-Methods")
            print("BUG CONFIRMED: OPTIONS method missing from allowed methods")
    
    return response


def test_post_request_after_preflight():
    """Test that POST request succeeds after OPTIONS preflight"""
    # 1. Send OPTIONS preflight
    # 2. Send actual POST request with Origin header
    # EXPECTED: POST succeeds with proper CORS headers
    # ACTUAL: May fail if preflight doesn't work properly
    
    print(f"\n=== Testing POST after preflight ===")
    
    # Step 1: Preflight request
    preflight_response = client.options(
        "/api/events",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    
    print(f"Preflight OPTIONS status: {preflight_response.status_code}")
    
    # Step 2: Actual POST request
    post_data = {
        "event_type": "login_attempt",
        "source_system": "auth_service",
        "user_id": "test_user_123",
        "device_id": "device_456",
        "event_data": {"ip": "192.168.1.100", "user_agent": "test"},
        "severity": "info"
    }
    
    post_response = client.post(
        "/api/events",
        json=post_data,
        headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json"
        }
    )
    
    print(f"POST /api/events status: {post_response.status_code}")
    print(f"POST response CORS header: {post_response.headers.get('access-control-allow-origin', 'MISSING')}")
    
    if post_response.status_code in [200, 201]:
        print("✅ POST request succeeded")
        # Check if CORS headers are present in actual response
        if "access-control-allow-origin" in post_response.headers:
            print("✅ CORS headers present in POST response")
        else:
            print("❌ CORS headers missing in POST response")
    else:
        print(f"❌ POST request failed: {post_response.status_code}")
        if hasattr(post_response, 'json'):
            try:
                print(f"Error: {post_response.json()}")
            except:
                print(f"Response text: {post_response.text}")


def test_cors_headers_on_actual_response():
    """Test that actual API responses include CORS headers"""
    # Send GET /api/events with Origin: http://localhost:3000
    # EXPECTED: Response includes Access-Control-Allow-Origin header
    # ACTUAL: Should work since GET is in allow_methods, but verify
    
    response = client.get(
        "/api/events",
        headers={
            "Origin": "http://localhost:3000"
        }
    )
    
    print(f"\n=== Actual GET request CORS test ===")
    print(f"GET /api/events status: {response.status_code}")
    print(f"Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin', 'MISSING')}")
    print(f"Access-Control-Allow-Credentials: {response.headers.get('access-control-allow-credentials', 'MISSING')}")
    
    if response.status_code == 200:
        print("✅ GET request succeeded")
        if "access-control-allow-origin" in response.headers:
            print("✅ CORS headers present in GET response")
        else:
            print("❌ CORS headers missing in GET response")
    else:
        print(f"❌ GET request failed: {response.status_code}")


def test_preflight_allows_custom_headers():
    """Test that preflight allows custom headers like Authorization"""
    # Send OPTIONS with Access-Control-Request-Headers: authorization
    # EXPECTED: Access-Control-Allow-Headers includes authorization
    # ACTUAL: May work since allow_headers=["*"], but verify
    
    response = client.options(
        "/api/alerts",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization,X-Custom-Header,Content-Type"
        }
    )
    
    print(f"\n=== Custom headers preflight test ===")
    print(f"OPTIONS /api/alerts status: {response.status_code}")
    
    if response.status_code == 200:
        allowed_headers = response.headers.get('access-control-allow-headers', '')
        print(f"Access-Control-Allow-Headers: {allowed_headers}")
        
        if allowed_headers == '*' or 'authorization' in allowed_headers.lower():
            print("✅ Custom headers (Authorization) are allowed")
        else:
            print("❌ Custom headers (Authorization) not explicitly allowed")
    else:
        print(f"❌ OPTIONS request failed: {response.status_code}")
        print("BUG CONFIRMED: Preflight request for custom headers failed")


if __name__ == "__main__":
    print("="*60)
    print("CORS PREFLIGHT BUG DISCOVERY TESTS")
    print("="*60)
    
    print("\nRunning CORS preflight tests to identify the bug...")
    print("Expected bug: OPTIONS method missing from allow_methods in CORSMiddleware")
    
    # Run each test individually to get detailed output
    try:
        test_options_request_to_events_endpoint()
        test_cors_headers_present_in_options_response()
        test_post_request_after_preflight() 
        test_cors_headers_on_actual_response()
        test_preflight_allows_custom_headers()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("SUMMARY: Run 'pytest test_cors_preflight.py -v -s' for full test results")
    print("="*60)