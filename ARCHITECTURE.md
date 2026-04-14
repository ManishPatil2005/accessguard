# ARCHITECTURE.md - AccessGuard System Design

## 📐 System Overview

AccessGuard follows a **three-tier web application architecture**:

```
┌─────────────────────────────────────────────────────────┐
│             PRESENTATION LAYER                          │
│  (HTML Templates + CSS - Glassmorphism UI)             │
│  - home.html, register.html, login.html                │
│  - welcome.html, dashboard.html                        │
│  - style.css (all styling)                            │
└────────────────────────┬────────────────────────────────┘
                        │ HTTP Requests/Responses
                        ↓
┌─────────────────────────────────────────────────────────┐
│             APPLICATION LAYER                           │
│  (FastAPI + Python Logic - main.py)                    │
│  - Request routing & validation                        │
│  - Authentication & session management                 │
│  - Authorization (RBAC)                                │
│  - Password hashing (SHA-256)                          │
│  - Brute-force protection logic                        │
│  - Audit logging                                       │
└────────────────────────┬────────────────────────────────┘
                        │ SQL Queries (Parameterized)
                        ↓
┌─────────────────────────────────────────────────────────┐
│             DATA LAYER                                  │
│  (SQLite Database - users.db)                          │
│  - users table (credentials, roles, lock status)       │
│  - login_attempts table (audit logs)                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow Diagrams

### Flow 1: User Registration
```
User enters email, password, role
          ↓
POST /register
          ↓
FastAPI validates input
  - Email format check
  - Password length (8+ chars)
  - Role validation (admin/user)
          ↓
Check if email exists in DB
  - YES → HTTP 409 (Conflict)
  - NO → Continue
          ↓
Hash password using SHA-256
          ↓
INSERT into users table
  - Parameterized query
  - Store: email, password_hash, role, created_at
          ↓
HTTP 201 Created + Success Template
```

### Flow 2: User Login Success
```
User enters email, password
          ↓
POST /login
          ↓
FastAPI validates input
          ↓
SELECT user FROM users WHERE email = ?
  - Parameterized: prevents SQL injection
          ↓
User NOT found?
  - YES → Log failed attempt (DB)
  - NO → Continue
          ↓
User is_locked == 1?
  - YES → Log failed attempt (lock state)
         → HTTP 423 Locked
  - NO → Continue
          ↓
Compare hash(input_password) vs stored hash
  - NOT EQUAL → Increment failed_attempts
              → If failed_attempts >= 3:
                  Set is_locked = 1
                  Log failed attempt (locked)
                  HTTP 423 Locked
              → ELSE:
                  Log failed attempt
                  HTTP 401 Unauthorized
              → Return error template
  - EQUAL → Continue (Success)
          ↓
Reset failed_attempts to 0
          ↓
Set session:
  - user_email
  - role (admin or user)
          ↓
Log successful login attempt
          ↓
Redirect:
  - Admin role → /dashboard
  - User role → /welcome
```

### Flow 3: Admin Unlock Account
```
Admin navigate to /dashboard
          ↓
GET /dashboard
          ↓
Verify session role == 'admin'
  - NOT admin → HTTP 403 Forbidden
  - IS admin → Continue
          ↓
SELECT all FROM login_attempts ORDER BY id DESC
SELECT all FROM users WHERE is_locked = 1
          ↓
Render dashboard template with data:
  - All login attempts (paginated)
  - Locked accounts highlighted
  - Unlock buttons for each locked user
          ↓
Admin clicks "Unlock" for user@example.com
          ↓
POST /unlock/user@example.com
          ↓
Verify admin role again
          ↓
SELECT email FROM users WHERE email = ?
  - NOT FOUND → HTTP 404 Not Found
  - FOUND → Continue
          ↓
UPDATE users SET is_locked = 0, failed_attempts = 0
  WHERE email = ?
          ↓
