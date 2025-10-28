"""
Factory classes for generating test data
"""
import factory
from datetime import datetime, timezone
from decimal import Decimal
from db import Event, Alert, AuditLog


class EventFactory(factory.Factory):
    """Factory for creating Event instances"""
    
    class Meta:
        model = Event
    
    event_type = factory.Iterator(['security', 'identity', 'financial', 'endpoint', 'email'])
    source_system = factory.Faker('company')
    timestamp = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    user_id = factory.Sequence(lambda n: f"user_{n}")
    device_id = factory.Sequence(lambda n: f"device_{n}")
    event_data = factory.LazyFunction(lambda: {
        "ip": factory.Faker('ipv4').generate(),
        "user_agent": factory.Faker('user_agent').generate(),
        "action": factory.Faker('word').generate()
    })
    severity = factory.Iterator(['info', 'low', 'medium', 'high', 'critical'])


class SecurityEventFactory(EventFactory):
    """Factory for security-specific events"""
    
    event_type = 'security'
    source_system = 'auth_service'
    event_data = factory.LazyFunction(lambda: {
        "login_attempt": factory.Iterator(['success', 'failed']).generate(),
        "ip": factory.Faker('ipv4').generate(),
        "location": factory.Faker('city').generate()
    })


class FinancialEventFactory(EventFactory):
    """Factory for financial events"""
    
    event_type = 'financial'
    source_system = 'payment_gateway'
    event_data = factory.LazyFunction(lambda: {
        "transaction_amount": float(factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True).generate()),
        "currency": "USD",
        "risk_score": factory.Faker('pyint', min_value=0, max_value=100).generate()
    })


class AlertFactory(factory.Factory):
    """Factory for creating Alert instances"""
    
    class Meta:
        model = Alert
    
    title = factory.Faker('sentence', nb_words=4)
    status = factory.Iterator(['open', 'investigating', 'resolved'])
    confidence_score = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=0, max_value=100)
    related_event_ids = factory.LazyFunction(lambda: [
        factory.Faker('uuid4').generate(),
        factory.Faker('uuid4').generate()
    ])


class HighConfidenceAlertFactory(AlertFactory):
    """Factory for high-confidence alerts"""
    
    title = factory.LazyAttribute(lambda obj: f"High Confidence Alert - {factory.Faker('word').generate()}")
    confidence_score = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, min_value=80, max_value=100)
    status = factory.Iterator(['open', 'investigating'])


class AuditLogFactory(factory.Factory):
    """Factory for creating AuditLog instances"""
    
    class Meta:
        model = AuditLog
    
    user_id = factory.Sequence(lambda n: f"user_{n}")
    action_type = factory.Iterator([
        'login', 'logout', 'alert_created', 'alert_resolved', 
        'investigation_started', 'evidence_collected'
    ])
    action_details = factory.LazyFunction(lambda: {
        "session_id": factory.Faker('uuid4').generate(),
        "ip_address": factory.Faker('ipv4').generate(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


class SecurityAnalystAuditFactory(AuditLogFactory):
    """Factory for security analyst audit logs"""
    
    user_id = factory.Iterator(['analyst_1', 'analyst_2', 'analyst_3'])
    action_type = factory.Iterator([
        'alert_assigned', 'alert_status_change', 'investigation_started',
        'evidence_collected', 'threat_analysis', 'alert_resolution'
    ])
    action_details = factory.LazyFunction(lambda: {
        "alert_id": factory.Faker('uuid4').generate(),
        "investigation_time_minutes": factory.Faker('pyint', min_value=5, max_value=480).generate(),
        "findings": factory.Faker('sentence').generate()
    })