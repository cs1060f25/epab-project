# AGENTS.md - EPAB: Unified Cyber-Fraud Detection Platform

## Project Overview

**EPAB** is a unified AI-driven cybersecurity and fraud detection platform that correlates security telemetry and financial events to detect cyber-enabled fraud in real-time. The platform combines traditional web authentication, PostgreSQL data storage, and cutting-edge AI/ML capabilities using RAG (Retrieval-Augmented Generation) and vector similarity search.

### Project Type

This is a **hybrid platform** consisting of:
- **Web Application**: Flask-based authentication portal with Auth0 integration
- **Data Pipeline**: Python-based ETL and RAG system for phishing detection
- **Database System**: PostgreSQL-backed event tracking and fraud detection system
- **AI/ML Pipeline**: Google Cloud Platform (GCP) Vertex AI integration for vector similarity search

### Team

- **Eli Pinkus** - Engineering Lead
- **Amit Berger** - Product Lead

### Course Context

CS1060 Fall 2025 - Computer Science for Ethics, Law, and Society

## Technology Stack

### Core Technologies

- **Language**: Python 3.12
- **Web Framework**: Flask 2.0.3+ with Jinja2 templates
- **Authentication**: Auth0 OAuth integration via Authlib 1.0+
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0+ ORM
- **Container Platform**: Docker & Docker Compose
- **Deployment**: Heroku (Procfile configured)

### Cloud & AI/ML Stack

- **Cloud Provider**: Google Cloud Platform (GCP)
  - Google Cloud Storage (data buckets)
  - Vertex AI Vector Search/Matching Engine
  - Regions: us-central1 (pipeline), us-east1 (Vertex AI)
- **ML Frameworks**:
  - sentence-transformers 2.0+ (embeddings)
  - PyTorch 2.0+
  - all-MiniLM-L6-v2 (embedding model)
- **Data Processing**: pandas 2.2.0+, pyarrow 15.0+ (Parquet files)

### Package Management

- **Web App**: pip with `requirements.txt`
- **Data Pipeline**: uv (modern Python package manager) with `pyproject.toml`

## Project Structure

```
epab-project/
├── server.py                       # Flask application entry point (Auth0)
├── db.py                          # SQLAlchemy ORM models & database connection
├── schema.sql                     # PostgreSQL database schema
├── seed_data.sql                  # Sample data for development
├── requirements.txt               # Web app dependencies
├── requirements-test.txt          # Testing dependencies
├── pytest.ini                     # Pytest configuration
├── Dockerfile                     # Web app container
├── docker-compose.yml             # PostgreSQL service definition
├── Procfile                       # Heroku deployment configuration
├── exec.sh                        # Docker build/run helper script
├── readme.md                      # Main project documentation
├── README_TESTS.md                # Comprehensive testing guide
│
├── templates/                     # Flask HTML templates
│   └── home.html
│
├── datapipeline/                  # GCP-integrated data processing & RAG
│   ├── Dockerfile                 # Data pipeline container
│   ├── pyproject.toml            # Pipeline dependencies (uv)
│   ├── uv.lock                   # Dependency lock file
│   ├── generate_fake_emails.py   # Synthetic test data generator
│   ├── dataloader.py             # GCS data download/upload utilities
│   ├── preprocess_clean.py       # Data cleaning pipeline
│   ├── preprocess_rag.py         # RAG preprocessing for Vertex AI
│   ├── query_vertex_ai.py        # Vector similarity search queries
│   └── test_embeddings_local.py  # Local embedding tests
│
└── tests/                         # Comprehensive test suite
    ├── __init__.py
    ├── conftest.py               # Pytest fixtures & configuration
    ├── test_database_connection.py
    ├── test_events.py
    ├── test_alerts.py
    ├── test_audit_log.py
    ├── test_integration.py
    ├── test_factories.py
    ├── test_auth.py              # Auth0 authentication tests
    └── test_preprocess_clean.py  # Data pipeline tests
```

## Database Architecture

### Core Database

- **Name**: `cyber_fraud_platform`
- **Host**: localhost:5432 (development)
- **Credentials**: admin / securepass123 (dev environment only)

