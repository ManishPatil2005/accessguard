# AccessGuard – Secure Authentication System

A **Secure Authentication and Login Monitoring System** demonstrating cybersecurity best practices.

## What It Does

✅ **User Registration & Login** – Secure email/password authentication  
✅ **Password Security** – SHA-256 hashing  
✅ **Brute-Force Protection** – Lock account after 3 failed attempts  
✅ **Login Audit Logging** – Every authentication event tracked  
✅ **Role-Based Access Control** – Separate user/admin permissions  
✅ **SQL Injection Prevention** – Parameterized queries only  
✅ **Professional UI** – Glassmorphism design  

Perfect for cybersecurity labs and interview portfolios.

---

## Quick Start (2 minutes)

```bash
# Setup
git clone https://github.com/ManishPatil2005/accessguard.git
cd accessguard
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate      # Linux/Mac
pip install -r requirements.txt

# Run
python main.py
```

Visit **http://localhost:8000**

---

## Try It

### Register
- **Email**: user@example.com
- **Password**: Password123
- **Role**: User

### Login as User
- See personal welcome page

### Register admin
- **Email**: admin@example.com
- **Role**: Admin

### Login as Admin
- View locked accounts
- See login audit trail
- Unlock accounts

### Test Brute-Force
- Login 3 times with wrong password → Account locks
- Admin unlocks from dashboard

---

## How It Works

| Step | What Happens |
|------|--------------|
| **Register** | Email validated, password hashed (SHA-256), stored in database |
| **Login (Success)** | Password hashed, compared with DB, session created |
| **Login (Fail)** | Failed attempt counter incremented, logged with timestamp |
| **3 Failures** | Account locked, requires admin unlock |
| **Admin Login** | Role checked, redirected to admin dashboard |

---

## Key Endpoints

```
GET  /                     Home page
POST /register             Create account
POST /login                Sign in
GET  /welcome              User page (after login)
GET  /dashboard            Admin panel (admin only)
POST /unlock/{email}       Unlock account (admin only)
GET  /logout               Clear session
GET  /docs                 API documentation
```

---

## Security Features

### Authentication & Password
- Email validation on registration
- 8+ character password requirement
- SHA-256 hashing (no plain text storage)
- Proper hash comparison

### Attack Prevention
- 3-strike brute-force lockout
- SQL injection prevention (parameterized queries)
- Session-based authentication
- HTTPOnly cookies

### Access Control
- Role-based permission checking
- Admin-only endpoints (`/dashboard`, `/unlock`)
- User-only endpoints (`/welcome`)
- Proper HTTP status codes (401, 403)

### Monitoring & Audit
- Every login attempt logged
- Timestamp recorded (UTC)
- Success/failure flagged
- Account lock state tracked
- Admin dashboard for review

---

## Database

Two simple tables:

**users**
- email (primary key)
- password_hash
- role (admin/user)
- failed_attempts (0-3)
- is_locked (0/1)

**login_attempts**
- email, timestamp, success (0/1), is_locked (0/1)

---

## Project Files

```
main.py              FastAPI app + all logic
requirements.txt     Python dependencies
users.db            SQLite database (auto-created)

templates/
  ├── base.html     Global layout
  ├── home.html     Landing page
  ├── register.html Registration form
  ├── login.html    Login form
  ├── welcome.html  User page
  └── dashboard.html Admin panel

static/
  └── style.css     Glassmorphism UI
```

---

## Reset Database

```bash
rm users.db
python main.py  # Creates fresh database
```

---

## Tech Stack

- **Language**: Python 3
- **Framework**: FastAPI
- **Database**: SQLite
- **Frontend**: Jinja2 + HTML5 + CSS3
- **Server**: Uvicorn
- **Auth**: SHA-256 + Sessions

---

## Testing Checklist

- [ ] Register user account
- [ ] Register admin account
- [ ] Login as user → redirects to `/welcome`
- [ ] Login as admin → redirects to `/dashboard`
- [ ] Wrong password 3x → Account locked
- [ ] Admin unlocks account
- [ ] Admin sees login audit trail
- [ ] Logout → Session cleared
- [ ] Access `/dashboard` without auth → 401 error
- [ ] Access `/dashboard` as user → 403 error

---

## Security Concepts Demonstrated

1. **Password Security** – Hashing, never plain text
2. **Attack Prevention** – Brute-force lockout
3. **Authorization** – Role-based access control
4. **Auditability** – Login tracking with audit logs
5. **Injection Prevention** – Parameterized queries

---

## Future Enhancements (v2.0)

- Bcrypt password hashing (upgrade)
- Email verification
- Two-factor authentication (2FA)
- PostgreSQL migration
- OAuth2/OIDC support
- Rate limiting

---

**Version**: 1.0.0 | **Status**: ✅ Production Ready
