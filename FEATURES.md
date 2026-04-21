# AccessGuard – Feature Documentation

## 🔐 Authentication Features

### User Registration
- **Email Validation**: Ensures valid email format
- **Password Requirements**: Minimum 8 characters
- **Role Selection**: Assign user or admin role at registration
- **Hash Storage**: SHA-256 password hashing (no plain text)
- **Duplicate Prevention**: Email uniqueness constraint

**Flow**:
```
User Input → Validation → Hash Password → Store in DB → Success Message
```

### User Login
- **Credential Verification**: Validates email and password hash
- **Session Creation**: Secure session management using Starlette middleware
- **Role-Based Redirect**: 
  - Admin → `/dashboard`
  - User → `/welcome`
- **Failed Attempt Tracking**: Increments counter on each failure

**Flow**:
```
Email/Password Input → Hash Comparison → Account Lock Check → Session Creation → Redirect
```

---

## 🛡️ Security Features

### Brute-Force Protection
- **3-Strike Lockout**: Account locks after 3 failed login attempts
- **Persistent Lock**: Requires admin intervention to unlock
- **Attempt Counter**: Resets on successful login
- **Lock Status Tracking**: Database field tracks locked state

**Scenario**:
```
Failed Attempt 1 → Counter: 1
Failed Attempt 2 → Counter: 2
Failed Attempt 3 → Counter: 3, Account Locked
Admin Unlock → Reset to 0, is_locked = false
```

### SQL Injection Prevention
- **Parameterized Queries**: All database queries use `?` placeholders
- **No String Formatting**: Never uses f-strings or `.format()` for queries
- **Type Safety**: Prevents malicious SQL injection

**Example**:
```python
# ✓ SAFE - Parameterized
conn.execute("SELECT * FROM users WHERE email = ?", (email,))

# ✗ DANGEROUS - Never used
conn.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### Password Security
- **SHA-256 Hashing**: Industry-standard cryptographic hash
- **No Salt** (Current implementation): Future enhancement opportunity
- **Hash Comparison**: Uses secure hash matching
- **Plain Text Never Stored**: Only hashes stored in database

**Enhancement Opportunity**:
```python
# Future: Add salt for stronger security
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash(password)
```

---

## 👥 Role-Based Access Control (RBAC)

### Admin Role
**Permissions**:
- View all locked accounts
- View complete login audit trail
- Unlock user accounts
- Access to `/dashboard` endpoint

**Features**:
- Locked accounts list with unlock buttons
- Audit log showing all login attempts
- Timestamp tracking for all activities

### User Role
**Permissions**:
- View personal welcome page
- Access to `/welcome` endpoint
- See own account status
- View personal login attempts

**Restrictions**:
- Cannot access `/dashboard`
- Cannot unlock accounts
- Read-only access to own information

---

## 📊 Audit Logging

### Login Attempt Tracking
Each login attempt logs:
- **Email**: User email address
- **Timestamp**: UTC timestamp of attempt
- **Success Status**: Boolean (true/false)
- **Lock Status**: Was account locked at time of attempt

**Stored In**: `login_attempts` table

### Database Schema
```sql
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    success INTEGER NOT NULL,  -- 1 = success, 0 = failure
    is_locked INTEGER NOT NULL -- 1 = locked, 0 = unlocked
)
```

### Use Cases
- **Security Investigation**: Track suspicious login patterns
- **Compliance**: Audit trail for regulatory requirements
- **User Support**: Help admins understand account issues
- **Analytics**: Identify common attack times

---

## 🎨 User Interface Features

### Glassmorphism Design
- **Frosted Glass Effect**: Semi-transparent cards with blur
- **Aurora Animation**: Dynamic background effects
- **Responsive Layout**: Works on desktop, tablet, mobile
- **Accessibility**: Clear typography and contrast

### Pages

#### Home (`/`)
- Welcome message
- Quick links to register/login
- Project description

#### Registration (`/register`)
- Email input field
- Password input field
- Role selection dropdown
- Submit button
- Success/error messages

#### Login (`/login`)
- Email input field
- Password input field
- Submit button
- Error messages for:
  - Invalid credentials
  - Locked accounts
  - System errors

#### User Welcome (`/welcome`)
- Personalized greeting with email
- Account status:
  - Account created date
  - Failed login attempts
  - Lock status

#### Admin Dashboard (`/dashboard`)
- **Locked Accounts Section**:
  - Table of locked accounts
  - Unlock button for each
  - Email and lock reason

- **Audit Log Section**:
  - Complete login attempt history
  - Timestamp, email, success/failure status
  - Real-time updates

---

## 🔄 Session Management

### Session Creation
- Created on successful login
- Uses Starlette SessionMiddleware
- Secret key from environment variable: `ACCESSGUARD_SESSION_SECRET`
- Max age: 1 hour (3600 seconds)

### Session Data Stored
```python
session["user_email"] = "user@example.com"
session["role"] = "admin"  # or "user"
```

### Session Validation
- Checked on protected endpoints
- Automatic redirect to login if invalid
- HTTP 401 response if missing

---

## 🔗 API Response Codes

| Code | Scenario |
|------|----------|
| **200** | GET request successful |
| **201** | Registration successful |
| **303** | Redirect (POST to GET) |
| **400** | Validation error (password too short, invalid role) |
| **401** | Invalid credentials or not authenticated |
| **403** | Insufficient permissions (user accessing admin endpoint) |
| **404** | Resource not found (email not in system) |
| **409** | Email already registered |
| **423** | Account locked |
| **500** | Server error |

---

## 📈 Future Enhancement Opportunities

1. **Email Verification**
   - Send verification email on registration
   - Confirm email before account activation

2. **Two-Factor Authentication (2FA)**
   - TOTP/SMS verification on login
   - Enhanced security for sensitive accounts

3. **Password Reset Flow**
   - Forgot password link
   - Email-based password reset
   - Reset token validation

4. **Enhanced Audit Logging**
   - IP address tracking
   - User agent logging
   - Geographic location (optional)

5. **Admin Tools**
   - Bulk user management
   - Password reset capability
   - Account deletion
   - Role assignment management

6. **Security Enhancements**
   - Bcrypt/Argon2 password hashing instead of SHA-256
   - Salt with passwords
   - Rate limiting on login attempts
   - CSRF token protection
   - HTTPS enforcement

7. **UI/UX Improvements**
   - Dark/light mode toggle
   - Account settings page
   - Profile picture support
   - Password change functionality
   - Export audit logs (CSV/PDF)

8. **Deployment Features**
   - Database backup automation
   - Health check endpoints
   - Metrics/monitoring
   - Logging to external service
   - CDN integration for static files
