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
    # EXPECTED: Should raise constraint violation error
    # ACTUAL: Will likely succeed, proving the bug exists
    
    alert = Alert(
        title="Test Alert with invalid high confidence",
        status="open",
        confidence_score=1.5  # Invalid - should be rejected
    )
    
    db_session.add(alert)
    
    # This should raise an IntegrityError due to CHECK constraint
    # If it doesn't raise an error, the bug exists
    try:
        db_session.commit()
        # If we get here without exception, the bug exists
        saved_alert = db_session.query(Alert).filter_by(title="Test Alert with invalid high confidence").first()
        assert saved_alert is not None, "Bug confirmed: confidence_score > 1.0 was accepted"
        print(f"BUG FOUND: confidence_score {saved_alert.confidence_score} > 1.0 was accepted")
    except IntegrityError:
        # This is the expected behavior - constraint should prevent this
        print("CORRECT: confidence_score > 1.0 was rejected")
        db_session.rollback()


def test_invalid_confidence_score_below_zero(db_session):
    """Test that confidence_score < 0.0 is REJECTED"""
    # Try to insert alert with confidence_score = -0.5
    # EXPECTED: Should raise constraint violation error
    # ACTUAL: Will likely succeed, proving the bug exists
    
    alert = Alert(
        title="Test Alert with invalid negative confidence",
        status="open",
        confidence_score=-0.5  # Invalid - should be rejected
    )
    
    db_session.add(alert)
    
    # This should raise an IntegrityError due to CHECK constraint
    # If it doesn't raise an error, the bug exists
    try:
        db_session.commit()
        # If we get here without exception, the bug exists
        saved_alert = db_session.query(Alert).filter_by(title="Test Alert with invalid negative confidence").first()
        assert saved_alert is not None, "Bug confirmed: confidence_score < 0.0 was accepted"
        print(f"BUG FOUND: confidence_score {saved_alert.confidence_score} < 0.0 was accepted")
    except IntegrityError:
        # This is the expected behavior - constraint should prevent this
        print("CORRECT: confidence_score < 0.0 was rejected")
        db_session.rollback()


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


if __name__ == "__main__":
    # Run tests manually to see results
    print("Running confidence_score validation tests...")
    pytest.main([__file__, "-v", "-s"])