### Key Tables

1. **events**: Security, identity, financial, endpoint, and email events with JSONB metadata
2. **alerts**: Confidence-scored alerts with event correlation
3. **audit_log**: Complete action tracking for compliance and auditing

### GCP Resources

- **Project ID**: 1097076476714
- **Storage Buckets**:
  - `rescam-dataset-bucket` (raw data)
  - `rescam-rag-bucket` (processed embeddings)
- **Vertex AI**: Vector Search for phishing email similarity matching

## Environment Variables

The following environment variables are required for full functionality:

```bash
# Flask Application
APP_SECRET_KEY=<your-secret-key>
PORT=3000

# Auth0 Configuration
AUTH0_CLIENT_ID=<your-auth0-client-id>
AUTH0_CLIENT_SECRET=<your-auth0-client-secret>
AUTH0_DOMAIN=<your-auth0-domain>

# Google Cloud Platform
GOOGLE_APPLICATION_CREDENTIALS=<path-to-gcp-credentials.json>
```

**Security Note**: Never commit `.env` files or credentials to version control.

## Development Setup

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 15+ (or use Docker Compose)
- Google Cloud SDK (for data pipeline)
- Auth0 account (for authentication)

### Quick Start

1. **Start PostgreSQL**:
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt  # For testing
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env  # Create from template
   # Edit .env with your credentials
   ```

4. **Run Database Schema**:
   ```bash
   # Connect to PostgreSQL and run schema.sql
   psql -h localhost -U admin -d cyber_fraud_platform -f schema.sql
   ```

5. **Start Web Application**:
   ```bash
   python server.py
   # Or use Docker:
   ./exec.sh
   ```

6. **Access Application**:
   ```
   http://localhost:3000
   ```

### Data Pipeline Setup

```bash
cd datapipeline

# Install dependencies (using uv)
# This is handled automatically by Dockerfile

# Generate synthetic test data
python generate_fake_emails.py

# Clean and preprocess data
python preprocess_clean.py

# Create RAG embeddings
python preprocess_rag.py

# Query vector search
python query_vertex_ai.py
```

## Testing Instructions

### Test Framework

The project uses **pytest** with the following key dependencies:
- pytest 7.4.0+
- pytest-asyncio 0.21.0+ (async test support)
- pytest-cov 4.1.0+ (code coverage)
- pytest-mock 3.11.0+ (mocking)
- TestContainers 3.7.0+ (isolated PostgreSQL instances)
- factory-boy 3.3.0+ (test data factories)
- freezegun 1.2.0+ (time/date mocking)

### Test Structure

Tests are organized by category using pytest markers:
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower, multiple components)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.database` - Database-specific tests

### Running Tests

**Run all tests**:
```bash
pytest
```

**Run specific test categories**:
```bash
pytest -m unit               # Unit tests only
pytest -m integration        # Integration tests only
pytest -m "not slow"        # Skip slow tests
pytest -m database          # Database tests only
```

**Run specific test files**:
```bash
pytest tests/test_events.py
pytest tests/test_auth.py
pytest tests/test_preprocess_clean.py
```

**Run with code coverage**:
```bash
pytest --cov=. --cov-report=html
# View coverage report: open htmlcov/index.html
```

**Run verbose output**:
```bash
pytest -v                    # Verbose
pytest -vv                   # Extra verbose
pytest -s                    # Show print statements
```

### Test Files Overview

- **test_database_connection.py**: Database connectivity and basic operations
- **test_events.py**: Events table CRUD operations
- **test_alerts.py**: Alerts table functionality and confidence scoring
- **test_audit_log.py**: Audit logging and compliance tracking
- **test_integration.py**: End-to-end workflows across multiple components
- **test_factories.py**: Test data factories validation
- **test_auth.py**: Auth0 authentication flow tests
- **test_preprocess_clean.py**: Data pipeline cleaning and validation

### Continuous Integration Plan

**Current Status**: No CI/CD is currently configured.

**Recommended CI/CD Setup** (GitHub Actions):

