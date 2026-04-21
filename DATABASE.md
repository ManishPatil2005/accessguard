# Database Design & Schema Documentation

## Overview

AccessGuard uses SQLite for data persistence. This document covers:
- Database schema design
- Data relationships
- Constraints and validations
- Query patterns
- Backup and recovery

---

## Schema

### users Table

**Purpose**: Store user accounts and authentication data

```sql
CREATE TABLE users (
    email TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    is_locked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
```

#### Fields

| Field | Type | Constraints | Purpose |
|-------|------|-----------|---------|
| `email` | TEXT | PRIMARY KEY | Unique user identifier |
| `password_hash` | TEXT | NOT NULL | SHA-256 hashed password |
| `role` | TEXT | NOT NULL, CHECK | User role (admin or user) |
| `failed_attempts` | INTEGER | DEFAULT 0 | Failed login counter |
| `is_locked` | INTEGER | DEFAULT 0 | Account lock status (1=locked) |
| `created_at` | TEXT | NOT NULL | Account creation timestamp (UTC) |

#### Constraints Explanation

```python
# Role must be 'admin' or 'user'
CHECK(role IN ('admin', 'user'))

# Email uniqueness enforced by PRIMARY KEY
# No two users can have same email

# Default values set to 0
# Enables safe INSERT without specifying these fields
```

#### Sample Data

```sql
-- User account
INSERT INTO users VALUES (
    'user@example.com',
    'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
    'user',
    0,
    0,
    '2024-01-15 10:30:00 UTC'
);

-- Admin account
INSERT INTO users VALUES (
    'admin@example.com',
    '8d969eef6ecad3c29a3a873fba3f81f9f3c9f7c4d8e1a2b3c4d5e6f7a8b9c0d1',
    'admin',
    0,
    0,
    '2024-01-10 09:00:00 UTC'
);

-- Locked account
INSERT INTO users VALUES (
    'locked@example.com',
    'b3a8e0e1c9f16af6b5d3c8b9a0f1e2d3c4b5a6f7e8d9c0b1a2f3e4d5c6b7a8',
    'user',
    3,
    1,
    '2024-01-20 14:45:00 UTC'
);
```

---

### login_attempts Table

**Purpose**: Audit log of all authentication events

```sql
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    success INTEGER NOT NULL,
    is_locked INTEGER NOT NULL
);
```

#### Fields

| Field | Type | Purpose |
|-------|------|---------|
| `id` | INTEGER | Auto-incrementing record ID |
| `email` | TEXT | Email of account (non-unique, many per user) |
| `timestamp` | TEXT | UTC timestamp of login attempt |
| `success` | INTEGER | 1 = successful, 0 = failed |
| `is_locked` | INTEGER | 1 = account was locked at time, 0 = not locked |

#### Sample Data

```sql
-- Successful login
INSERT INTO login_attempts VALUES (
    NULL,  -- Auto-increment
    'user@example.com',
    '2024-01-21 10:30:00 UTC',
    1,  -- success=true
    0   -- account not locked
);

-- Failed login (account not locked)
INSERT INTO login_attempts VALUES (
    NULL,
    'user@example.com',
    '2024-01-21 10:32:00 UTC',
    0,  -- success=false
    0   -- account not locked
);

-- Failed login (account locked)
INSERT INTO login_attempts VALUES (
    NULL,
    'attacker@example.com',
    '2024-01-21 10:35:00 UTC',
    0,  -- success=false
    1   -- account was/is locked
);
```

---

## Data Relationships

### Email as Foreign Key

Although not enforced at DB level, `login_attempts.email` logically references `users.email`:

```
users.email ──────→ login_attempts.email
    (1)                  (many)
    
One user can have many login attempts
```

### Example Query

```python
# Get all login attempts for a specific user
attempts = conn.execute(
    "SELECT * FROM login_attempts WHERE email = ? ORDER BY timestamp DESC",
    ("user@example.com",)
).fetchall()
```

---

## Lifecycle & State Transitions

### User Account States

```
┌─────────────────────────────────────────────────────────┐
│                   Account Creation                      │
│                                                         │
│  email, password_hash, role, failed_attempts=0, locked=0│
└────────────────────────┬────────────────────────────────┘
                         │
                    LOGIN ATTEMPT
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ↓                ↓                ↓
    CORRECT         INCORRECT         LOCKED
    PASSWORD        PASSWORD           ACCOUNT
        │                │                │
        │                │           (requires admin)
        │                ↓                │
        │          failed_attempts++      │
        │                │                │
        │           Is 3+ fails?          │
        │                │                │
        │         ┌──────┴──────┐         │
        │         │             │         │
        │        NO            YES        │
        │         │             │         │
        │         │         is_locked=1   │
        │         │             │         │
        │         └──────┬──────┘         │
        │                │                │
        ↓                ↓                ↓
    UNLOCK          LOCKED            LOCKED
    failed_attempts=0         (stays until admin action)
    is_locked=0
        │
        │ (next login)
        │
        └──────────→ (cycle repeats)
```

---

## Query Patterns

### 1. User Authentication

```python
# Get user by email (password verification)
user = conn.execute(
    "SELECT email, password_hash, role, is_locked FROM users WHERE email = ?",
    (email,)
).fetchone()
```

