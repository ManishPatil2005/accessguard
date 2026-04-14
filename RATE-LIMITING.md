# RATE-LIMITING.md - Rate Limiting & Throttling

## Rate Limiting Strategy

### Per-IP Rate Limiting

```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.util import get_remote_address
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, email: str = Form(...)):
    """Max 5 login attempts per minute per IP"""
    return handle_login(request, email)

@app.post("/register")
@limiter.limit("3/hour")
def register(request: Request, email: str = Form(...)):
    """Max 3 registrations per hour per IP"""
    return handle_registration(request, email)
```

### Per-User Rate Limiting

```python
from datetime import datetime, timedelta

user_requests = {}  # {user_email: [timestamp1, timestamp2, ...]}

def check_rate_limit(email: str, max_requests: int, time_window: int) -> bool:
    """Check if user exceeded rate limit"""
    
    # Get requests in time window
    now = datetime.now()
    cutoff = now - timedelta(seconds=time_window)
    
    if email not in user_requests:
        user_requests[email] = []
    
    # Remove old requests
    user_requests[email] = [
        req for req in user_requests[email] 
        if req > cutoff
    ]
    
    # Check limit
    if len(user_requests[email]) >= max_requests:
        return False
    
    # Add current request
    user_requests[email].append(now)
    return True

@app.post("/password-reset")
def request_password_reset(email: str):
    """Max 3 reset requests per hour"""
    if not check_rate_limit(email, max_requests=3, time_window=3600):
        raise HTTPException(
            status_code=429,
            detail="Too many password reset attempts. Try again in 1 hour."
        )
    
    # Send reset email
```

---

## Adaptive Rate Limiting

### Increase Limits for Trusted IPs

```python
TRUSTED_IPS = {
    "203.0.113.0/24",  # Office network
}

def is_trusted_ip(ip: str) -> bool:
    """Check if IP is in trust list"""
    import ipaddress
    
    client = ipaddress.ip_address(ip)
    for trusted in TRUSTED_IPS:
        if client in ipaddress.ip_network(trusted, strict=False):
            return True
    return False

def get_rate_limit(ip: str) -> str:
    """Get rate limit for IP"""
    if is_trusted_ip(ip):
        return "100/minute"  # Trusted: 100 per minute
    else:
        return "10/minute"   # Untrusted: 10 per minute

@app.post("/api/endpoint")
@limiter.limit(get_rate_limit)
def endpoint():
    pass
```

---

## Rate Limit Leaky Bucket Algorithm

```python
import time
from collections import defaultdict

class LeakyBucket:
    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = capacity           # Max tokens
        self.leak_rate = leak_rate         # Tokens per second
        self.buckets = defaultdict(lambda: {
            'tokens': capacity,
            'last_update': time.time()
        })
    
    def allow_request(self, identifier: str) -> bool:
        """Check if request is allowed"""
        bucket = self.buckets[identifier]
        now = time.time()
        
        # Add leaked tokens
        elapsed = now - bucket['last_update']
        leaked = elapsed * self.leak_rate
        bucket['tokens'] = min(self.capacity, bucket['tokens'] + leaked)
        bucket['last_update'] = now
        
        # Check if token available
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        
        return False

# Initialize: 10 requests, 5 refill per second
limiter = LeakyBucket(capacity=10, leak_rate=5)

@app.post("/api")
def api_endpoint(request: Request):
    ip = request.client.host
    if not limiter.allow_request(ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

---

## Exponential Backoff for Retries

```python
import time
import random

def retry_with_backoff(func, max_retries: int = 3):
    """Retry with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff: 2^attempt seconds + jitter
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)

# Usage
def api_call():
    # Make API request
    pass

retry_with_backoff(api_call)  # Retries with backoff
```

---

## Rate Limit Headers

```python
from slowapi import templates

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        headers={
            "X-RateLimit-Limit": "10",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1234567890",
            "Retry-After": "60"
        },
        content={
            "detail": "Rate limit exceeded. Retry after 60 seconds."
        }
    )
```

---

## Circuit Breaker Pattern (Failure Handling)

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Too many failures
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.last_failure_time = None
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
breaker = CircuitBreaker()

@app.get("/external-api")
def call_external_api():
    try:
        return breaker.call(fetch_from_external_api)
    except Exception:
        return {"error": "Service unavailable, try again later"}
```

---

## Monitoring Rate Limits

```python
def get_rate_limit_stats():
    """Get rate limit metrics"""
    return {
        "total_requests": 15000,
        "rate_limited_requests": 250,
        "rate_limit_percentage": 1.67,
        "top_ips": [
            {"ip": "203.0.113.1", "requests": 5000},
            {"ip": "203.0.113.2", "requests": 4500}
        ],
        "alert": "1.67% of requests are rate limited (acceptable)"
    }

# Alert if > 5% of requests are rate limited
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
