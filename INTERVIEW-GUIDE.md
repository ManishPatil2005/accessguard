# INTERVIEW-GUIDE.md - Interview Preparation

## Tell Me About AccessGuard (2-3 minutes)

**Answer Structure**:

"AccessGuard is a secure authentication and login monitoring system I built to demonstrate five critical cybersecurity principles in a real-world application.

The system has a FastAPI backend that handles user registration, login, and admin functions. It uses SQLite for data persistence and Jinja2 for server-side HTML templating with a glassmorphism UI design.

The five security principles demonstrated are:

1. **Password Hashing**: I use SHA-256 via Python's hashlib to hash passwords before storing them. When a user logs in, I hash their input and compare it to the stored hash. This ensures passwords are never stored in plaintext.

2. **Brute-Force Protection**: After 3 failed login attempts, the system automatically locks the account in the database. This persists across sessions, so attackers can't keep guessing. Only admins can unlock accounts.

3. **Login Audit Logging**: Every login attempt is recorded with email, timestamp, success/failure status, and lock state. Admins can view this in the dashboard to detect attack patterns.

4. **Role-Based Access Control**: Users have 'admin' or 'user' roles. The system enforces role checks on every protected endpoint, preventing privilege escalation.

5. **SQL Injection Prevention**: All database queries use parameterized statements with ? placeholders. User input is never concatenated directly into SQL, preventing injection attacks regardless of input.

The project includes comprehensive documentation covering architecture, security implementation, testing procedures, and deployment guidelines. It's designed to be portfolio-ready and production-quality."

---

## Five Security Principles (Detailed Answers)

### Principle 1: Password Hashing
**Question**: "How do you hash passwords?"

**Answer**:
- I use Python's `hashlib.sha256()`
- Password is encoded to UTF-8 bytes
- The hash is stored (64-character hex string)
- Original password is never stored or recoverable
- On login, I hash the input and compare to stored hash

**Code**:
```python
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
```

**Production Note**: Production systems should use bcrypt or Argon2 with salt.

---

### Principle 2: Brute-Force Protection
**Question**: "How do you prevent brute-force attacks?"

**Answer**:
- Account locks after 3 failed login attempts
- The lock state ('is_locked' field) is persisted in the database
- Locked accounts cannot login, even with the correct password
- Admins can manually unlock via the /unlock endpoint
- The lock persists across sessions and browser restarts

**Implementation**:
```python
if hash_password(password) != user["password_hash"]:
    failed_attempts += 1
    if failed_attempts >= 3:
        set is_locked = 1 in database
```

**Why This Works**: Attackers cannot bypass the lockout by restarting.

---

### Principle 3: Audit Logging
**Question**: "Tell me about your logging strategy."

**Answer**:
- Every login attempt is recorded in `login_attempts` table
- Logs include: email, timestamp (UTC), success (1/0), is_locked (1/0)
- Successful and failed attempts are both logged
- Lockout events are logged with is_locked=1
- Admins have a dashboard to view all attempts

**Database Schema**:
```sql
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY,
    email TEXT,
    timestamp TEXT (UTC),
    success INTEGER (0/1),
    is_locked INTEGER (0/1)
)
```

**Dashboard Shows**:
- All attempts in reverse chronological order
- Color-coded: green for success, red for failure
- Locked accounts clearly highlighted

---

### Principle 4: Role-Based Access Control
**Question**: "How do you enforce different access levels?"

**Answer**:
- Two roles: 'admin' and 'user'
- Role is stored in users table and copied to session
- Every protected endpoint checks the session role
- Non-admin users get HTTP 403 Forbidden to /dashboard
- Admin users are redirected to /dashboard on login
- User role gets /welcome page only

**Implementation**:
```python
def require_admin(request: Request):
    role = request.session.get("role")
    if role != "admin":
        raise HTTPException(status_code=403)
```

**Principle of Least Privilege**: Users only get the minimum access they need.

---

### Principle 5: SQL Injection Prevention
**Question**: "How do you prevent SQL injection?"

**Answer**:
- I never concatenate user input into SQL strings
- All queries use parameterized statements with ? placeholders
- User data is passed separately in a tuple
- SQL and data are processed separately by SQLite

**Safe Code**:
```python
conn.execute(
    "SELECT * FROM users WHERE email = ?",  # SQL structure
    (email,)  # Data (separate)
)
```

**Unsafe Code (NEVER)**:
```python
query = f"SELECT * FROM users WHERE email = '{email}'"  # DON'T DO THIS
```

**Why This Works**: User input cannot be interpreted as SQL code because data is processed after SQL parsing.

---

## Architecture Question

**Question**: "Draw the system architecture or explain the data flow."

**Answer**:
```
External User → /register or /login → FastAPI Backend
                                         ↓
                               Validate Input
                               Hash Password
                               Query Database
                               Check Brute-Force
                               Manage Session
                                        ↓
                                    SQLite DB
                                  (users table)
                               (login_attempts table)
                                        ↓
                               Render Jinja2 Template
                                        ↓
                        Return HTML to Browser
```

**Key Points**:
- Request validation
- Database interaction (parameterized)
- Session management
- Template rendering
- Audit logging on each attempt

---

## Why This Project?

**Question**: "Why did you build this?"

**Answer**:
"I wanted to understand real-world security practices beyond just knowing the concepts. Building AccessGuard forced me to think about:
- How passwords are actually protected
- Why brute-force attacks are dangerous
- How to design systems that leave audit trails
- How to enforce access controls consistently
- **The full security pipeline** from registration to admin functions

The project demonstrates these principles in a complete system, not in isolation."

---

## Deployment Question

**Question**: "Is this ready for production?"

**Answer**:
"The architecture and security principles are sound and production-ready. However, some parts need upgrades:

1. **Database**: Migrate from SQLite to PostgreSQL
2. **Hashing**: Upgrade from SHA-256 to bcrypt or Argon2
3. **Infrastructure**: Add HTTPS, reverse proxy (Nginx), rate limiting
4. **Monitoring**: Integrate logging service and alerting

The application code is clean and well-documented, so these upgrades are straightforward."

---

## Questions to Ask Back

Be prepared to ask the interviewer:

1. "What are your current security challenges?"
2. "How do you handle authentication at scale?"
3. "What's your rate limiting strategy?"
4. "Do you have a security incident response plan?"
5. "How often do you do penetration testing?"

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
