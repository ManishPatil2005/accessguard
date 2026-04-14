# DOCKER.md - Container Deployment Guide

## Dockerfile (v1.0)

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build Command**:
```bash
docker build -t accessguard:1.0 .
```

**Run Command**:
```bash
docker run -p 8000:8000 accessguard:1.0
```

---

## docker-compose.yml (Development)

```yaml
version: '3.9'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=1
      - SECRET_KEY=dev-secret-key-change-in-production
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: accessguard
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Start Development**:
```bash
docker-compose up
```

---

## Multi-Stage Build (Production)

```dockerfile
# Build stage
FROM python:3.13 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Benefits**:
- Smaller image (multi-stage removes build dependencies)
- No root user running app
- Optimized for production

---

## Docker Registry

### AWS ECR
```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag accessguard:1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/accessguard:1.0

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/accessguard:1.0

# Pull & run
docker run -p 8000:8000 123456789.dkr.ecr.us-east-1.amazonaws.com/accessguard:1.0
```

### Docker Hub
```bash
# Tag
docker tag accessguard:1.0 myusername/accessguard:1.0

# Login
docker login

# Push
docker push myusername/accessguard:1.0

# Pull & run
docker run -p 8000:8000 myusername/accessguard:1.0
```

---

## Kubernetes Deployment (v3.0)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: accessguard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: accessguard
  template:
    metadata:
      labels:
        app: accessguard
    spec:
      containers:
      - name: accessguard
        image: myregistry.azurecr.io/accessguard:1.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: accessguard-secrets
              key: database_url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: accessguard-secrets
              key: secret_key
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: accessguard-service
spec:
  selector:
    app: accessguard
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy**:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get pods
kubectl logs -f <pod-name>
```

---

## Health Checks

```python
# Add to main.py
@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
def ready():
    # Check database connectivity
    try:
        conn = sqlite3.connect("users.db")
        conn.execute("SELECT 1")
        conn.close()
        return {"ready": True}
    except:
        return {"ready": False}, 503
```

---

## Environment Variables in Docker

```bash
docker run -p 8000:8000 \
  -e DEBUG=0 \
  -e SECRET_KEY=production-secret-key \
  -e DATABASE_URL=postgresql://user:pass@db:5432/accessguard \
  accessguard:1.0
```

Or with a .env file:
```bash
docker run -p 8000:8000 \
  --env-file .env \
  accessguard:1.0
```

---

## Security Best Practices

### Non-Root User
```dockerfile
RUN useradd -m appuser
USER appuser
```

### Read-Only Filesystem
```yaml
securityContext:
  readOnlyRootFilesystem: true
```

### Resource Limits
```yaml
resources:
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### No Privileged Access
```yaml
securityContext:
  privileged: false
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
