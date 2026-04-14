# MIGRATION.md - Database Migration Guide

## SQLite to PostgreSQL Migration (v2.0)

### Why Migrate?

| Feature | SQLite | PostgreSQL |
|---------|--------|-----------|
| Concurrency | Single writer ❌ | Multiple writers ✅ |
| Scale | Up to 1M records | 1B+ records ✅ |
| Replication | No | Yes ✅ |
| Full-text search | Limited | Advanced ✅ |
| JSON support | Basic | Advanced ✅ |
| Performance | Good (local) | Excellent (distributed) |

### Step 1: Set Up PostgreSQL

```sql
CREATE DATABASE accessguard_production;
CREATE USER accessguard WITH PASSWORD 'secure_password';
ALTER ROLE accessguard WITH CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE accessguard_production TO accessguard;
```

### Step 2: Schema Conversion

**Original SQLite**:
```sql
CREATE TABLE users (
    email TEXT PRIMARY KEY,
    password_hash TEXT,
    role TEXT,
    failed_attempts INTEGER DEFAULT 0,
    is_locked INTEGER DEFAULT 0,
    created_at TEXT
);

CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY,
    email TEXT,
    timestamp TEXT,
    success INTEGER,
    is_locked INTEGER
);
```

**PostgreSQL**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    failed_attempts INTEGER DEFAULT 0,
    is_locked BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE login_attempts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    success BOOLEAN NOT NULL,
    is_locked BOOLEAN DEFAULT false,
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_login_attempts_email ON login_attempts(email);
CREATE INDEX idx_login_attempts_timestamp ON login_attempts(timestamp);
```

### Step 3: Data Migration Script

```python
import sqlite3
import psycopg2
from datetime import datetime

# Connect to both databases
sqlite_conn = sqlite3.connect('users.db')
sqlite_cursor = sqlite_conn.cursor()

postgres_conn = psycopg2.connect(
    host='localhost',
    database='accessguard_production',
    user='accessguard',
    password='secure_password'
)
postgres_cursor = postgres_conn.cursor()

# Migrate users
sqlite_cursor.execute("SELECT * FROM users")
for row in sqlite_cursor.fetchall():
    email, password_hash, role, failed_attempts, is_locked, created_at = row
    postgres_cursor.execute(
        "INSERT INTO users (email, password_hash, role, failed_attempts, is_locked, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (email, password_hash, role, failed_attempts, bool(is_locked), created_at)
    )

# Migrate login attempts
sqlite_cursor.execute("SELECT * FROM login_attempts")
for row in sqlite_cursor.fetchall():
    id_, email, timestamp, success, is_locked = row
    postgres_cursor.execute(
        "INSERT INTO login_attempts (email, timestamp, success, is_locked) VALUES (%s, %s, %s, %s)",
        (email, timestamp, bool(success), bool(is_locked))
    )

postgres_conn.commit()
postgres_cursor.close()
postgres_conn.close()
sqlite_conn.close()

print("Migration complete!")
```

### Step 4: Update Application Code

**Before (SQLite)**:
```python
import sqlite3
conn = sqlite3.connect("users.db")
```

**After (PostgreSQL)**:
```python
import psycopg2
conn = psycopg2.connect(
    host=os.environ.get('DB_HOST'),
    database=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD')
)
```

### Step 5: Test Migration

```bash
# Run full test suite against PostgreSQL
pytest --cov=.

# Verify data integrity
python -c "
import psycopg2
conn = psycopg2.connect('...')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
print(f'Users: {cursor.fetchone()[0]}')
cursor.execute('SELECT COUNT(*) FROM login_attempts')
print(f'Login attempts: {cursor.fetchone()[0]}')
"
```

### Step 6: Gradual Rollout

```
Day 1:  DRY RUN - Full test in staging
Day 2:  SHADOW - Postgres receives writes, read from SQLite
Day 3:  DUAL WRITE - Write to both, read from PostgreSQL
Day 4:  READ-ONLY - SQLite becomes read-only backup
Day 5:  CUTOVER - Full migration, deprecate SQLite
Week 2: VERIFY - Monitor 7 days for anomalies
Week 3: RETIRE - Remove SQLite backup
```

### Step 7: Connection Pooling (Production)

```python
from psycopg2.pool import SimpleConnectionPool

pool = SimpleConnectionPool(1, 20,
    host='db.example.com',
    database='accessguard',
    user='accessguard',
    password=os.environ.get('DB_PASSWORD')
)

def get_connection():
    return pool.getconn()

def return_connection(conn):
    pool.putconn(conn)
```

---

## SHA-256 to Bcrypt Migration (v2.0)

### Why Migrate?

- SHA-256: 0.0000001 seconds per hash (too fast)
- Bcrypt: ~0.1 seconds per hash (password-specific)
- Impact: Bcrypt makes brute-force 1M times slower

### Migration Strategy: Lazy Update

```python
import hashlib
import bcrypt

def verify_password(input_password: str, stored_hash: str) -> str:
    """
    Returns:
    - 'valid_new': Valid, already upgraded
    - 'valid_upgrade': Valid, needs upgrade
    - 'invalid': Invalid password
    """
    # Try new bcrypt format
    if stored_hash.startswith('$2b$'):
        if bcrypt.checkpw(input_password.encode(), stored_hash.encode()):
            return 'valid_new'
        return 'invalid'
    
    # Try old SHA-256 format
    if hashlib.sha256(input_password.encode()).hexdigest() == stored_hash:
        return 'valid_upgrade'
    
    return 'invalid'

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = get_user(email)
    result = verify_password(password, user['password_hash'])
    
    if result == 'invalid':
        return error_response("Invalid credentials")
    
    # Upgrade hash if still using SHA-256
    if result == 'valid_upgrade':
        new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        db.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))
        db.commit()
    
    # Create session...
```

### Migration Timeline

```
v1.0: Old SHA-256 format
v1.5: Support both formats (lazy migration)
v2.0: Require bcrypt
v2.1: Drop SHA-256 support
```

---

## Feature Flag Rollout

### A/B Testing New Features

```python
def is_feature_enabled(feature_name: str, user_email: str) -> bool:
    features = {
        'email_verification': {
            'enabled': True,
            'threshold': 0.25,  # 25% of users
        },
        'mfa': {
            'enabled': False,
            'threshold': 0.0,
        }
    }
    
    if not features[feature_name]['enabled']:
        return False
    
    # Hash user email to get consistent 0-1 value
    user_hash = int(hashlib.md5(user_email.encode()).hexdigest(), 16)
    return (user_hash % 100) < (features[feature_name]['threshold'] * 100)

@app.post("/register")
def register(request: Request, email: str = Form(...), ...):
    if is_feature_enabled('email_verification', email):
        send_verification_email(email)
    else:
        create_user_immediately(email)
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