HTTP 303 Redirect → /dashboard?message=unlocked
```

---

## 🗄️ Database Schema Details

### Users Table
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

**Explanation**:
- `email`: Primary key, unique identifier, normalized to lowercase
- `password_hash`: SHA-256 hex digest (never plaintext)
- `role`: Either 'admin' (dashboard access) or 'user' (welcome page only)
- `failed_attempts`: Counter for brute-force tracking (resets on successful login)
- `is_locked`: Boolean (0=active, 1=locked); persists until admin unlocks
- `created_at`: Timestamp of account creation (UTC)

### Login Attempts Table
```sql
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    success INTEGER NOT NULL,
    is_locked INTEGER NOT NULL
);
```

**Explanation**:
- `id`: Auto-incrementing unique row identifier
- `email`: Email of user attempting login
- `timestamp`: UTC timestamp in format "YYYY-MM-DD HH:MM:SS UTC"
- `success`: 1 for successful login, 0 for failed
- `is_locked`: 1 if account was/became locked during attempt, 0 otherwise

**Indexing Strategy**: Add these indexes for production
```sql
CREATE INDEX idx_login_attempts_email ON login_attempts(email);
CREATE INDEX idx_login_attempts_timestamp ON login_attempts(timestamp);
CREATE INDEX idx_users_role ON users(role);
```

---

## 🔒 Security Architecture

### Password Hashing Strategy
```
User Input: "MySecurePassword123"
                ↓
Python hashlib.sha256()
                ↓
Hex Digest: "6f2b90d440dd821281..."  (64 characters)
                ↓
Store in DB (never store plaintext)
                ↓
On Login: hash(input) == stored_hash?
```

**Why SHA-256**:
- Fast deterministic hashing
- No salt (for simplicity in educational context)
- Industry standard
- Built into Python stdlib

**Production Note**: Use bcrypt/Argon2 instead for real systems

### Brute-Force Protection Architecture
```
                Failed Attempt
                      ↓
         ┌────────────┴────────────┐
         ↓                         ↓
   failed_attempts++      failed_attempts < 3?
                             ↓          ↓
                           YES        NO
                          ↓          ↓
                   Allow Retry    Lock Account
                                  is_locked = 1
```

**Lockout Trigger**:
- After 3 consecutive failed login attempts
- Account remains locked until admin unlocks
- Lock state persists across sessions (database)

### SQL Injection Prevention
```
VULNERABLE (Bad):
query = f"SELECT * FROM users WHERE email = '{email}'"
# User input: ' OR 1=1 --
# Becomes: SELECT * FROM users WHERE email = '' OR 1=1 --'

SAFE (Good - AccessGuard):
conn.execute("SELECT * FROM users WHERE email = ?", (email,))
# Parameterized query - SQL and data are separate
# User input is never interpreted as SQL code
```

**Rule**: Every database operation in AccessGuard uses `?` placeholders

### Session Security
```
User Login Success
        ↓
Create Session:
  - request.session["user_email"] = normalized_email
  - request.session["role"] = role
        ↓
Session stored in secure cookie
  - SECRET_KEY protects integrity
  - Max age: 3600 seconds (1 hour)
  - HTTPOnly flag (not accessible to JS)
        ↓
On each request: Validate session exists and hasn't expired
        ↓
Logout: request.session.clear() + redirect to /login
```

### Role-Based Access Control (RBAC)
```
┌─────────────────────────────────────────┐
│         Session Exists?                 │
└────────────┬────────────────────────────┘
             │ NO: HTTP 401 Unauthorized
             │ YES: Continue
             ↓
┌─────────────────────────────────────────┐
│         role == "admin"?                │
└────────────┬────────────────────────────┘
             │ NO: HTTP 403 Forbidden
             │ YES: Return /dashboard
             ↓
         Admin Dashboard
```

---

## 📝 File Structure & Responsibilities

### main.py (FastAPI Core)
```python
"""
Core application module with:
- Database initialization (init_db)
- Helper functions (hash_password, log_login_attempt, etc.)
- Authentication helpers (require_authenticated_user, require_admin)
- Endpoint handlers (GET/POST for each route)
"""

KEY FUNCTIONS:
├── hash_password(password: str) → str
│   └─ SHA-256 hashing
│
├── get_db_connection() → sqlite3.Connection
│   └─ Return DB connection with Row factory
│
├── log_login_attempt(email: str, success: bool, is_locked: bool)
│   └─ Insert audit log entry
│
├── get_user_by_email(email: str) → sqlite3.Row
│   └─ Fetch user record (parameterized)
│
├── require_authenticated_user(request: Request) → tuple
│   └─ Validate session exists (else 401)
│
├── require_admin(request: Request) → tuple
│   └─ Validate role='admin' (else 403)
│
├── init_db() → None
│   └─ Create tables on startup
│
└── ENDPOINT HANDLERS:
    ├── @app.get("/") → home(request)
    ├── @app.get("/register") → register_page(request)
    ├── @app.post("/register") → register(...)
    ├── @app.get("/login") → login_page(request)
    ├── @app.post("/login") → login(...)
    ├── @app.get("/welcome") → welcome(request)
    ├── @app.get("/dashboard") → dashboard(request)
    ├── @app.post("/unlock/{email}") → unlock_account(...)
    └── @app.get("/logout") → logout(request)
