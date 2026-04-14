# EXAMPLES.md - Code Snippets & Usage Examples

## Authentication Examples

### Creating a User Programmatically
```python
import sqlite3
import hashlib

def create_user(email: str, password: str, role: str = "user"):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect("users.db")
    conn.execute(
        "INSERT INTO users (email, password_hash, role,  failed_attempts, is_locked, created_at) VALUES (?, ?, ?, 0, 0, datetime('now'))",
        (email, password_hash, role)
    )
    conn.commit()
    conn.close()
    return email

# Usage
create_user("user@example.com", "SecurePass123", "user")
```

### Checking if User is Admin
```python
from fastapi import HTTPException, status

def require_admin(request: Request):
    session_role = request.session.get("role")
    if session_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return session_role
```

### Password Verification
```python
import hashlib

def verify_password(input_password: str, stored_hash: str) -> bool:
    return hashlib.sha256(input_password.encode()).hexdigest() == stored_hash

# Usage
if verify_password(user_input, db_hash):
    # Login successful
else:
    # Login failed
```

## Database Query Examples

### Get User by Email
```python
conn.execute(
    "SELECT email, role, is_locked FROM users WHERE email = ?",
    (email,)
).fetchone()
```

### Update Last Login
```python
conn.execute(
    "UPDATE users SET last_login = datetime('now') WHERE email = ?",
    (email,)
)
conn.commit()
```

### Count Failed Attempts
```python
attempts = conn.execute(
    "SELECT COUNT(*) FROM login_attempts WHERE email = ? AND success = 0",
    (email,)
).fetchone()[0]
```

### Get Locked Accounts
```python
locked = conn.execute(
    "SELECT email, failed_attempts FROM users WHERE is_locked = 1 ORDER BY email"
).fetchall()
```

## API Usage Examples

### Register via cURL
```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=user@example.com&password=SecurePass123&role=user"
```

### Login via cURL
```bash
curl -X POST http://127.0.0.1:8000/login \
  -c cookies.txt \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=user@example.com&password=SecurePass123"
```

### Access Protected Route
```bash
curl http://127.0.0.1:8000/welcome \
  -b cookies.txt
```

## Testing Examples

### Simulate Failed Login
```python
for i in range(3):
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "wrong_password"
    })
    print(f"Attempt {i+1}: {response.status_code}")
    # Expected: 401, 401, 423

# Verify account locked
account = db.execute(
    "SELECT is_locked FROM users WHERE email = 'test@example.com'"
).fetchone()
assert account[0] == 1  # is_locked = True
```

### Verify Audit Log Entry
```python
entries = db.execute(
    "SELECT * FROM login_attempts WHERE email = ? ORDER BY id DESC LIMIT 1",
    (email,)
).fetchone()

assert entries[2] == timestamp  # timestamp
assert entries[3] == 1 if success else 0  # success
assert entries[4] == is_locked  # is_locked
```

## Integration Examples

### Full User Registration Flow
```python
# 1. Register
register_response = client.post("/register", data={
    "email": "newuser@example.com",
    "password": "NewPassword123",
    "role": "user"
})
assert register_response.status_code == 201

# 2. Login
login_response = client.post(
    "/login",
    data={
        "email": "newuser@example.com",
        "password": "NewPassword123"
    }
)
assert login_response.status_code == 303  # Redirect

# 3. Access protected page
welcome_response = client.get("/welcome", cookies=cookies)
assert welcome_response.status_code == 200
assert "newuser@example.com" in welcome_response.text
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
