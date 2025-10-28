# Cybersecurity & Fraud Detection Platform API

A minimal FastAPI server providing REST endpoints for SOC analysts to investigate security incidents and manage events/alerts.

## Features

- 5 core REST endpoints for events and alerts management
- PostgreSQL database integration with connection pooling
- CORS support for frontend development
- Automatic OpenAPI documentation
- Request logging and error handling
- Environment-based configuration

## Prerequisites

- Python 3.11+
- PostgreSQL database (set up from CS12-6)
- pip or pipenv for dependency management

## Setup Instructions

### 1. Install Dependencies

```bash
cd api-server
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your database:

```bash
cp .env.example .env
```

Edit `.env` to match your database configuration:

```bash
DATABASE_URL=postgresql://admin:securepass123@localhost:5432/cyber_fraud_platform
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 3. Verify Database Connection

Make sure your PostgreSQL database is running and accessible:

```bash
# Test database connection using the parent directory's db.py
cd ..
python db.py
cd api-server
```

### 4. Start the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API Base URL**: http://localhost:8000/api
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

**GET** `/api/health`

Returns the API and database health status.

```bash
curl -X GET "http://localhost:8000/api/health"
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Get Events

**GET** `/api/events`

Retrieve security events with optional filtering.

**Query Parameters:**
- `event_type` (optional): Filter by event type (security, identity, financial, endpoint, email)
- `user_id` (optional): Filter by user ID
- `start_date` (optional): Filter events after this date (ISO format)
- `end_date` (optional): Filter events before this date (ISO format)
- `limit` (optional): Maximum events to return (default: 100, max: 1000)

```bash
# Get all events
curl -X GET "http://localhost:8000/api/events"

# Get security events for specific user
curl -X GET "http://localhost:8000/api/events?event_type=security&user_id=user_123&limit=50"

# Get events in date range
curl -X GET "http://localhost:8000/api/events?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z"
```

### 3. Create Event

**POST** `/api/events`

Create a new security event.

**Request Body:**
```json
{
  "event_type": "security",
  "source_system": "firewall",
  "user_id": "user_123",
  "device_id": "device_456",
  "event_data": {
    "ip_address": "192.168.1.100",
    "action": "login_attempt",
    "success": false
  },
  "severity": "medium"
}
```

```bash
curl -X POST "http://localhost:8000/api/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "security",
    "source_system": "test_system",
    "user_id": "user_123",
    "severity": "high",
    "event_data": {"ip": "10.0.0.1", "action": "failed_login"}
  }'
```

### 4. Get Alerts

**GET** `/api/alerts`

Retrieve security alerts with optional filtering.

**Query Parameters:**
- `status` (optional): Filter by status (open, investigating, resolved)
- `limit` (optional): Maximum alerts to return (default: 50, max: 500)

```bash
# Get all alerts
curl -X GET "http://localhost:8000/api/alerts"

# Get open alerts only
curl -X GET "http://localhost:8000/api/alerts?status=open&limit=10"
```

### 5. Get Alert Events

**GET** `/api/alerts/{alert_id}/events`

Retrieve all events linked to a specific alert.

```bash
# Replace with actual alert UUID
curl -X GET "http://localhost:8000/api/alerts/550e8400-e29b-41d4-a716-446655440000/events"
```

## Testing

### Run Automated Tests

```bash
# Make sure the server is running first
python main.py &

# Run the test suite
python test_api.py
```

### Manual Testing with curl

The examples above show how to manually test each endpoint using curl commands.

## Error Handling

The API returns consistent error responses:

```json
{
  "error": "Error message",
  "detail": "Optional additional details"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created (for POST requests)
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Internal Server Error

## Development

### Project Structure

```
api-server/
├── main.py              # FastAPI application with endpoints
├── database.py          # Database connection and session management
├── models.py            # Pydantic request/response models
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── test_api.py          # API endpoint tests
└── README.md           # This file
```

### Adding New Endpoints

1. Define Pydantic models in `models.py`
2. Add endpoint function to `main.py`
3. Update this README with documentation
4. Add tests to `test_api.py`

### Logging

The application logs all requests and errors. Logs include:
- Request timestamp, method, path, and status code
- Request duration
- Database errors and connection issues

## Production Considerations

For production deployment, consider:

1. **Environment Variables**: Use proper secrets management
2. **Database**: Configure connection pooling and timeouts
3. **Security**: Add authentication/authorization middleware
4. **Monitoring**: Integrate with monitoring systems
5. **HTTPS**: Use proper TLS certificates
6. **Rate Limiting**: Add rate limiting middleware
7. **Caching**: Consider Redis for frequently accessed data

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in `.env`
   - Ensure database exists and credentials are correct

2. **Import Errors**
   - Make sure you're running from the `api-server` directory
   - Verify all dependencies are installed

3. **CORS Issues**
   - Check CORS_ORIGINS setting in `.env`
   - Ensure frontend origin is included

### Debugging

Enable debug logging by setting the log level:

```python
logging.basicConfig(level=logging.DEBUG)
```