### 2. Update Failed Attempts

```python
# Increment failed attempts and lock if needed
conn.execute(
    "UPDATE users SET failed_attempts = ?, is_locked = ? WHERE email = ?",
    (failed_attempts + 1, should_lock, email)
)
```

### 3. Reset Failed Attempts (Successful Login)

```python
# Clear failed attempts on successful login
conn.execute(
    "UPDATE users SET failed_attempts = 0 WHERE email = ?",
    (email,)
)
```

### 4. Unlock Account (Admin)

```python
# Admin unlock
conn.execute(
    "UPDATE users SET is_locked = 0, failed_attempts = 0 WHERE email = ?",
    (email,)
)
```

### 5. Log Login Attempt

```python
# Record every login attempt
conn.execute(
    "INSERT INTO login_attempts (email, timestamp, success, is_locked) VALUES (?, ?, ?, ?)",
    (email, timestamp, success_int, locked_int)
)
```

### 6. Get All Locked Accounts

```python
# For admin dashboard
locked_accounts = conn.execute(
    "SELECT email, role, created_at, failed_attempts FROM users WHERE is_locked = 1"
).fetchall()
```

### 7. Get Login Audit Log

```python
# Recent login attempts (last 100)
recent_attempts = conn.execute(
    "SELECT email, timestamp, success, is_locked FROM login_attempts ORDER BY timestamp DESC LIMIT 100"
).fetchall()
```

### 8. Get User Account Status

```python
# Full account information (for dashboard display)
user = conn.execute(
    "SELECT email, role, failed_attempts, is_locked, created_at FROM users WHERE email = ?",
    (email,)
).fetchone()
```

---

## Indexes

### Recommended Indexes (For Performance)

```sql
-- Email lookup (very frequent)
CREATE INDEX idx_users_email ON users(email);

-- Role filtering (used in queries)
CREATE INDEX idx_users_role ON users(role);

-- Lock status filtering (admin dashboard)
CREATE INDEX idx_users_is_locked ON users(is_locked);

-- Login attempt queries (audit log)
CREATE INDEX idx_login_email ON login_attempts(email);

-- Timestamp ordering (recent attempts first)
CREATE INDEX idx_login_timestamp ON login_attempts(timestamp DESC);

-- Combined index for common query
CREATE INDEX idx_login_email_timestamp ON login_attempts(email, timestamp DESC);
```

### Add Indexes

```bash
# Connect to database
sqlite3 users.db < indexes.sql

# Or in Python
conn = sqlite3.connect("users.db")
conn.execute("CREATE INDEX idx_users_email ON users(email)")
conn.commit()
```

---

## Constraints & Validation

### Database Level

```sql
-- Email must be unique (PRIMARY KEY)
-- Role must be 'admin' or 'user' (CHECK)
-- All required fields must be present (NOT NULL)
```

### Application Level

```python
# Email validation
import re
email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
assert re.match(email_pattern, email)

# Password length
assert len(password) >= 8

# Role validation
assert role in {'admin', 'user'}

# Parameterized queries (SQL injection prevention)
conn.execute("SELECT * FROM users WHERE email = ?", (email,))
```

---

## Backup & Recovery

### Backup Database

```bash
# Simple file copy (when app is stopped)
cp users.db users.db.backup

# Or with SQLite backup command
sqlite3 users.db ".backup users.db.backup"
```

### Restore Database

```bash
# Restore from backup
cp users.db.backup users.db

# Or
sqlite3 users.db ".restore users.db.backup"
```

### Export Data

```bash
# Export all users to CSV
sqlite3 -header -csv users.db "SELECT email, role, created_at FROM users;" > users.csv

# Export login attempts
sqlite3 -header -csv users.db "SELECT email, timestamp, success FROM login_attempts;" > login_attempts.csv
```

### Import Data

```bash
# Import users from CSV
sqlite3 users.db ".mode csv" ".import users.csv users_import"
```

---

## Migration (SQLite → PostgreSQL)

When scaling beyond SQLite:

```python
# PostgreSQL equivalent
from sqlalchemy import create_engine, Column, String, Integer, Text
from sqlalchemy.orm import declarative_base, Session

engine = create_engine("postgresql://user:password@localhost/accessguard")
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    email = Column(String(255), primary_key=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    failed_attempts = Column(Integer, default=0)
    is_locked = Column(Integer, default=0)
    created_at = Column(String(255), nullable=False)

Base.metadata.create_all(engine)
```

---

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| User lookup by email | <1ms | With index |
| Password hashing | 200-500ms | SHA-256 computation |
| Database write (login attempt) | 5-10ms | Disk I/O |
| Admin dashboard (all locked) | 10-50ms | Depends on user count |

---

## Troubleshooting

### Database Locked Error

```
sqlite3.OperationalError: database is locked
```

**Cause**: Multiple processes writing simultaneously  
**Solution**: 
```python
conn = sqlite3.connect("users.db", timeout=10)  # Wait up to 10 seconds
```

### Corrupted Database

```bash
# Verify database integrity
sqlite3 users.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp users.db.backup users.db
```

---

## Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQL Syntax Guide](https://www.w3schools.com/sql/)
- [Database Design Best Practices](https://en.wikipedia.org/wiki/Database_design)
