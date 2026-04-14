# ERRORS.md - Error Handling & HTTP Status Codes

## HTTP Status Code Reference

### 2xx Success

| Code | Name | When | Example |
|------|------|------|---------|
| 200 | OK | Request succeeded | GET /dashboard returns user data |
| 201 | Created | Resource created | POST /register creates new user |
| 303 | See Other | Redirect after POST | POST /login → redirect to /welcome |

### 4xx Client Errors

| Code | Name | When | Example |
|------|------|------|---------|
| 400 | Bad Request | Invalid input | Missing required field |
| 401 | Unauthorized | Auth failure | Wrong password |
| 403 | Forbidden | Auth success, no permission | User accessing /dashboard |
| 404 | Not Found | Resource doesn't exist | GET /nonexistent |
| 409 | Conflict | Resource already exists | POST /register with existing email |
| 422 | Unprocessable Entity | Validation fails | Password too weak |
| 429 | Too Many Requests | Rate limit exceeded | 100 requests in 1 minute |

### 5xx Server Errors

| Code | Name | When | Example |
|------|------|------|---------|
| 500 | Internal Server Error | Unexpected error | Database connection lost |
| 503 | Service Unavailable | Server down | Database migration in progress |

---

## Error Response Format

### Standard Error Response

```python
from fastapi import HTTPException, status

@app.post("/login")
def login(request: Request, email: str, password: str):
    if not is_valid_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    user = get_user(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if user['is_locked']:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked due to too many failed attempts"
        )
```

### JSON Error Response

```json
{
    "detail": "Invalid credentials",
    "status_code": 401,
    "error": "unauthorized"
}
```

### HTML Error Response

```html
<div class="alert alert-danger">
    <h4>Login Failed</h4>
    <p>Invalid email or password. Try again.</p>
</div>
```

---

## Error Categories

### Authentication Errors

```python
class AuthenticationError(Exception):
    """Base authentication error"""
    status_code = 401
    detail = "Invalid credentials"

class InvalidPasswordError(AuthenticationError):
    detail = "Invalid password"

class AccountLockedError(AuthenticationError):
    status_code = 423  # Locked
    detail = "Account locked. Contact admin to unlock"

class InvalidTokenError(AuthenticationError):
    detail = "Invalid session token"
```

### Validation Errors

```python
class ValidationError(Exception):
    """Base validation error"""
    status_code = 422

class PasswordWeakError(ValidationError):
    detail = "Password must be at least 8 characters"

class EmailInvalidError(ValidationError):
    detail = "Invalid email format"

class DuplicateEmailError(Exception):
    status_code = 409
    detail = "Email already registered"
```

### Authorization Errors

```python
class AuthorizationError(Exception):
    """Base authorization error"""
    status_code = 403

class AdminRequiredError(AuthorizationError):
    detail = "Admin access required"

class InsufficientPermissions(AuthorizationError):
    detail = "You don't have permission to access this resource"
```

---

## Error Handling Strategy

### Catch & Log Errors

```python
import logging
from typing import Callable
from functools import wraps

logger = logging.getLogger(__name__)

def handle_errors(func: Callable):
    """Decorator to catch and log errors"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AuthenticationError as e:
            logger.warning(f"Authentication failed: {e.detail}")
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        except ValidationError as e:
            logger.warning(f"Validation failed: {e.detail}")
            raise HTTPException(status_code=422, detail=e.detail)
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper

@app.post("/login")
@handle_errors
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # Implementation
```

### User-Friendly Error Messages

```python
# ❌ BAD: Technical error messages
"KeyError: 'email' on line 42 of main.py"

# ✅ GOOD: User-friendly messages  
"Email address is required"

# ✅ GOOD: Actionable messages
"Account locked. Please contact support to unlock."
```

### Logging Error Context

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_error(error_type: str, details: dict):
    """Log structured error information"""
    logger.error(json.dumps({
        "error_type": error_type,
        "timestamp": datetime.now().isoformat(),
        "details": details,
        "status": "error"
    }))

# Usage
try:
    user = get_user(email)
except KeyError:
    log_error("user_not_found", {"email": email})
```

---

## Error Response Examples

### Login - Wrong Password

```
HTTP/1.1 401 Unauthorized

{
    "detail": "Invalid email or password",
    "status_code": 401
}
```

### Register - Password Too Weak

```
HTTP/1.1 422 Unprocessable Entity

{
    "detail": "Password must contain: uppercase, lowercase, number, special character",
    "status_code": 422,
    "requirements": [
        "At least 8 characters",
        "One uppercase letter (A-Z)",
        "One lowercase letter (a-z)",
        "One number (0-9)",
        "One special character (!@#$%^&*)"
    ]
}
```

### Admin Endpoint - Not Authorized

```
HTTP/1.1 403 Forbidden

{
    "detail": "Admin access required",
    "status_code": 403
}
```

### Account Locked

```
HTTP/1.1 423 Locked

{
    "detail": "Account locked due to too many failed login attempts. Please contact an administrator.",
    "status_code": 423,
    "error": "account_locked",
    "retry_after": null
}
```

---

## Monitoring & Alerts

### Error Rate Tracking

```python
from datetime import datetime, timedelta

error_counts = {}

def track_error(error_type: str):
    """Track errors for alerting"""
    now = datetime.now()
    key = f"{error_type}_{now.strftime('%Y-%m-%d %H:00')}"
    error_counts[key] = error_counts.get(key, 0) + 1
    
    # Alert if > 50 errors in an hour
    if error_counts[key] > 50:
        send_alert(f"High error rate: {error_type}")

# Alert thresholds
ALERT_THRESHOLDS = {
    "authentication_error": 50,  # per hour
    "validation_error": 100,     # per hour
    "internal_error": 10,        # per hour
}
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
