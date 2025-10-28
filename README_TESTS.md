# Database Test Suite

This test suite provides comprehensive testing for the cybersecurity fraud detection platform database functionality.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Test configuration and fixtures
├── test_database_connection.py # Database connection and setup tests
├── test_events.py              # Events table functionality tests
├── test_alerts.py              # Alerts table functionality tests
├── test_audit_log.py           # Audit log functionality tests
├── test_integration.py         # Cross-table integration tests
└── test_factories.py           # Test data factories
```

## Test Categories

### Unit Tests
- **Database Connection**: Connection, tables, indexes, constraints
- **Events Table**: CRUD operations, constraints, JSON queries, aggregations
- **Alerts Table**: Status management, confidence scores, event relationships
- **Audit Log**: User tracking, action logging, JSON details, security compliance

### Integration Tests
- **Fraud Detection Workflows**: Complete end-to-end scenarios
- **Alert Investigation Lifecycle**: Multi-step investigation processes
- **Bulk Operations**: High-volume data processing
- **Data Retention**: Cleanup and archival operations
- **Concurrency**: Multi-user access patterns

## Prerequisites

### Dependencies
Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Database Setup
The tests use TestContainers to spin up isolated PostgreSQL instances:
- No manual database setup required
- Each test gets a clean database
- Automatic cleanup after tests

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only  
pytest -m integration

# Database tests only
pytest -m database

# Slow tests (excluded by default)
pytest -m slow
```

### Specific Test Files
```bash
# Events table tests
pytest tests/test_events.py

# Integration tests
pytest tests/test_integration.py

# Specific test class
pytest tests/test_alerts.py::TestAlertModel

# Specific test method
pytest tests/test_events.py::TestEventQueries::test_query_by_severity
```

### Coverage Reports
```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

## Test Data

### Fixtures
- `clean_database`: Fresh database session with automatic cleanup
- `sample_event_data`: Pre-configured event data for testing
- `sample_alert_data`: Pre-configured alert data for testing
- `sample_audit_log_data`: Pre-configured audit log data for testing

### Factories
Test data factories are provided for generating realistic test data:
- `EventFactory`: General event creation
- `SecurityEventFactory`: Security-specific events
- `FinancialEventFactory`: Financial transaction events
- `AlertFactory`: General alert creation
- `HighConfidenceAlertFactory`: High-confidence alerts
- `AuditLogFactory`: General audit log entries
- `SecurityAnalystAuditFactory`: Analyst-specific audit logs

## Key Test Scenarios

### Fraud Detection Workflow
Tests the complete flow from suspicious events to alert generation and investigation:
1. Multiple failed login attempts
2. Successful login from new location
3. High-value financial transactions
4. Alert generation with event correlation
5. Investigation workflow with audit trail

### Data Integrity
- Foreign key relationships
- Constraint validation
- JSON data structure preservation
- UUID generation and uniqueness
- Timestamp accuracy

### Security & Compliance
- Audit trail completeness
- User action tracking
- Data access logging
- Investigation workflow documentation

### Performance
- Large JSON payload handling
- Bulk data operations
- Concurrent access patterns
- Query optimization validation

## Configuration

### pytest.ini
The test configuration includes:
- Test discovery patterns
- Coverage reporting
- Custom markers for test categorization
- Output formatting

### Environment Variables
- `DATABASE_URL`: Overrides default test database (if needed)
- `TEST_TIMEOUT`: Sets custom timeout for slow tests

## Continuous Integration

### GitHub Actions Example
```yaml
name: Database Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          pytest -v --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Troubleshooting

### Common Issues

1. **Docker not available**: TestContainers requires Docker
   ```bash
   # Install Docker Desktop or Docker CE
   # Ensure Docker daemon is running
   docker --version
   ```

2. **Port conflicts**: If port 5432 is in use
   ```bash
   # Stop local PostgreSQL
   sudo service postgresql stop
   ```

3. **Slow tests**: Use parallel execution
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

4. **Memory issues with large tests**: Limit test scope
   ```bash
   pytest -m "not slow"
   ```

### Debug Mode
```bash
# Verbose output with debug info
pytest -v -s --tb=long

# Stop on first failure
pytest -x

# Run specific failing test
pytest tests/test_events.py::TestEventModel::test_create_event -v -s
```

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Use appropriate markers (`@pytest.mark.database`, etc.)
3. Ensure tests are isolated and don't depend on external state
4. Add docstrings explaining the test purpose
5. Use factories for test data generation when possible
6. Clean up resources in test teardown