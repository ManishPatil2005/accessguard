# CACHING.md - Caching Strategy

## Session Caching

### Current Implementation (Cookies)

```python
# Session data is stored in secure cookies
# Every request validates the cookie signature
# No server-side cache needed

@app.post("/login")
def login(request: Request, email: str, password: str):
    if verify_credentials(email, password):
        request.session["user_email"] = email
        request.session["role"] = role
        # Session automatically saved to signed cookie
```

### Future: Redis Session Backend

```python
import redis

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_session(session_id: str) -> dict:
    """Get session data from Redis"""
    data = redis_client.get(f"session:{session_id}")
    return json.loads(data) if data else None

def create_session(user_email: str, role: str) -> str:
    """Create session in Redis"""
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "user_email": user_email,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    redis_client.setex(
        f"session:{session_id}",
        3600,  # 1-hour expiry
        json.dumps(session_data)
    )
    return session_id
```

---

## User Data Caching

### Current: Direct Database Lookups

```python
@app.get("/welcome")
def welcome(request: Request):
    email = request.session.get("user_email")
    # Query database every request
    user = db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    return template.render(user=user)
```

### Future: Cache with TTL

```python
import functools
import time

# Simple in-memory cache
user_cache = {}
CACHE_TTL = 300  # 5 minutes

def get_user_cached(email: str) -> dict:
    """Get user with 5-minute cache"""
    cached = user_cache.get(email)
    
    # Return cached if fresh
    if cached and (time.time() - cached['timestamp']) < CACHE_TTL:
        return cached['data']
    
    # Query database
    user = db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    
    # Store in cache
    user_cache[email] = {
        'data': user,
        'timestamp': time.time()
    }
    
    return user

# Invalidate cache on user update
def update_user(email: str, updates: dict):
    db.execute("UPDATE users SET ... WHERE email = ?", ...)
    user_cache.pop(email, None)  # Clear cache
```

---

## Query Result Caching (Redis)

```python
import redis
import json
import hashlib

redis_client = redis.Redis(host='localhost', port=6379)

def get_login_attempts_cached(email: str) -> list:
    """Cache login attempts for 1 minute"""
    
    # Create cache key
    cache_key = f"login_attempts:{email}"
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query database
    attempts = db.execute(
        "SELECT * FROM login_attempts WHERE email = ? ORDER BY timestamp DESC LIMIT 10",
        (email,)
    ).fetchall()
    
    # Store in cache with 60-second TTL
    redis_client.setex(
        cache_key,
        60,
        json.dumps(attempts)
    )
    
    return attempts
```

---

## HTTP Caching Headers

```python
from fastapi import Response
from datetime import datetime, timedelta

@app.get("/static/style.css")
def get_css(response: Response):
    """CSS should be cached by browser"""
    response.headers["Cache-Control"] = "public, max-age=86400"  # 24 hours
    response.headers["ETag"] = '"abc123"'
    return FileResponse("static/style.css")

@app.get("/")
def home(response: Response):
    """Homepage should not be cached (dynamic)"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return template.render(...)

@app.get("/dashboard")
def dashboard(request: Request, response: Response):
    """Dashboard: cache for 1 minute (user-specific)"""
    response.headers["Cache-Control"] = "private, max-age=60"
    return template.render(...)
```

---

## Invalidation Strategies

### Time-Based (TTL)
```python
# Data expires after fixed time
redis_client.setex(key, 300, value)  # 5 minutes
```

### Event-Based (Invalidate on Change)
```python
def update_user(email: str, data: dict):
    db.execute("UPDATE users SET ... WHERE email = ?", ...)
    redis_client.delete(f"user:{email}")  # Immediate invalidation
```

### Cascade Invalidation
```python
def unlock_account(email: str):
    db.execute("UPDATE users SET is_locked = 0 WHERE email = ?", (email,))
    
    # Invalidate all related caches
    redis_client.delete(f"user:{email}")
    redis_client.delete(f"login_attempts:{email}")
    redis_client.delete(f"account_status:{email}")
```

---

## Cache Warming

```python
def warm_cache():
    """Pre-populate cache on startup"""
    
    # Load all users into cache
    users = db.execute("SELECT * FROM users").fetchall()
    for user in users:
        redis_client.setex(
            f"user:{user['email']}",
            3600,
            json.dumps(user)
        )
    
    logger.info(f"Warmed cache with {len(users)} users")

# Run on startup
@app.on_event("startup")
async def startup():
    warm_cache()
```

---

## Cache Metrics

```python
def get_cache_stats():
    """Monitor cache effectiveness"""
    info = redis_client.info()
    return {
        "used_memory": info['used_memory_human'],
        "connected_clients": info['connected_clients'],
        "evicted_keys": info.get('evicted_keys', 0),
        "hit_rate": (hits / (hits + misses)) if (hits + misses) > 0 else 0
    }

# Target: >80% hit rate for production
```

---

## Cache Problems & Solutions

### Cache Stampede

```
Problem: Multiple requests hit expired cache simultaneously

Solution: Lock + Single Update
```python
lock = threading.Lock()

def get_data_safe(key: str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    
    # Multiple threads wait for lock
    with lock:
        data = redis_client.get(key)  # Double-check
        if data:
            return json.loads(data)
        
        # Only one thread fetches
        fresh_data = fetch_from_db()
        redis_client.setex(key, 300, json.dumps(fresh_data))
        return fresh_data
```

### Cache Coherence

```
Problem: Stale data in cache after update

Solution: Invalidate immediately on write
```python
def update_user(email: str, new_data: dict):
    db.execute("UPDATE users SET ... WHERE email = ?", ...)
    redis_client.delete(f"user:{email}")  # Immediate invalidation
```

### Memory Pressure

```
Problem: Cache grows too large, memory exhausted

Solution: Set max memory and eviction policy
```bash
# In Redis config
maxmemory 256mb
maxmemory-policy allkeys-lru  # Evict least recently used keys
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