When implementing CI, add `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: securepass123
          POSTGRES_USER: admin
          POSTGRES_DB: cyber_fraud_platform
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**When CI is implemented**, ensure:
- All tests pass before merging PRs
- Coverage thresholds are maintained (recommend >80%)
- Tests run on Python 3.12+
- PostgreSQL 15 service is available

### Linters and Static Analysis

**Current Status**: No linters or static analysis tools are currently configured.

**If/When Linters Are Added**:

The project would benefit from the following tools:

1. **Code Formatting**:
   ```bash
   black .                    # Code formatter
   isort .                    # Import sorting
   ```

2. **Linting**:
   ```bash
   flake8 .                   # Style guide enforcement
   pylint server.py db.py     # Code analysis
   ruff check .               # Fast modern linter
   ```

3. **Type Checking**:
   ```bash
   mypy server.py db.py       # Static type checking
   ```

4. **Security Scanning**:
   ```bash
   bandit -r .                # Security issue detection
   safety check               # Dependency vulnerability scanning
   ```

**If these tools are configured in the future**, run them before committing code and ensure all checks pass in CI.

### When to Update Tests

**ALWAYS update tests when**:
1. Adding new features or endpoints to `server.py`
2. Modifying database schema in `schema.sql`
3. Changing ORM models in `db.py`
4. Adding new data pipeline components in `datapipeline/`
5. Modifying authentication logic or Auth0 integration
6. Changing business logic or alert confidence scoring
7. Updating API contracts or response formats
8. Fixing bugs (add regression tests)

**Test Update Guidelines**:
- Add new test files for new modules
- Add test cases to existing files for new functionality in existing modules
- Update fixtures in `conftest.py` if test data requirements change
- Update factories if model schemas change
- Run full test suite after changes: `pytest`

### IMPORTANT: Do NOT Modify Existing Tests

**Unless explicitly requested by the user**, you must:
- ❌ **NEVER** modify existing passing tests
- ❌ **NEVER** delete existing test cases
- ❌ **NEVER** comment out failing tests
- ❌ **NEVER** change test assertions to make them pass
- ❌ **NEVER** skip tests using `@pytest.mark.skip` without user approval

**If tests fail after your changes**:
1. Fix your code to make the tests pass
2. If the test is genuinely incorrect, ask the user before modifying it
3. Document why a test change is necessary
4. Ensure the user explicitly approves test modifications

**You MAY**:
- ✅ Add new test cases
- ✅ Add new test files
- ✅ Extend existing tests with additional assertions (if additive)
- ✅ Update test data/fixtures when schema changes require it (with user approval)

### Test Data and Fixtures

**Fixtures Location**: `tests/conftest.py`

Key fixtures available:
- `db_connection`: Clean database connection for each test
- `test_client`: Flask test client for web app testing
- `mock_auth0`: Mocked Auth0 authentication

**Test Factories**: Use factory-boy patterns defined in test files for generating test data.

**Isolation**: Each test runs with an isolated database instance via TestContainers, ensuring no side effects between tests.

### Troubleshooting Tests

**Common Issues**:

1. **PostgreSQL connection failures**:
   ```bash
   docker-compose up -d  # Ensure PostgreSQL is running
   docker-compose ps     # Check status
   ```

2. **Import errors**:
   ```bash
   pip install -r requirements-test.txt
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. **TestContainers failures**:
   - Ensure Docker is running
   - Check Docker disk space: `docker system df`
   - Clean up containers: `docker system prune`

4. **GCP/Vertex AI test failures**:
   - Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set
   - Verify GCP project access and quotas
   - Check network connectivity to GCP

For more detailed troubleshooting, see `README_TESTS.md`.

## Code Style and Best Practices

### General Guidelines

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose
- Avoid deep nesting (max 3-4 levels)

### Security Considerations

**IMPORTANT**: This is a cybersecurity platform handling sensitive data.

- Never commit credentials or API keys to version control
- Validate all user inputs to prevent SQL injection
- Sanitize data before inserting into database
- Use parameterized queries (SQLAlchemy handles this)
- Implement proper authentication and authorization checks
- Log security-relevant events to audit_log table
- Follow OWASP Top 10 security best practices
- Be careful with JSONB fields - validate structure before queries

### Database Operations

