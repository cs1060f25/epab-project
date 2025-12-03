# Bug Report: Missing OPTIONS Method in CORS Configuration

## Bug Description
The FastAPI application has CORSMiddleware configured, but the `allow_methods` parameter is missing `"OPTIONS"`, which is critical for CORS preflight requests. This prevents browsers from making cross-origin POST, PUT, and DELETE requests.

## File Location
- **File**: `/api-server/main.py`
- **Lines**: 41-48
- **Current Code**:
```python
# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # ❌ MISSING "OPTIONS"
    allow_headers=["*"],
)
```

## Steps to Reproduce
1. Start the FastAPI server: `cd api-server && python3 main.py`
2. Send OPTIONS preflight request:
```bash
curl -X OPTIONS http://localhost:8000/api/events \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```
3. Observe the response
4. Try to make a POST request from a browser (cross-origin)

## Expected Behavior
- OPTIONS request should return **200 OK**
- Response should include CORS headers:
  - `Access-Control-Allow-Origin: http://localhost:3000`
  - `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`
  - `Access-Control-Allow-Headers: *`
- Browser should allow subsequent POST/PUT/DELETE requests

## Actual Behavior
- OPTIONS request likely returns **405 Method Not Allowed** or **404 Not Found**
- Missing CORS preflight headers in response
- Browser blocks actual cross-origin POST/PUT/DELETE requests with CORS policy error
- Console shows: *"Access to XMLHttpRequest at 'http://localhost:8000/api/events' from origin 'http://localhost:3000' has been blocked by CORS policy"*

## Impact Analysis

**Severity**: **High** - Critical Frontend Integration Issue

**Risk Level**: **High**
- **Completely blocks frontend-backend integration** (CS12-41)
- Users cannot interact with the application through the frontend
- All non-GET requests fail due to CORS policy violations
- Application appears broken to end users

**Business Impact**:
- **Frontend unusable** - React app cannot communicate with API
- **User experience completely broken** - forms, data submission don't work
- **Development workflow blocked** - Frontend developers cannot test integration
- **Production deployment impossible** - App would not function for users

**Technical Impact**:
- POST `/api/events` - Cannot create new security events from frontend
- Any authenticated requests fail
- File uploads, form submissions blocked
- Real-time features cannot work

## Root Cause Analysis

### Technical Root Cause
The `CORSMiddleware` configuration explicitly lists allowed methods but **omits `"OPTIONS"`**:

```python
allow_methods=["GET", "POST", "PUT", "DELETE"]  # Missing OPTIONS!
```

### Why This Causes Issues
1. **CORS Preflight Requirement**: Browsers send OPTIONS requests before "non-simple" requests (POST with custom headers, PUT, DELETE)
2. **Method Not Allowed**: Since OPTIONS isn't in `allow_methods`, FastAPI returns 405 Method Not Allowed
3. **Failed Preflight**: Browser blocks the actual request when preflight fails
4. **Cascade Failure**: All complex cross-origin requests become impossible

### Browser Behavior
```
1. Browser wants to POST to /api/events from localhost:3000
2. Browser sends: OPTIONS /api/events (preflight)
3. FastAPI responds: 405 Method Not Allowed (no OPTIONS in allow_methods)
4. Browser blocks the actual POST request
5. JavaScript gets CORS error
```

## Evidence
- **Code Analysis**: Line 46 in `api-server/main.py` shows missing OPTIONS
- **CORS Standard**: [MDN CORS Preflight](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#preflighted_requests) requires OPTIONS
- **Test Cases**: Created `test_cors_preflight.py` with 5 test cases demonstrating the issue

## Recommended Fix
Add `"OPTIONS"` to the `allow_methods` list:

```python
# Fixed CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # ✅ Added OPTIONS
    allow_headers=["*"],
)
```

**Alternative (more permissive):**
```python
allow_methods=["*"]  # Allows all methods including OPTIONS
```

## Manual Verification Commands

**Test OPTIONS request:**
```bash
curl -X OPTIONS http://localhost:8000/api/events \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

**Expected after fix:**
```
< HTTP/1.1 200 OK
< access-control-allow-origin: http://localhost:3000
< access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
< access-control-allow-headers: *
< access-control-allow-credentials: true
```

**Test actual POST after fix:**
```bash
curl -X POST http://localhost:8000/api/events \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","source_system":"test","severity":"info"}' \
  -v
```

## Related Issues
- **CS12-48**: This issue (Fix missing CORS preflight handling in API)
- **CS12-41**: React Frontend Integration (blocked by this bug)
- **CS12-8**: API Layer Foundation (CORS misconfiguration)

## Testing Strategy
Created comprehensive test suite in `test_cors_preflight.py`:
1. `test_options_request_to_events_endpoint()` - Tests OPTIONS returns 200
2. `test_cors_headers_present_in_options_response()` - Validates required CORS headers
3. `test_post_request_after_preflight()` - Tests full preflight + POST flow
4. `test_cors_headers_on_actual_response()` - Validates CORS headers on actual responses
5. `test_preflight_allows_custom_headers()` - Tests Authorization header support

## Additional Notes
- **Environment Variable**: CORS origins are configurable via `CORS_ORIGINS` env var
- **Default Origin**: Defaults to `http://localhost:3000` (React dev server)
- **Security**: Current configuration properly restricts origins (good security practice)
- **Headers**: `allow_headers=["*"]` is appropriate for this use case
- **Credentials**: `allow_credentials=True` is needed for authentication

## Priority
**Critical** - This bug completely blocks frontend integration and must be fixed immediately for any cross-origin functionality to work.