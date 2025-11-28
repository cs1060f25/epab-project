# API Test Suite Documentation

This directory contains a comprehensive test suite for the Cybersecurity & Fraud Detection Platform API. The test suite includes multiple testing approaches and covers various aspects of API functionality, security, and performance.

## Test Files Overview

### 🔧 Core Test Files

- **`test_api.py`** - Original basic API endpoint testing script
- **`test_comprehensive.py`** - Comprehensive test suite with extensive coverage
- **`test_pytest.py`** - Professional pytest-based test suite with fixtures
- **`test_security.py`** - Security-focused tests (SQL injection, XSS, etc.)

### ⚙️ Configuration Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`pytest.ini`** - Pytest settings and markers
- **`requirements-test.txt`** - Testing dependencies
- **`run_tests.py`** - Test orchestration script

## Test Categories

### 1. Basic API Tests (`test_api.py`)
- Health check endpoint
- Event creation and retrieval
- Alert endpoints
- Basic error handling

### 2. Comprehensive Tests (`test_comprehensive.py`)
- All endpoints with extensive parameter testing
- Edge cases and boundary conditions
- Input validation
- Error handling and status codes
- Performance benchmarks
- Concurrent request handling

### 3. Pytest Suite (`test_pytest.py`)
- Parametrized tests for all valid inputs
- Fixtures for test data management
- Structured test organization
- Custom assertions
- Markers for test categorization

### 4. Security Tests (`test_security.py`)
- SQL injection prevention
- Cross-Site Scripting (XSS) prevention
- Input sanitization
- Authentication bypass attempts
- Denial of Service (DoS) resistance
- Data leakage prevention
- Path traversal protection
- Command injection prevention

## Running Tests

### Prerequisites

1. **API Server Running**: Ensure the API server is running on `http://localhost:8000`
2. **Dependencies**: Install test dependencies (optional, can be auto-installed)

```bash
pip install -r requirements-test.txt
```

### Quick Start

Run all tests with the orchestration script:

```bash
python run_tests.py --all
```

### Individual Test Suites

**Basic Tests:**
```bash
python test_api.py
```

**Comprehensive Tests:**
```bash
python test_comprehensive.py
```

**Pytest Suite:**
```bash
pytest test_pytest.py -v
```

**Security Tests:**
```bash
python test_security.py
```

### Advanced Usage

**Run with coverage:**
```bash
python run_tests.py --pytest --coverage
```

**Run specific test categories:**
```bash
# Security tests only
python run_tests.py --security

# Basic and comprehensive
python run_tests.py --basic --comprehensive

# Pytest with specific markers
python run_tests.py --pytest --markers "not slow"
```

**Generate detailed report:**
```bash
python run_tests.py --all --save-report
```

## Test Orchestration Script (`run_tests.py`)

The `run_tests.py` script provides comprehensive test orchestration with the following features:

### Command Line Options

| Option | Description |
|--------|-------------|
| `--all` | Run all test suites |
| `--basic` | Run basic API tests |
| `--comprehensive` | Run comprehensive test suite |
| `--pytest` | Run pytest-based test suite |
| `--security` | Run security-focused tests |
| `--coverage` | Generate coverage report (pytest only) |
| `--markers` | Filter pytest tests by markers |
| `--save-report` | Save detailed JSON report |
| `--install-deps` | Install test dependencies before running |
| `--skip-server-check` | Skip API server availability check |

### Example Usage

```bash
# Run all tests with coverage and save report
python run_tests.py --all --coverage --save-report

# Run only fast tests
python run_tests.py --pytest --markers "not slow"

# Security audit
python run_tests.py --security --save-report

# Install dependencies and run comprehensive tests
python run_tests.py --comprehensive --install-deps
```

## Test Markers

The pytest suite uses markers to categorize tests:

- `@pytest.mark.slow` - Tests that take longer to execute
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.security` - Security-related tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.smoke` - Basic smoke tests

**Filter tests by markers:**
```bash
# Run only fast tests
pytest -m "not slow"

# Run only security tests
pytest -m "security"

# Run smoke tests only
pytest -m "smoke"
```

## Test Coverage

### Endpoints Covered

1. **GET /api/health** - Health check endpoint
2. **GET /api/events** - Retrieve events with filtering
3. **POST /api/events** - Create new events
4. **GET /api/alerts** - Retrieve alerts with filtering
5. **GET /api/alerts/{alert_id}/events** - Get events for specific alert