```

### templates/ (Jinja2 Templates)
```
base.html
  └─ Header, navigation, footer (inherited)
     - Brand: "AccessGuard"
     - Nav links: Home, Register, Login, Welcome, Dashboard, Logout
     - Aurora background animations

home.html
  └─ Landing page
     - Hero section with project description
     - Call-to-action buttons (Register / Login)

register.html
  └─ Registration form
     - Email input (required)
     - Password input (min 8 chars)
     - Role dropdown (admin/user)
     - Form validation errors
     - Success message after registration

login.html
  └─ Login form
     - Email input
     - Password input
     - Form validation errors
     - Locked account error (423 status)
     - Failed attempt error (401 status)

welcome.html
  └─ Post-login user page
     - Personalized greeting (email)
     - Role display
     - Logout button
     - Redirect admins to dashboard

dashboard.html
  └─ Admin-only security panel
     - Locked accounts section
       ├─ Table: email, failed_attempts
       ├─ Unlock button for each
     - Login audit log section
       ├─ Table: email, timestamp, success, is_locked
       ├─ Color-coded rows (risk / safe)
```

### static/style.css (Glassmorphism UI)
```
DESIGN SYSTEM:
├── Color Palette
│   ├── --bg-0: #07171f (darkest)
│   ├── --bg-1: #0e2531 (dark)
│   ├── --bg-2: #143645 (medium-dark)
│   ├── --ok: #35d084 (green - success)
│   ├── --fail: #ff6b6b (red - error)
│   ├── --warn: #ffb347 (orange - warning)
│   └── --accent: #6ad5ff (cyan - accent)
│
├── Components
│   ├── .glass-card
│   │   └─ backdrop-filter: blur(14px)
│   │   └─ border: 1px solid rgba(255,255,255,0.25)
│   │   └─ background: linear-gradient(170deg, rgba(255,255,255,0.2), ...)
│   │
│   ├── .aurora (animated background)
│   │   └─ Floating orbs with blur & opacity
│   │   └─ Animation: 13s ease-in-out infinite
│   │
│   ├── .btn
│   │   ├── .btn-primary (cyan-green gradient)
│   │   ├── .btn-secondary (transparent with border)
│   │   └── .btn-warning (orange gradient)
│   │
│   ├── .alert
│   │   ├── .alert.success (green tint)
│   │   ├── .alert.error (red tint)
│   │   └── .alert.info (cyan tint)
│   │
│   ├── .badge (inline status)
│   │   ├── .badge.ok (green)
│   │   ├── .badge.fail (red)
│   │   ├── .badge.lock (orange)
│   │   └── .badge.neutral (gray)
│   │
│   └── .table (audit log)
│       └─ .row-risk (red tint)
│       └─ .row-safe (green tint)
│
└── Responsive Design
    └─ Mobile navbar adjusts to column layout
    └─ Card padding scales down
    └─ Table becomes scrollable on small screens
```

---

## 🔀 Data Flow Diagram (DFD Level 1)

### Detailed DFD showing all processes and stores:

```
External Entities:
  ┌─────────────────────┐
  │   End User          │ (Register, Login)
  └────────┬────────────┘
           │
           │ Credentials
           ↓
   ┌───────────────────────────────────────────────┐
   │  1.0 Authentication System (FastAPI)          │
   │  ├─ 1.1 Validate Input                        │
   │  ├─ 1.2 Hash Password                         │
   │  ├─ 1.3 Check Brute-Force                     │
   │  ├─ 1.4 Create/Validate Session               │
   │  └─ 1.5 Log Attempt                           │
   └───────┬──────────────┬────────┬───────────────┘
           │              │        │
           │              │        │ Log Data
           ↓              ↓        ↓
   ┌──────────────┐  ┌────────────────────┐
   │ D1: Users DB │  │ D2: Login Attempts │
   │ (Persistent) │  │ (Audit Logs)       │
   └──────────────┘  └────────────────────┘
        ↑                    ↑
        │                    │
        └────────┬───────────┘
                 │ Query Results
                 ↓
   ┌─────────────────────────────┐
   │  2.0 Rendering (Jinja2)     │
   │  ├─ Bind data to templates  │
   │  └─ Generate HTML           │
   └────────────┬────────────────┘
                │ HTML Output
                ↓
         Browser/Client


