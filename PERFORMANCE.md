# PERFORMANCE.md - Performance Tuning Guide

## Database Performance

### Query Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_login_email ON login_attempts(email);
CREATE INDEX idx_login_timestamp ON login_attempts(timestamp DESC);
```

### Bulk Operations
```sql
-- Batch insert (faster than individual INSERTs)
BEGIN TRANSACTION;
INSERT INTO login_attempts VALUES (NULL, 'user1@test.com', '...', 1, 0);
INSERT INTO login_attempts VALUES (NULL, 'user2@test.com', '...', 1, 0);
-- ... more inserts ...
COMMIT;
```

### Archive Old Logs
```sql
-- Move old logs to archive
CREATE TABLE login_attempts_archive AS
SELECT * FROM login_attempts 
WHERE datetime(timestamp) < datetime('now', '-6 months');

DELETE FROM login_attempts 
WHERE datetime(timestamp) < datetime('now', '-6 months');
```

## Application Performance

### Caching Strategy
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_by_email(email: str):
    # Cache user lookups
    ...
```

### Connection Pooling (PostgreSQL)
```python
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://user:password@localhost/accessguard',
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

### Async Support
```python
import asyncio

async def log_login_attempt_async(email, success, is_locked):
    # Non-blocking audit logging
    ...
```

## Monitoring Metrics

### Key Metrics to Track
- Request latency (target: < 500ms)
- Database query time (target: < 100ms)
- Error rate (target: < 0.1%)
- Locked accounts count
- Login attempts per hour
- Cache hit rate

### Prometheus Metrics  
```python
from prometheus_client import Counter, Histogram, Gauge

login_requests = Counter('login_requests_total', 'Total login attempts')
login_latency = Histogram('login_latency_seconds', 'Login request latency')
locked_accounts = Gauge('locked_accounts', 'Current locked account count')
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
