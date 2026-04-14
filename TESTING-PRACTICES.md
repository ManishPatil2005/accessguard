# TESTING-PRACTICES.md - Testing Best Practices

## Unit Testing

### Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAuthentication:
    """Test suite for authentication"""
    
    def test_register_success(self):
        """Valid registration should succeed"""
        response = client.post("/register", data={
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "role": "user"
        })
        assert response.status_code == 201
    
    def test_register_weak_password(self):
        """Weak password should fail"""
        response = client.post("/register", data={
            "email": "user@example.com",
            "password": "weak",
            "role": "user"
        })
        assert response.status_code == 422
    
    def test_login_invalid_credentials(self):
        """Invalid credentials should fail"""
        response = client.post("/login", data={
            "email": "nonexistent@example.com",
            "password": "AnyPassword123"
        })
        assert response.status_code == 401
```

### Fixtures

```python
import pytest

@pytest.fixture
def test_user():
    """Create test user"""
    email = "test@example.com"
    password = "TestPass123"
    
    client.post("/register", data={
        "email": email,
        "password": password,
        "role": "user"
    })
    
    return {"email": email, "password": password}

def test_login_with_fixture(test_user):
    """Test login with fixture"""
    response = client.post("/login", data={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 303  # Redirect
```

---

## Test Coverage

### Calculate Coverage

```bash
# Run tests with coverage
pytest --cov=. --cov-report=html

# View coverage report
coverage report
```

### Coverage Goals

```
Overall: 80%+
Critical paths: 100%
  - Authentication: 100%
  - Authorization: 100%
  - Database: 95%+
  - Utilities: 70%+
```

---

## Integration Testing

### Full Flow Testing

```python
def test_full_login_flow():
    """Test complete login workflow"""
    
    # Step 1: Register
    register_response = client.post("/register", data={
        "email": "integration@example.com",
        "password": "IntegrationTest123",
        "role": "user"
    })
    assert register_response.status_code == 201
    
    # Step 2: Login
    login_response = client.post("/login", data={
        "email": "integration@example.com",
        "password": "IntegrationTest123"
    })
    assert login_response.status_code == 303
    
    # Step 3: Access protected page
    welcome_response = client.get("/welcome", cookies=login_response.cookies)
    assert welcome_response.status_code == 200
    assert "integration@example.com" in welcome_response.text
```

---

## Security Testing

### SQL Injection Testing

```python
def test_sql_injection_protection():
    """Verify SQL injection is prevented"""
    
    malicious_inputs = [
        "' OR '1'='1",
        "admin' --",
        "' UNION SELECT * FROM users --",
        "); DROP TABLE users; --"
    ]
    
    for payload in malicious_inputs:
        response = client.post("/login", data={
            "email": payload,
            "password": "AnyPassword123"
        })
        # Should not cause error, just invalid login
        assert response.status_code in [401, 400]
```

### XSS Prevention Testing

```python
def test_xss_prevention():
    """Verify script injection is prevented"""
    
    xss_payload = "<script>alert('xss')</script>"
    
    response = client.post("/register", data={
        "email": xss_payload + "@example.com",
        "password": "Password123",
        "role": "user"
    })
    
    # Check response doesn't execute script
    if response.status_code == 201 or 422:
        assert "<script>" not in response.text
```

---

## Performance Testing

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/

# Using Locust
locust -f locustfile.py --host=http://localhost:8000
```

### Benchmark Script

```python
import time
import statistics

def benchmark_login():
    """Measure login performance"""
    
    times = []
    for i in range(100):
        start = time.perf_counter()
        client.post("/login", data={
            "email": "user@example.com",
            "password": "Password123"
        })
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)  # Convert to ms
    
    return {
        "min": min(times),
        "max": max(times),
        "avg": statistics.mean(times),
        "median": statistics.median(times),
        "p95": sorted(times)[int(len(times) * 0.95)]
    }

results = benchmark_login()
assert results["p95"] < 100  # P95 < 100ms
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest --cov=. --cov-report=term
      - run: pytest --cov=. --cov-report=json
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