External Entities:
  ┌─────────────────────┐
  │   Admin User        │ (Dashboard, Unlock)
  └────────┬────────────┘
           │
           │ View Dashboard / Unlock Request
           ↓
   ┌───────────────────────────────────────────────┐
   │  1.0 Authorization System (FastAPI)           │
   │  ├─ 1.1 Verify Admin Role (RBAC)              │
   │  ├─ 1.2 Grant/Deny Access                     │
   │  ├─ 1.3 Process Unlock                        │
   │  └─ 1.4 Update Lock Status                    │
   └───────┬──────────────────────────────────────┘
           │
           │ Read/Update Requests
           ↓
   ┌──────────────────────────────────┐
   │ D1: Users DB                     │
   │ Read: (email, role, is_locked)   │
   │ Write: (is_locked, failed_...)   │
   └──────────────────────────────────┘
```

---

## 🛡️ Security Controls Mapping

| Principle | Implementation | File(s) | Function |
|-----------|----------------|---------|----------|
| **Password Hashing** | SHA-256 via hashlib | main.py | `hash_password()` |
| **Brute-Force** | 3-strike lockout | main.py | `login()` endpoint |
| **Audit Logging** | Login attempt table | main.py | `log_login_attempt()` |
| **RBAC** | Role check in auth | main.py | `require_admin()` |
| **SQL Injection** | Parameterized queries | main.py | All db operations |

---

## 🚀 Scalability Considerations

### Current Design (Single-Server)
- Suitable for: Internal tools, demos, educational purposes
- Users: Up to ~1000 concurrent
- Limitation: Single SQLite process

### For Production Scaling
1. **Database**: Migrate to PostgreSQL/MySQL
2. **Caching**: Add Redis for session management
3. **Load Balancing**: Nginx/HAProxy with multiple FastAPI workers
4. **Monitoring**: Prometheus + Grafana for metrics
5. **Logging**: Centralized logging (ELK Stack)
6. **Security**: WAF, rate limiting, DDoS protection

---

## ✅ Design Decisions & Rationale

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **SQLite** | Zero setup, file-based, suitable for educational context | Limited concurrency, not for high-load |
| **Jinja2 Templates** | Server-side rendering, simple integration, secure | Less interactive (no JS frameworks allowed) |
| **Pure CSS** (Glassmorphism) | Modern aesthetic, no JS dependency, follows constraints | Manual media queries, no component library |
| **SHA-256** | Simple, deterministic, educational context | Production: Use bcrypt/Argon2 |
| **3-Strike Lockout** | Balance between usability and security | Could be configurable |
| **Session Cookies** | Simple, no external dependencies | Consider JWT for APIs (future) |

---

## 📊 Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| User Registration | O(1) | Single INSERT |
| User Login | O(1) | Single SELECT + hash check |
| Brute-Force Check | O(1) | In-memory comparison |
| Dashboard Load | O(n) | Query all login attempts (n = rows) |
| Unlock Account | O(1) | Single UPDATE |

**Database Optimization**:
```sql
-- Add these indexes for production
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_login_attempts_email ON login_attempts(email);
CREATE INDEX idx_login_attempts_timestamp ON login_attempts(timestamp);
```

---

## 🔧 Configuration & Environment

### Environment Variables (Optional)
```bash
# Session security (override default)
ACCESSGUARD_SESSION_SECRET=your-production-key

# Database location
ACCESSGUARD_DB_PATH=./users.db

# Server
ACCESSGUARD_HOST=127.0.0.1
ACCESSGUARD_PORT=8000
ACCESSGUARD_DEBUG=False
```

### Running with Custom Settings
```bash
export ACCESSGUARD_SESSION_SECRET="production-secret-key"
python main.py
```

---

## 📚 Design Documentation Standards Met

✅ DFD Level-0 (Context Diagram)  
✅ DFD Level-1 (Process Decomposition)  
✅ Data Dictionary (Database Schema)  
✅ Security Architecture  
✅ Request/Response Flows  
✅ Technology Stack  
✅ File Structure & Responsibilities  
✅ Scalability Analysis  

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
