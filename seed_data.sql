-- Sample data for cybersecurity & fraud detection platform
-- Demonstrates a cyber-fraud scenario with compromised account and suspicious transactions

-- Insert sample events (cyber-fraud scenario)
INSERT INTO events (event_type, source_system, timestamp, user_id, device_id, event_data, severity) VALUES
-- Initial suspicious login attempts
('security', 'auth_service', '2024-01-15 14:30:00+00', 'user_12345', 'device_abc123', '{"login_attempt": "failed", "ip": "192.168.1.100", "user_agent": "Mozilla/5.0", "reason": "invalid_password"}', 'medium'),
('security', 'auth_service', '2024-01-15 14:31:15+00', 'user_12345', 'device_abc123', '{"login_attempt": "failed", "ip": "192.168.1.100", "user_agent": "Mozilla/5.0", "reason": "invalid_password"}', 'medium'),
('security', 'auth_service', '2024-01-15 14:32:30+00', 'user_12345', 'device_abc123', '{"login_attempt": "failed", "ip": "192.168.1.100", "user_agent": "Mozilla/5.0", "reason": "invalid_password"}', 'high'),

-- Successful login from different location
('security', 'auth_service', '2024-01-15 14:35:00+00', 'user_12345', 'device_xyz789', '{"login_attempt": "success", "ip": "203.0.113.45", "user_agent": "Chrome/120.0", "location": "Unknown"}', 'high'),

-- Identity verification bypass
('identity', 'kyc_service', '2024-01-15 14:36:00+00', 'user_12345', 'device_xyz789', '{"verification_type": "phone_otp", "status": "bypassed", "method": "social_engineering"}', 'critical'),

-- Suspicious financial transactions
('financial', 'payment_gateway', '2024-01-15 14:40:00+00', 'user_12345', 'device_xyz789', '{"transaction_type": "transfer", "amount": 5000.00, "currency": "USD", "destination": "external_account_999", "risk_score": 85}', 'high'),
('financial', 'payment_gateway', '2024-01-15 14:42:00+00', 'user_12345', 'device_xyz789', '{"transaction_type": "transfer", "amount": 10000.00, "currency": "USD", "destination": "external_account_999", "risk_score": 95}', 'critical'),

-- Endpoint security alerts
('endpoint', 'edr_system', '2024-01-15 14:38:00+00', 'user_12345', 'device_xyz789', '{"process": "keylogger.exe", "action": "process_created", "hash": "a1b2c3d4e5f6", "threat_level": "high"}', 'high'),
('endpoint', 'edr_system', '2024-01-15 14:39:00+00', 'user_12345', 'device_xyz789', '{"network_connection": "suspicious_ip", "destination": "203.0.113.50", "port": 4444, "protocol": "TCP"}', 'medium'),

-- Email security events
('email', 'email_security', '2024-01-15 14:20:00+00', 'user_12345', NULL, '{"email_type": "phishing", "sender": "admin@fake-bank.com", "subject": "Urgent: Verify Your Account", "clicked_link": true}', 'high'),

-- Normal baseline events for comparison
('security', 'auth_service', '2024-01-15 09:00:00+00', 'user_67890', 'device_normal1', '{"login_attempt": "success", "ip": "192.168.1.50", "user_agent": "Safari/17.0", "location": "Home"}', 'info'),
('financial', 'payment_gateway', '2024-01-15 10:30:00+00', 'user_67890', 'device_normal1', '{"transaction_type": "purchase", "amount": 25.99, "currency": "USD", "merchant": "coffee_shop_123", "risk_score": 10}', 'info'),
('security', 'auth_service', '2024-01-15 11:15:00+00', 'user_11111', 'device_normal2', '{"login_attempt": "success", "ip": "10.0.0.25", "user_agent": "Firefox/121.0", "location": "Office"}', 'info'),
('endpoint', 'edr_system', '2024-01-15 12:00:00+00', 'user_11111', 'device_normal2', '{"process": "chrome.exe", "action": "process_created", "hash": "trusted_hash_123", "threat_level": "none"}', 'info'),
('email', 'email_security', '2024-01-15 13:00:00+00', 'user_11111', NULL, '{"email_type": "legitimate", "sender": "newsletter@company.com", "subject": "Weekly Update", "clicked_link": false}', 'info');

-- Insert sample alerts
INSERT INTO alerts (title, status, confidence_score, related_event_ids) VALUES
('Potential Account Takeover - user_12345', 'investigating', 92.5, ARRAY[
    (SELECT id::text FROM events WHERE user_id = 'user_12345' AND event_type = 'security' AND event_data->>'login_attempt' = 'failed' LIMIT 1),
    (SELECT id::text FROM events WHERE user_id = 'user_12345' AND event_type = 'security' AND event_data->>'login_attempt' = 'success' LIMIT 1),
    (SELECT id::text FROM events WHERE user_id = 'user_12345' AND event_type = 'identity' LIMIT 1)
]),

('High-Value Fraud Transaction Detected', 'open', 88.0, ARRAY[
    (SELECT id::text FROM events WHERE user_id = 'user_12345' AND event_type = 'financial' AND (event_data->>'amount')::numeric > 5000 LIMIT 1)
]),

('Malware Detection on Compromised Device', 'open', 95.0, ARRAY[
    (SELECT id::text FROM events WHERE user_id = 'user_12345' AND event_type = 'endpoint' AND event_data->>'process' = 'keylogger.exe' LIMIT 1),
    (SELECT id::text FROM events WHERE user_id = 'user_12345' AND event_type = 'endpoint' AND event_data ? 'network_connection' LIMIT 1)
]);

-- Insert audit log entries
INSERT INTO audit_log (user_id, action_type, action_details) VALUES
('security_analyst_1', 'alert_created', '{"alert_id": "auto-generated", "trigger": "multiple_failed_logins", "user_affected": "user_12345"}'),
('security_analyst_1', 'alert_status_change', '{"alert_id": "1", "old_status": "open", "new_status": "investigating", "reason": "assigned_to_analyst"}'),
('fraud_analyst_2', 'transaction_blocked', '{"user_id": "user_12345", "transaction_amount": 15000.00, "reason": "risk_threshold_exceeded"}'),
('system_admin', 'user_account_locked', '{"user_id": "user_12345", "reason": "suspicious_activity", "lock_duration": "24_hours"}'),
('security_analyst_1', 'threat_hunt_initiated', '{"target": "device_xyz789", "scope": "endpoint_analysis", "tools": ["edr", "network_monitoring"]}')