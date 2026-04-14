# SCALING.md - Scaling Strategies

## Horizontal Scaling (Add More Servers)

### Current (Single Server)

```
Browser → Uvicorn:8000 → SQLite:users.db
```

### Scaled (Multiple Servers Behind Load Balancer)

```
Browser 1 → 
Browser 2 → Load Balancer → Uvicorn Server 1 → PostgreSQL
Browser 3 →               → Uvicorn Server 2
                          → Uvicorn Server 3
```

### Load Balancer Configuration (Nginx)

```nginx
upstream accessguard {
    server 10.0.1.1:8000;
    server 10.0.1.2:8000;
    server 10.0.1.3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://accessguard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Vertical Scaling (Bigger Servers)

```
Current: 2 CPU, 4GB RAM, 50GB SSD
→ Upgrade: 8 CPU, 32GB RAM, 500GB SSD

Can handle 10x more concurrent connections with same code
```

---

## Database Scaling

### Read Replicas

```
PostgreSQL Primary → Replication → Replica 1
                                 → Replica 2

Distribute reads across replicas:
- Write-heavy endpoints use Primary
- Read-only endpoints use Replica
```

```python
# Use primary for writes
primary = psycopg2.connect("postgresql://primary:5432/db")

# Use replica for reads
replica = psycopg2.connect("postgresql://replica-1:5432/db")

@app.post("/login")
def login(request: Request, ...):
    # Write goes to primary
    primary.execute("INSERT INTO users ...")

@app.get("/dashboard")
def dashboard(request: Request):
    # Read comes from replica
    results = replica.execute("SELECT * FROM login_attempts ...")
```

### Sharding (Partition by User)

```
Shard Users by Email Domain:

Shard 1: *.com users    → DB1
Shard 2: *.org users    → DB2
Shard 3: *.edu users    → DB3

def get_shard(email: str) -> str:
    domain = email.split("@")[1]
    hash_val = hash(domain) % 3
    return ["db1", "db2", "db3"][hash_val]

@app.post("/login")
def login(request: Request, email: str, ...):
    db = get_shard(email)
    # Use shard-specific database
```

---

## Caching Layer

### Before Caching

```
Browser → FastAPI → Database (100ms)
```

### With Redis Cache

```
Browser → FastAPI → Redis Cache (1ms hit, 100ms miss) → Database
```

```python
import redis

cache = redis.Redis(host='redis-1', port=6379)

def get_user(email: str):
    # Try cache first
    cached = cache.get(f"user:{email}")
    if cached:
        return json.loads(cached)
    
    # Cache miss, query database
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,))
    
    # Store in cache with 1-hour TTL
    cache.setex(f"user:{email}", 3600, json.dumps(user))
    
    return user
```

---

## Asynchronous Tasks

### Background Jobs

```
Current:
Browser → send_email() [blocks] → Response

Background:
Browser → queue_email() → Response
                       ↓
                    Worker 1 sends email
                    Worker 2 sends email
                    Worker 3 sends email
```

```python
from celery import Celery

app = Celery('accessguard', broker='redis://localhost:6379')

@app.task
def send_verification_email(email: str):
    """Run in background"""
    time.sleep(2)  # Email API call
    print(f"Email sent to {email}")

# In main app
@app.post("/register")
def register(request: Request, email: str, ...):
    create_user(email, password)
    
    # Queue email (returns immediately)
    send_verification_email.delay(email)
    
    return {"message": "Account created. Check your email."}
```

---

## CDN for Static Assets

### Before

```
Browser → FastAPI → static/style.css (transfer from origin)
```

### With CDN

```
Browser → CDN Edge 1 (fast, cached) 
         OR
       → CDN Edge 2 → Origin (FastAPI) on first request

CloudFlare/AWS CloudFront caches CSS globally
```

```python
@app.get("/static/style.css")
def get_css():
    response = FileResponse("static/style.css")
    
    # Cache for 1 month on CDN
    response.headers["Cache-Control"] = "public, max-age=2592000"
    
    return response
```

---

## Microservices Architecture (v3.0)

```
Current (Monolithic):
Browser → [FastAPI+Auth+Users+Admin+Email]

Future (Microservices):
Browser → API Gateway → Auth Service
                     → User Service
                     → Admin Service
                     → Email Service
```

---

## Kubernetes Deployment (v3.0)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: accessguard
spec:
  replicas: 10  # Auto-scaled based on load
  
  template:
    spec:
      containers:
      - name: api
        image: accessguard:1.0
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # Auto-restart if healthcheck fails
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## Bottleneck Analysis

### Current (SQLite)

```
Bottleneck: Database (single writer)
- Max writes: 50/sec
- Max concurrent reads: Unlimited

When to scale:
- Error rate increasing
- p95 latency > 500ms
- Database CPU > 80%
```

### After PostgreSQL Migration

```
Bottleneck: Application (Uvicorn workers)
- Each worker: ~100 req/sec
- 4 workers: 400 req/sec

When to scale:
- Application CPU > 80% across all workers
- Memory per worker > 300MB
- Context switching high
```

### After Caching

```
Bottleneck: Network
- API gateway throughput limit
- Load balancer capacity

When to scale:
- Load balancer CPU > 80%
- Network bandwidth at limit
- Connection pool exhausted
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
