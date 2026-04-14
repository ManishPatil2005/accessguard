# MONITORING.md - Health Checks & Monitoring

## Health Check Endpoints

### Liveness Probe (Is service running?)

```python
@app.get("/health")
def health_check():
    """Simple liveness check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
```

### Readiness Probe (Can service handle requests?)

```python
@app.get("/ready")
def readiness_check():
    """Check if all dependencies are ready"""
    checks = {}
    
    # Database check
    try:
        conn = sqlite3.connect("users.db")
        conn.execute("SELECT 1")
        conn.close()
        checks["database"] = "ready"
    except Exception:
        checks["database"] = "unavailable"
    
    # Cache check (if Redis)
    try:
        redis_client.ping()
        checks["cache"] = "ready"
    except Exception:
        checks["cache"] = "unavailable"
    
    # Determine overall status
    all_ready = all(v == "ready" for v in checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
```

### Detailed Health Endpoint

```python
@app.get("/api/status")
def detailed_status():
    """Comprehensive system status"""
    return {
        "service": "accessguard",
        "version": "1.0.0",
        "status": "operational",
        "uptime_seconds": get_uptime(),
        "dependencies": {
            "database": {
                "status": "healthy",
                "response_time_ms": 2,
                "connection_count": 1
            },
            "cache": {
                "status": "healthy",
                "hit_rate": 0.85,
                "memory_used_mb": 45
            }
        },
        "metrics": {
            "requests_per_second": 42,
            "error_rate": 0.001,
            "p95_latency_ms": 125,
            "active_users": 234
        },
        "alerts": []  // Empty if all healthy
    }
```

---

## Metrics Collection

### Request Metrics

```python
from time import perf_counter

request_metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_response_time": 0,
    "response_times": []
}

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = perf_counter()
    
    try:
        response = await call_next(request)
        request_metrics["successful_requests"] += 1
    except Exception:
        request_metrics["failed_requests"] += 1
        raise
    finally:
        duration = perf_counter() - start
        request_metrics["total_requests"] += 1
        request_metrics["total_response_time"] += duration
        request_metrics["response_times"].append(duration)
    
    return response

@app.get("/metrics")
def get_metrics():
    """Get collected metrics"""
    response_times = request_metrics["response_times"]
    response_times.sort()
    
    return {
        "total_requests": request_metrics["total_requests"],
        "successful": request_metrics["successful_requests"],
        "failed": request_metrics["failed_requests"],
        "error_rate": request_metrics["failed_requests"] / request_metrics["total_requests"],
        "avg_response_time_ms": (request_metrics["total_response_time"] / request_metrics["total_requests"]) * 1000,
        "p95_response_time_ms": response_times[int(len(response_times) * 0.95)] * 1000,
        "p99_response_time_ms": response_times[int(len(response_times) * 0.99)] * 1000
    }
```

### Business Metrics

```python
def track_login_event(email: str, success: bool):
    """Track login metrics"""
    db.execute(
        """INSERT INTO metrics_logins 
           (timestamp, success, email_domain) 
           VALUES (?, ?, ?)""",
        (datetime.now(), success, email.split('@')[1])
    )

@app.get("/metrics/business")
def get_business_metrics():
    """Business KPIs"""
    
    # Daily active users
    daily_active = db.execute(
        "SELECT COUNT(DISTINCT email) FROM login_attempts WHERE timestamp > datetime('now', '-1 day')"
    ).fetchone()[0]
    
    # Login success rate
    total = db.execute("SELECT COUNT(*) FROM login_attempts").fetchone()[0]
    successful = db.execute(
        "SELECT COUNT(*) FROM login_attempts WHERE success = 1"
    ).fetchone()[0]
    success_rate = successful / total if total > 0 else 0
    
    # Account lockouts
    locked_accounts = db.execute(
        "SELECT COUNT(*) FROM users WHERE is_locked = 1"
    ).fetchone()[0]
    
    return {
        "daily_active_users": daily_active,
        "login_success_rate": success_rate,
        "locked_accounts": locked_accounts,
        "new_registrations_today": get_new_registrations_today()
    }
```

---

## Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: accessguard
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      annotations:
        summary: "High error rate detected"
        
    - alert: HighLatency
      expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
      for: 10m
      annotations:
        summary: "P95 latency > 1 second"
        
    - alert: DatabaseDown
      expr: up{job="accessguard_db"} == 0
      for: 1m
      annotations:
        summary: "Database is down"
        
    - alert: BruteForceAttack
      expr: rate(failed_logins_total[5m]) > 10
      annotations:
        summary: "Potential brute-force attack detected"
```

---

## Dashboards (Grafana)

```json
{
  "dashboard": {
    "title": "AccessGuard Monitoring",
    "panels": [
      {
        "title": "Requests Per Second",
        "targets": [{
          "expr": "rate(http_requests_total[1m])"
        }]
      },
      {
        "title": "Error Rate",
        "targets": [{
          "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
        }]
      },
      {
        "title": "Response Time (p95)",
        "targets": [{
          "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
        }]
      },
      {
        "title": "Database Connections",
        "targets": [{
          "expr": "mysql_global_status_threads_connected"
        }]
      }
    ]
  }
}
```

---

## Health Check Best Practices

- ✅ Return 200 OK when healthy
- ✅ Return 503 Service Unavailable when degraded
- ✅ Include dependencies check (database, cache, etc.)
- ✅ No authentication required on /health
- ✅ Response time < 100ms
- ✅ Don't query external services in health check
- ✅ Regular monitoring (every 10 seconds)

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
