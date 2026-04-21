# Performance & Optimization Guide

## Database Optimization

### Current Limitations (SQLite)
- Single-writer only (concurrent writes may cause locks)
- Best for < 100K records
- Limited query optimization
- File-based (slower than server-based DB)

### Optimization Tips

#### 1. Index Creation
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_login_attempts_email ON login_attempts(email);
CREATE INDEX idx_login_attempts_timestamp ON login_attempts(timestamp);
```

#### 2. Query Optimization
```python
# ✓ Good - Uses index, single query
user = conn.execute(
    "SELECT * FROM users WHERE email = ?", 
    (email,)
).fetchone()

# ✗ Bad - Fetches all records
users = conn.execute("SELECT * FROM users").fetchall()
user = next(u for u in users if u["email"] == email)
```

#### 3. Connection Pooling
```python
# Current: New connection per request
# Future: Use connection pooling for high traffic
from sqlalchemy import create_engine
engine = create_engine("sqlite:///users.db", pool_pre_ping=True)
```

### Scale to Production

**When you need:**
- Concurrent users > 50
- Daily transactions > 10,000
- High availability
- Automatic backups

**Migrate to:**
- PostgreSQL (recommended)
- MySQL
- MariaDB
- Cloud databases (Firebase, MongoDB Atlas)

---

## Application Performance

### Caching Strategies

#### 1. Template Caching (Already Enabled)
```python
# FastAPI caches compiled Jinja2 templates automatically
# Reduces template compilation time on repeated requests
```

#### 2. Static File Caching
```python
# Add cache headers to CSS/JS responses
from fastapi.middleware.cors import CORSMiddleware

# Tell browser to cache for 1 hour
def add_cache_headers(response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response
```

#### 3. Session Data Caching
```python
# Sessions are cached in cookies
# Reduces database queries on each request
# Verify user on sensitive operations only
```

### Load Testing

#### Tools
- **Apache JMeter**: Visual load testing
- **Locust**: Python-based load testing
- **ab** (ApacheBench): Simple command-line tool

#### Example with Locust
```python
from locust import HttpUser, task, between

class UserBehavior(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def login(self):
        self.client.post("/login", data={
            "email": "test@example.com",
            "password": "password"
        })
```

#### Run Test
```bash
locust -f locustfile.py --host=http://localhost:8000
```

---

## Frontend Performance

### CSS Optimization
```css
/* Current: Good */
.glass-card {
    backdrop-filter: blur(10px);
    /* Hardware acceleration on modern browsers */
}

/* Reduce animation complexity for mobile */
@media (max-width: 768px) {
    .aurora {
        animation: none;  /* Disable expensive animations */
    }
}
```

### Image Optimization
```html
<!-- Use modern formats -->
<picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="description">
</picture>
```

### Font Optimization
```css
/* Current: System fonts (✓ Good) */
font-family: "Segoe UI", sans-serif;
/* No external font downloads = faster loading */
```

---

## Monitoring & Metrics

### Key Metrics to Track
1. **Response Time**: < 200ms ideal
2. **Error Rate**: < 0.1% acceptable
3. **Availability**: > 99.9% uptime
4. **Database Load**: CPU < 80%, Memory < 85%
5. **User Sessions**: Active concurrent users

### Add Monitoring

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Logging

```python
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.info(f"Login attempt: {email}")
```

---

## Browser Performance

### Check Performance
```javascript
// In browser console
performance.timing.loadEventEnd - performance.timing.navigationStart
// Shows total load time in ms
```

### Lighthouse Audit
1. Open DevTools (F12)
2. Click "Lighthouse" tab
3. Click "Generate report"
4. Review recommendations

### Target Scores
- Performance: > 80
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

---

## Deployment Performance

### Server Configuration

#### Uvicorn Workers
```bash
# Single worker (current)
python main.py

# Multiple workers for concurrent requests
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

#### Gunicorn with Uvicorn
```bash
# Production setup
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### CDN Setup (For Static Files)
```bash
# Push static files to CDN
# Update template references
<link rel="stylesheet" href="https://cdn.example.com/style.css">
```

### Database Connection String (Production)
```python
# Current: SQLite (local)
DB_PATH = "users.db"

# Production: PostgreSQL
# DB_URL = "postgresql://user:pass@host:5432/accessguard"
```

---

## Security & Performance Trade-offs

| Feature | Performance Cost | Security Benefit |
|---------|-------------------|-----------------|
| Parameterized SQL | +0.1ms | Prevents SQL injection |
| Password hashing | +500ms | Prevents password breach |
| Session validation | +1ms | Prevents CSRF |
| RBAC checks | +0.5ms | Prevents unauthorized access |
| Audit logging | +5ms | Enables investigation |

---

## Optimization Roadmap

### Short-term (Week 1)
- [ ] Add database indexes
- [ ] Enable browser caching
- [ ] Optimize images/assets
- [ ] Minify CSS

### Medium-term (Month 1)
- [ ] Setup CDN for static files
- [ ] Implement caching layer (Redis)
- [ ] Add monitoring/logging
- [ ] Load testing

### Long-term (Month 3+)
- [ ] Migrate to PostgreSQL
- [ ] Implement clustering
- [ ] Auto-scaling setup
- [ ] Advanced analytics

---

## Benchmarks

### Expected Metrics (Current Setup)
- **Page Load**: 500-1000ms
- **Registration**: 100-200ms
- **Login**: 150-300ms (due to hashing)
- **Admin Dashboard**: 200-400ms
- **Database Query**: 1-10ms

### After Optimization
- **Page Load**: 200-400ms
- **Registration**: 50-100ms
- **Login**: 100-200ms
- **Admin Dashboard**: 100-200ms
- **Database Query**: 0.5-2ms

---

## Resources

- [FastAPI Performance Tips](https://fastapi.tiangolo.com/deployment/concepts/)
- [SQLite vs PostgreSQL](https://www.postgresql.org/about/comparisons/sqlite/)
- [Web Vitals](https://web.dev/vitals/)
- [Uvicorn Configuration](https://www.uvicorn.org/configuration/)
