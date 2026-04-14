# SESSION-MANAGEMENT.md - Session Management & Security

## Current Session Implementation

### Starlette SessionMiddleware

```python
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "dev-key-change-in-prod"),
    max_age=3600,  # 1 hour
    same_site="strict",
    https_only=True  # Production
)

@app.post("/login")
def login(request: Request, email: str, password: str):
    if verify_credentials(email, password):
        request.session["user_email"] = email
        request.session["role"] = role
        request.session["login_time"] = datetime.now().isoformat()
        return RedirectResponse("/welcome")
```

### Accessing Session

```python
@app.get("/welcome")
def welcome(request: Request):
    email = request.session.get("user_email")
    if not email:
        return RedirectResponse("/login")
    
    return {"message": f"Welcome {email}"}
```

### Clearing Session (Logout)

```python
@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")
```

---

## Session Security

### HTTPOnly Flag

```python
# Automatically set by SessionMiddleware
# Prevents JavaScript access to session cookies
# Protects against XSS attacks
```

### Secure Flag

```python
# Only transmit cookie over HTTPS
app.add_middleware(
    SessionMiddleware,
    https_only=True
)
```

### SameSite Attribute

```python
# Prevent CSRF attacks
app.add_middleware(
    SessionMiddleware,
    same_site="strict"  # Only same-site requests
)
```

---

## Session Expiration

### Inactivity Timeout

```python
import time

MAX_INACTIVE_TIME = 3600  # 1 hour

@app.middleware("http")
async def session_timeout(request: Request, call_next):
    if "logged_in" in request.session:
        last_activity = request.session.get("last_activity", 0)
        now = time.time()
        
        if (now - last_activity) > MAX_INACTIVE_TIME:
            request.session.clear()
            return RedirectResponse("/login")
        
        # Update last activity
        request.session["last_activity"] = now
    
    return await call_next(request)
```

### Fixed Expiration

```python
from datetime import datetime, timedelta

@app.post("/login")
def login(request: Request, ...):
    # Session expires in 1 hour regardless of activity
    request.session["login_time"] = datetime.now()
    request.session["expires_at"] = (datetime.now() + timedelta(hours=1)).isoformat()
```

---

## Multiple Sessions Per User (Future Feature)

```python
# Track all active sessions for a user
db.execute("""
CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY,
    user_email TEXT,
    session_id TEXT,
    created_at TIMESTAMP,
    last_activity TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN
)
""")

def create_session_record(user_email: str, session_id: str, ip: str, user_agent: str):
    """Track session in database"""
    db.execute(
        "INSERT INTO user_sessions (user_email, session_id, created_at, ip_address, user_agent, is_active) VALUES (?, ?, ?, ?, ?, 1)",
        (user_email, session_id,  datetime.now(), ip, user_agent)
    )

def get_user_sessions(user_email: str):
    """Get all active sessions for user"""
    return db.execute(
        "SELECT * FROM user_sessions WHERE user_email = ? AND is_active = 1",
        (user_email,)
    ).fetchall()

def revoke_session(session_id: str):
    """Logout specific session"""
    db.execute(
        "UPDATE user_sessions SET is_active = 0 WHERE session_id = ?",
        (session_id,)
    )
```

---

## Session Fixation Prevention

```python
# ❌ WRONG: Don't keep same session after login
request.session["authenticated"] = True

# ✅ CORRECT: Regenerate session after authentication
@app.post("/login")
def login(request: Request, ...):
    if verify_credentials(...):
        # Old session is discarded
        old_session = dict(request.session)
        request.session.clear()
        
        # New session created with post-login data
        request.session["user_email"] = email
        request.session["role"] = role
```

---

## Session Hijacking Prevention

### Session Validation

```python
def validate_session(request: Request):
    """Comprehensive session validation"""
    
    session = request.session
    
    # Check if exists
    if "user_email" not in session:
        return False, "No active session"
    
    # Check expiration
    if "expires_at" in session:
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            request.session.clear()
            return False, "Session expired"
    
    # Match IP (optional, user-configurable)
    if "ip_address" in session:
        if session["ip_address"] != request.client.host:
            # Log suspicious activity
            logger.warning(f"Session IP mismatch: {session['ip_address']} vs {request.client.host}")
            # Could force re-authentication
    
    # Match User-Agent (optional)
    if "user_agent" in session:
        if session["user_agent"] != request.headers.get("user-agent"):
            logger.warning("Session User-Agent mismatch")
    
    return True, "Session valid"

@app.middleware("http")
async def validate_sessions(request: Request, call_next):
    if "user_email" in request.session:
        valid, reason = validate_session(request)
        if not valid:
            request.session.clear()
            return RedirectResponse("/login")
    
    return await call_next(request)
```

---

## Session Storage Options (Future)

### Redis Backend

```python
from fastapi_sessions.backends.implementations import RedisBackend
from fastapi_sessions.frontends.implementations import SessionCookie

redis_backend = RedisBackend(redis_client)
session_cookie = SessionCookie(cookie_name="session", backend=redis_backend)

@app.middleware("http")
async def manage_sessions(request: Request, call_next):
    request.state.session = await session_cookie.get_session(request)
    response = await call_next(request)
    await session_cookie.save_session(response, request.session)
    return response
```

### Database Backend

```python
def create_session_db(user_email: str) -> str:
    """Create session in database"""
    session_id = secrets.token_urlsafe(32)
    db.execute(
        "INSERT INTO sessions (id, user_email, created_at) VALUES (?, ?, ?)",
        (session_id, user_email, datetime.now())
    )
    return session_id

def get_session_data(session_id: str):
    """Get session from database"""
    return db.execute(
        "SELECT user_email, role FROM sessions WHERE id = ?",
        (session_id,)
    ).fetchone()
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
