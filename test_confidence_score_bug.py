#!/usr/bin/env python3
"""
Test cases to discover and verify the confidence_score validation bug in alerts table
CS12-17: Missing CHECK constraint for confidence_score field
"""

import pytest
from sqlalchemy.exc import IntegrityError
from db import Alert, Base, engine, SessionLocal
import uuid


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Clean up - drop all tables after test
        Base.metadata.drop_all(bind=engine)


def test_valid_confidence_scores(db_session):
    """Test that valid confidence scores (0.0-1.0) are accepted"""
    # Test boundary values and middle value
    valid_scores = [0.0, 0.5, 1.0]
    
    for score in valid_scores:
        alert = Alert(
            title=f"Test Alert with confidence {score}",
            status="open", 
            confidence_score=score
        )
        db_session.add(alert)
        db_session.commit()
        
        # Verify the alert was saved correctly
        saved_alert = db_session.query(Alert).filter_by(title=f"Test Alert with confidence {score}").first()
        assert saved_alert is not None
        assert float(saved_alert.confidence_score) == score


def test_invalid_confidence_score_above_one(db_session):
    """Test that confidence_score > 1.0 is REJECTED"""
    # Try to insert alert with confidence_score = 1.5
    # EXPECTED: Should raise ValueError due to validation
    # FIXED: Now should raise ValueError from our validation
    
    # Test that object creation fails with ValueError
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        alert = Alert(
            title="Test Alert with invalid high confidence",
            status="open",
            confidence_score=1.5  # Invalid - should be rejected
        )
    
    print("FIXED: confidence_score > 1.0 is now properly rejected during object creation")


def test_invalid_confidence_score_below_zero(db_session):
    """Test that confidence_score < 0.0 is REJECTED"""
    # Try to insert alert with confidence_score = -0.5
    # EXPECTED: Should raise ValueError due to validation
    # FIXED: Now should raise ValueError from our validation
    
    # Test that object creation fails with ValueError
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        alert = Alert(
            title="Test Alert with invalid negative confidence",
            status="open",
            confidence_score=-0.5  # Invalid - should be rejected
        )
    
    print("FIXED: confidence_score < 0.0 is now properly rejected during object creation")


def test_invalid_confidence_score_null(db_session):
    """Test that NULL confidence_score is handled correctly"""
    # Check if NULL is allowed - this might be acceptable depending on business rules
    
    alert = Alert(
        title="Test Alert with null confidence",
        status="open",
        confidence_score=None  # NULL value
    )
    
    db_session.add(alert)
    db_session.commit()
    
    # Verify the alert was saved - NULL might be acceptable
    saved_alert = db_session.query(Alert).filter_by(title="Test Alert with null confidence").first()
    assert saved_alert is not None
    assert saved_alert.confidence_score is None
    print("NULL confidence_score is allowed (may be acceptable)")


def test_confidence_score_assignment_validation(db_session):
    """Test that confidence_score validation works when assigning to existing objects"""
    # Create a valid alert first
    alert = Alert(
        title="Test Alert for assignment validation",
        status="open",
        confidence_score=0.5  # Valid initial value
    )
    
    # Test that assigning invalid values raises ValueError
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        alert.confidence_score = 2.0  # Invalid assignment
    
    with pytest.raises(ValueError, match="confidence_score must be between 0.0 and 1.0"):
        alert.confidence_score = -1.0  # Invalid assignment
    
    # Verify that valid assignments still work
    alert.confidence_score = 0.8  # Valid assignment
    assert alert.confidence_score == 0.8
    
    print("FIXED: confidence_score assignment validation is working correctly")


if __name__ == "__main__":
    # Run tests manually to see results
    print("Running confidence_score validation tests...")
    pytest.main([__file__, "-v", "-s"])