# DATABASE-ADMIN.md - Database Administration Guide

## SQLite Database Management

### File Location
```bash
./users.db  # In project root
```

### Backup Strategy
```bash
# Single backup
sqlite3 users.db ".backup /path/to/backup/users.db.bak"

# Automated daily backup (Linux/macOS)
0 2 * * * sqlite3 /path/to/users.db ".backup /backup/users-$(date +%Y%m%d).db"

# Keep only 30 days
find /backup -name "users-*.db" -mtime +30 -delete
```

### Common Database Operations

#### Connect to Database
```bash
sqlite3 users.db
```

#### View All Users
```sql
SELECT email, role, is_locked, failed_attempts FROM users ORDER BY email;
```

#### View Recent Login Attempts
```sql
SELECT * FROM login_attempts ORDER BY id DESC LIMIT 50;
```

#### Find Locked Accounts
```sql
SELECT email, failed_attempts FROM users WHERE is_locked = 1;
```

#### Unlock Account Manually
```sql
UPDATE users SET is_locked = 0, failed_attempts = 0 WHERE email = 'user@example.com';
```

#### Delete User Account
```sql
DELETE FROM users WHERE email = 'user@example.com';
DELETE FROM login_attempts WHERE email = 'user@example.com';
```

#### Clean Up Old Audit Logs (Keep 90 Days)
```sql
DELETE FROM login_attempts 
WHERE datetime(timestamp) < datetime('now', '-90 days');
```

#### Count Users by Role
```sql
SELECT role, COUNT(*) FROM users GROUP BY role;
```

#### Get Login Statistics
```sql
SELECT email, COUNT(*) as total, 
       SUM(success) as successes,
       SUM(CASE WHEN is_locked THEN 1 ELSE 0 END) as locked_attempts
FROM login_attempts
GROUP BY email
ORDER BY total DESC;
```

### Database Schema

#### Users Table
```
Columns:
  email TEXT PRIMARY KEY
  password_hash TEXT
  role TEXT (admin|user)
  failed_attempts INTEGER (0-3+)
  is_locked INTEGER (0|1)
  created_at TEXT (UTC timestamp)

Indexes (recommended):
  PRIMARY KEY (email)
```

#### Login Attempts Table
```
Columns:
  id INTEGER PRIMARY KEY AUTOINCREMENT
  email TEXT
  timestamp TEXT (UTC)
  success INTEGER (0|1)
  is_locked INTEGER (0|1)

Indexes (recommended):
  INDEX (email)
  INDEX (timestamp)
```

### Performance Optimization

#### Add Indexes
```sql
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_login_email ON login_attempts(email);
CREATE INDEX idx_login_timestamp ON login_attempts(timestamp);
CREATE INDEX idx_login_success ON login_attempts(success);
```

#### View Index Statistics
```sql
.indexes users
.indexes login_attempts
```

#### Defragment Database
```sql
VACUUM;
ANALYZE;
```

### Migration to PostgreSQL

When scaling to production, migrate to PostgreSQL:

```python
# Update main.py
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="accessguard",
        user="postgres",
        password="secure-password",
        host="localhost",
        port=5432
    )
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