### Test Scenarios

#### Positive Tests
- Valid inputs for all parameters
- All supported event types and severity levels
- All supported alert statuses
- Various filtering combinations
- Pagination with different limits

#### Negative Tests
- Invalid input formats
- Missing required fields
- Out-of-range values
- Malformed JSON payloads
- Invalid UUIDs
- Non-existent resources

#### Edge Cases
- Empty responses
- Large payloads
- Unicode and special characters
- Concurrent requests
- Rate limiting behavior

#### Security Tests
- SQL injection attempts
- XSS payload handling
- Input sanitization
- Error message information disclosure
- Authentication bypass attempts
- DoS resistance

## Fixtures and Test Data

### Available Fixtures

- `api_client` - HTTP client with base URL configured
- `sample_event_data` - Complete valid event data
- `minimal_event_data` - Minimal valid event data
- `created_event` - Auto-created event for testing
- `multiple_events` - Multiple events with different properties
- `valid_event_type` - Parametrized valid event types
- `valid_severity` - Parametrized valid severity levels
- `valid_alert_status` - Parametrized valid alert statuses

### Custom Assertions

- `assert_valid_uuid()` - Validate UUID format
- `assert_valid_datetime()` - Validate ISO datetime format
- `assert_event_structure()` - Validate event response structure
- `assert_alert_structure()` - Validate alert response structure

## Performance Testing

### Response Time Benchmarks

- Health check: < 2 seconds
- Event creation: < 3 seconds
- Event retrieval: < 5 seconds
- Alert retrieval: < 5 seconds

### Concurrent Testing

Tests include concurrent request handling to ensure the API can handle multiple simultaneous requests without degradation.

## Security Testing Features

### SQL Injection Testing
- Parameter injection in filters
- Payload injection in event creation
- Database query manipulation attempts

### XSS Prevention Testing
- Script tag injection
- Event handler injection
- JavaScript URL schemes
- HTML entity encoding

### Input Validation Testing
- Oversized payloads
- Deeply nested JSON
- Unicode character handling
- Special character processing

### DoS Resistance Testing
- Rapid request flooding
- Malformed JSON parsing
- Resource exhaustion attempts

## Reporting

### Console Output
All test suites provide detailed console output with:
- Real-time test progress
- Success/failure indicators
- Error details and stack traces
- Performance metrics
- Summary statistics

### JSON Reports
When using `--save-report`, detailed JSON reports include:
- Test execution timestamps
- Individual test results
- Error messages and stack traces
- Performance metrics
- Overall success rates

### Coverage Reports
When using `--coverage`, HTML and terminal coverage reports show:
- Line coverage percentages
- Uncovered code sections
- Branch coverage analysis

## Best Practices

### Running Tests in CI/CD

```bash
# Complete test run with coverage and reporting
python run_tests.py --all --coverage --save-report --install-deps
```

### Local Development

```bash
# Quick smoke test
python run_tests.py --basic

# Full validation before deployment
python run_tests.py --all --save-report
```

### Security Auditing

```bash
# Security-focused testing
python run_tests.py --security --save-report
```

## Troubleshooting

### Common Issues

1. **Server Not Running**
   - Ensure API server is running on port 8000
   - Check server logs for startup errors
   - Use `--skip-server-check` if testing against remote server

2. **Test Dependencies Missing**
   - Use `--install-deps` to auto-install
   - Manually install: `pip install -r requirements-test.txt`

3. **Timeout Issues**
   - Check database connectivity
   - Increase timeout values in test configuration
   - Run tests individually to identify slow tests

4. **Database Connection Issues**
   - Verify database is running and accessible
   - Check database credentials in environment
   - Ensure test data doesn't conflict with existing data

### Debug Mode

For detailed debugging:

```bash
# Pytest with verbose output and no capture
pytest test_pytest.py -v -s --tb=long

# Run single test method
pytest test_pytest.py::TestEventsCreation::test_create_event_valid_data -v
```

## Contributing

When adding new tests:

1. Follow existing naming conventions
2. Add appropriate markers for categorization
3. Include both positive and negative test cases
4. Add security considerations for new endpoints
5. Update this documentation with new test scenarios

## Test Maintenance

- Review and update test data regularly
- Monitor test execution times and optimize slow tests
- Keep security test payloads current with latest threats
- Update dependencies and fix deprecation warnings
- Maintain test coverage above 80%