- Always use SQLAlchemy ORM rather than raw SQL when possible
- Use transactions for multi-step operations
- Close database connections properly
- Handle connection errors gracefully
- Use connection pooling for production
- Never expose database credentials in logs

### Auth0 Integration

- Validate OAuth tokens on every protected endpoint
- Handle token expiration gracefully
- Don't store Auth0 secrets in code
- Use environment variables for all Auth0 configuration
- Implement proper session management

### GCP/Vertex AI Operations

- Handle GCP API rate limits gracefully
- Implement retry logic with exponential backoff
- Monitor GCP costs (Vertex AI can be expensive)
- Use appropriate regions (us-central1 for pipeline, us-east1 for Vertex AI)
- Clean up temporary files in GCS buckets
- Handle embedding generation failures gracefully

## Common Tasks

### Adding a New Database Table

1. Update `schema.sql` with new table definition
2. Add corresponding SQLAlchemy model in `db.py`
3. Create migration (manual for now - no Alembic configured)
4. Add tests in `tests/test_<table_name>.py`
5. Update seed data if needed in `seed_data.sql`
6. Document the new table in `readme.md`

### Adding a New API Endpoint

1. Add route handler in `server.py`
2. Add authentication decorators if needed
3. Implement request validation
4. Add database operations via SQLAlchemy
5. Create tests in `tests/test_<feature>.py`
6. Update documentation

### Adding New Data Pipeline Component

1. Create new Python script in `datapipeline/`
2. Add dependencies to `datapipeline/pyproject.toml`
3. Update `datapipeline/Dockerfile` if needed
4. Create tests in `tests/test_<component>.py`
5. Document usage in `readme.md`
6. Consider GCS bucket structure and costs

## Documentation

### Existing Documentation

- **readme.md**: Main project overview and quick start guide
- **README_TESTS.md**: Comprehensive testing documentation
- **This file (AGENTS.md)**: Project context for AI agents and contributors
- **Google Drive**: [Project Documentation](https://drive.google.com/drive/u/0/folders/1HPHgI0nW2go5IIYanfdKkL4BBDnZNlZu)

### When to Update Documentation

- Update `readme.md` when adding major features
- Update `README_TESTS.md` when changing test infrastructure
- Update this file when project structure changes significantly
- Add inline code comments for complex logic
- Document all environment variables
- Keep setup instructions current

## Additional Context

### Project Goals

This platform aims to:
1. Detect cyber-enabled fraud by correlating security and financial events
2. Use AI/ML (RAG + vector search) to identify phishing attempts
3. Provide real-time alerts with confidence scoring
4. Maintain comprehensive audit logs for compliance
5. Demonstrate ethical AI principles in cybersecurity

### Current Limitations

- No CI/CD automation (manual testing required)
- No linters configured (manual code review required)
- No database migrations tool (Alembic not configured)
- Auth0 is development configuration (not production-ready)
- GCP costs not fully optimized
- Limited error handling in data pipeline
- No pre-commit hooks configured

### Future Enhancements

- Implement GitHub Actions CI/CD
- Add code linting and formatting tools
- Configure Alembic for database migrations
- Implement comprehensive logging
- Add API rate limiting
- Enhance error handling and recovery
- Add monitoring and alerting
- Optimize GCP costs
- Implement pre-commit hooks

## Agent Instructions

When working on this codebase as an AI agent:

1. **Read First**: Always review existing code before making changes
2. **Test Coverage**: Ensure tests exist for your changes
3. **Security First**: Never introduce security vulnerabilities
4. **Follow Patterns**: Match existing code style and patterns
5. **Database Safety**: Use transactions, handle errors, validate inputs
6. **Documentation**: Update relevant docs when making changes
7. **Ask Questions**: When unclear, ask the user for clarification
8. **Preserve Tests**: Never modify existing tests without explicit user approval
9. **Environment Variables**: Never hardcode credentials or secrets
10. **GCP Costs**: Be mindful of Vertex AI and GCS operations (they cost money)

---

**Last Updated**: 2025-11-10
**Project Version**: HW9 (RAG Integration Complete)
**Python Version**: 3.12
**Database**: PostgreSQL 15
