# Bug Report: Missing Confidence Score Validation

## Bug Description
The alerts table accepts confidence_score values outside the valid range (0.0-1.0) because there is no CHECK constraint to validate the input.

## File Location
- **File**: `db.py`
- **Line**: 42
- **Current Code**: `confidence_score = Column(DECIMAL(5, 2), nullable=True)`

## Steps to Reproduce
1. Start the database with `docker-compose up -d postgres`
2. Run the test: `pytest test_confidence_score_bug.py::test_invalid_confidence_score_above_one -v`
3. Observe: Alert with confidence_score = 1.5 is accepted without error
4. Run the test: `pytest test_confidence_score_bug.py::test_invalid_confidence_score_below_zero -v`
5. Observe: Alert with confidence_score = -0.5 is accepted without error

## Expected Behavior
- Confidence scores should be constrained to the range 0.0-1.0
- Attempting to insert confidence_score > 1.0 should raise a constraint violation error
- Attempting to insert confidence_score < 0.0 should raise a constraint violation error

## Actual Behavior
- Database accepts any decimal value for confidence_score
- No validation occurs at the database level
- Invalid confidence scores (like 1.5, -0.5, 999.99) are stored successfully

## Impact Analysis
**Severity**: Medium - Data Integrity Issue

**Risk Level**: Medium
- Invalid confidence scores can lead to incorrect risk assessments
- Dashboard and reporting may display misleading confidence percentages
- Machine learning models consuming this data may make poor decisions based on invalid confidence ranges

**Business Impact**:
- Analysts may misinterpret alert reliability
- Automated systems may incorrectly prioritize alerts
- Data quality issues may propagate to downstream systems

## Root Cause
Missing CHECK constraint in the SQLAlchemy column definition. The current implementation:
```python
confidence_score = Column(DECIMAL(5, 2), nullable=True)
```

Should include a constraint to ensure values are within the valid range.

## Evidence
- **Code Analysis**: Line 42 in db.py shows no CHECK constraint
- **Test Cases**: Created `test_confidence_score_bug.py` with 4 test cases that demonstrate the issue
- **Database Schema**: No constraint visible in the table definition

## Recommended Fix
Add a CHECK constraint to ensure confidence_score values are between 0.0 and 1.0:
```python
from sqlalchemy import CheckConstraint

confidence_score = Column(
    DECIMAL(5, 2), 
    CheckConstraint('confidence_score >= 0.0 AND confidence_score <= 1.0'),
    nullable=True
)
```

## Related Issues
- CS12-17: Test Suite/bug fix for CS12-6
- Potential data quality issues in existing alerts data

## Testing Strategy
- Created comprehensive test suite in `test_confidence_score_bug.py`
- Tests cover valid range (0.0, 0.5, 1.0)
- Tests cover invalid values above 1.0 and below 0.0
- Tests verify NULL handling

## Additional Notes
- The DECIMAL(5,2) precision allows for values like 999.99, which is far outside the expected range
- Consider if confidence_score should be nullable or required
- May need data migration to clean up any existing invalid confidence scores