# TESTING.md - Comprehensive Test Suite & Validation

## 🧪 Overview

This document provides complete testing procedures for AccessGuard's **5 cybersecurity principles**.

**Total Test Cases**: 20+  
**Time to Complete**: ~30 minutes  
**Prerequisites**: System running, admin user created  

---

## ✅ Pre-Test Checklist

Before running tests:

- [ ] Server running: `http://127.0.0.1:8000`
- [ ] Database fresh or data cleared
- [ ] No users logged in
- [ ] Browser cache cleared
- [ ] Test admin account created
- [ ] Test user accounts available

---

## 🏠 Module 1: Password Hashing

### TC-1.1: Password Not Stored in Plaintext

**Objective**: Verify passwords are hashed, not stored as-is

**Steps**:
1. Register user with email: `hash@test.com`, password: `PlainTestPass123`
2. Open terminal, inspect database:
   ```bash
   sqlite3 users.db "SELECT email, password_hash FROM users WHERE email = 'hash@test.com';"
   ```

**Expected Result**:
```
hash@test.com|6f2b90d440dd821281d5b7ff876098695d98f2923f...
^Email      ^Hash (NOT plaintext)
```

❌ **FAIL**: If you see `PlainTestPass123` in database  
✅ **PASS**: If you see 64-char hex string

**Security Relevance**: Prevents attackers from reading passwords if database is stolen

---

### TC-1.2: Same Password Produces Same Hash

**Objective**: Verify SHA-256 is deterministic

**Steps**:
1. Open Python REPL:
   ```python
   import hashlib
   password = "TestPassword123"
   hash1 = hashlib.sha256(password.encode()).hexdigest()
   hash2 = hashlib.sha256(password.encode()).hexdigest()
   print(hash1 == hash2)  # Should be True
   ```

**Expected Result**:
```
True
```

✅ **PASS**: Hashes match  
❌ **FAIL**: Hashes differ (encryption, not hashing)

---

### TC-1.3: Different Passwords Produce Different Hashes

**Objective**: Verify hash uniqueness

**Steps**:
1. In Python:
   ```python
   import hashlib
   pass1 = hashlib.sha256("Password1".encode()).hexdigest()
   pass2 = hashlib.sha256("Password2".encode()).hexdigest()
   print(pass1 == pass2)  # Should be False
   ```

**Expected Result**:
```
False
```

✅ **PASS**: Different hashes  
❌ **FAIL**: Same hash

---

### TC-1.4: Password Validation on Login

**Objective**: Verify correct password unlocks, incorrect password rejects

**Steps**:
1. Register: `login@test.com`, password: `CorrectPassword123`
2. Login with correct password → ✓ Success (redirect to /welcome or /dashboard)
3. Logout
4. Login with wrong password: `WrongPassword` → ✗ Error: "Invalid credentials"

**Expected Result**:
- Correct password: HTTP 303 redirect to user page
- Wrong password: HTTP 401 Unauthorized + error message

✅ **PASS**: Both attempts work as expected  
❌ **FAIL**: Wrong password logs in, or correct password rejects

---

## 🔐 Module 2: Brute-Force Protection

### TC-2.1: Account Lockout After 3 Failed Attempts

**Objective**: Verify lockout mechanism triggers automatically

**Precondition**: Create user `brutef@test.com` with password `BruteForceTest123`

**Steps**:
1. Go to /login
2. Enter email: `brutef@test.com`
3. Enter password: `wrong` 
4. Click "Sign In" → Error: "Invalid credentials" (failed_attempts = 1)
5. Repeat steps 3-4 again → Error: "Invalid credentials" (failed_attempts = 2)
6. Repeat steps 3-4 once more → Error: "Account locked after 3 failed attempts" (is_locked = 1)
7. Try to login with **correct** password → HTTP 423: "Account is locked"

**Database Verification**:
```bash
sqlite3 users.db "SELECT email, failed_attempts, is_locked FROM users WHERE email = 'brutef@test.com';"
# Expected: brutef@test.com|3|1
```

**Expected Result**:
- After 3 failures: Account locked
- Correct password doesn't work: Still locked (not silently logged in)
- Database shows: `failed_attempts=3, is_locked=1`

✅ **PASS**: Account locked automatically, persists  
❌ **FAIL**: Account not locked or incorrect password works

**Security Relevance**: Prevents automated password-guessing attacks

---

### TC-2.2: Lock State Persists Across Sessions

**Objective**: Verify locked state survives browser restart

**Steps**:
1. Account `brutef@test.com` is already locked from TC-2.1
2. Close browser completely (Ctrl+W on all tabs)
3. Open new browser window
4. Go to http://127.0.0.1:8000/login
5. Attempt login with any password → Should still be locked

**Expected Result**:
```
Error: "Account is locked. Contact an admin."
HTTP 423
```

✅ **PASS**: Lock persists (database-backed)  
❌ **FAIL**: Lock cleared after browser restart (session-only)

---

### TC-2.3: Failed Attempt Counter Resets on Successful Login

**Objective**: Verify counter doesn't "remember" old failures

**Precondition**: Create user `counter@test.com`, password `ResetCounter123`

**Steps**:
1. Login with wrong password twice (failed_attempts = 2)
2. Database check:
   ```bash
   sqlite3 users.db "SELECT failed_attempts FROM users WHERE email = 'counter@test.com';"
   # Shows: 2
   ```
3. Login with **correct** password → Success
4. Database check:
   ```bash
   sqlite3 users.db "SELECT failed_attempts FROM users WHERE email = 'counter@test.com';"
   # Should show: 0 (RESET)
   ```

**Expected Result**:
- After successful login: failed_attempts = 0
- No "memory" of failed attempts

✅ **PASS**: Counter resets to 0  
❌ **FAIL**: Counter remains at 2

**Security Relevance**: Prevents permanent lockout from occasional typos

---

### TC-2.4: Admin Can Unlock Accounts

**Objective**: Verify admin unlock functionality

**Precondition**: Account `locked@test.com` is in locked state

**Steps**:
1. Login as admin@example.com
2. Go to /dashboard
3. Find `locked@test.com` in "Locked Accounts" section
4. Click "Unlock" button
5. Should see: "Account unlocked successfully"
6. Database check:
   ```bash
   sqlite3 users.db "SELECT is_locked, failed_attempts FROM users WHERE email = 'locked@test.com';"
   # Expected: 0|0 (unlocked, attempts reset)
   ```
7. Logout and login as `locked@test.com` with correct password → Success

**Expected Result**:
- Unlock button works
- Database updated: is_locked=0, failed_attempts=0
- User can login immediately

✅ **PASS**: Admin unlock works end-to-end  
❌ **FAIL**: Unlock doesn't work or page shows error

---

## 📊 Module 3: Login Monitoring & Audit Logs

### TC-3.1: Successful Login Logged

**Objective**: Verify successful login creates audit record

**Steps**:
1. Go to /login
2. Login successfully with `user@example.com`
3. Logout
4. Login as admin, go to /dashboard
5. Scroll to "Login Audit Log"
6. Find most recent entry with email: `user@example.com`

**Expected Result**:
```
Email: user@example.com
Status: ✓ Success (green badge)
Is_Locked: Normal view
```

**Database Check**:
```bash
sqlite3 users.db "SELECT * FROM login_attempts WHERE email = 'user@example.com' AND success = 1 ORDER BY id DESC LIMIT 1;"
# Expected: success=1, is_locked=0
```

✅ **PASS**: Entry exists with success=1  
❌ **FAIL**: No entry or success=0

---

### TC-3.2: Failed Login Logged

**Objective**: Verify failed login creates audit record

**Steps**:
1. Go to /login
2. Attempt login with wrong password for `user@example.com`
3. Login as admin, go to /dashboard
4. Find entry for `user@example.com` with status "Failure"

**Expected Result**:
```
Email: user@example.com
Status: ✗ Failure (red badge)
Row highlighted in red
```

**Database Check**:
```bash
sqlite3 users.db "SELECT * FROM login_attempts WHERE email = 'user@example.com' AND success = 0 ORDER BY id DESC LIMIT 1;"
# Expected: success=0
```

✅ **PASS**: Failed attempt logged  
❌ **FAIL**: Not logged or incorrect success value

---

### TC-3.3: Timestamp Recorded in UTC

**Objective**: Verify timestamps are in UTC format

**Steps**:
1. Create a login attempt (success or failure)
2. Check dashboard or database
3. Verify timestamp format

**Expected Result**:
```
Format: "YYYY-MM-DD HH:MM:SS UTC"
Example: "2026-04-14 15:32:45 UTC"
```

✅ **PASS**: UTC timestamp format correct  
❌ **FAIL**: Local time or wrong format

---

### TC-3.4: Locked Account Attempts Show Lock Status

**Objective**: Verify audit log shows lock state

**Precondition**: Account locked (from TC-2.1)

**Steps**:
1. Try to login on locked account
2. Login as admin, check /dashboard
3. Find attempt entries for locked account
4. Check "Lock State" column

**Expected Result**:
```
Recent attempts show: "Locked" badge (orange)
All entries with is_locked=1 in database
```

✅ **PASS**: Lock state visible in logs  
❌ **FAIL**: Lock state not shown or incorrect

---

### TC-3.5: Dashboard Shows All Attempts (Historical)

**Objective**: Verify audit log is comprehensive

**Steps**:
1. Perform 5+ login attempts (mix of success/failure)
2. Login as admin
3. Go to /dashboard → "Login Audit Log"
4. Scroll to see all entries
5. Count total rows

**Expected Result**:
- All attempts visible
- Ordered by most recent first
- Each row has: email, timestamp, status, lock state

✅ **PASS**: All attempts visible and ordered  
❌ **FAIL**: Missing entries or wrong order

---

## 👥 Module 4: Role-Based Access Control (RBAC)

### TC-4.1: User Cannot Access Admin Dashboard

**Objective**: Verify users are restricted from /dashboard

**Steps**:
1. Login as regular user
2. Try to manually navigate to `/dashboard` (type in address bar)
3. Observe result

**Expected Result**:
```
HTTP 403 Forbidden
Error message: "Admin access required"
Redirect to /login or error page
```

✅ **PASS**: User blocked from dashboard  
❌ **FAIL**: User can see dashboard or data

**Security Relevance**: Prevents privilege escalation

---

### TC-4.2: Admin Can Access Dashboard

**Objective**: Verify admins have dashboard access

**Steps**:
1. Logout
2. Login as admin user (role=admin)
3. Should be redirected to /dashboard automatically
4. Alternatively, navigate to `/dashboard` directly
5. Should see dashboard contents

**Expected Result**:
```
HTTP 200 OK
Dashboard displayed with:
  - Locked accounts section
  - Login audit log
  - Unlock buttons
```

✅ **PASS**: Admin can access dashboard  
❌ **FAIL**: Admin blocked or sees error

---

### TC-4.3: User Redirected to Welcome, Admin to Dashboard

**Objective**: Verify post-login redirect based on role

**Steps**:
1. Logout
2. Login as user@example.com (role=user)
3. Check redirect destination

**Expected Result**:
```
Redirected to: /welcome
Shows: "Welcome, user@example.com"
```

**Then**:
1. Logout
2. Login as admin@example.com (role=admin)
3. Check redirect destination

**Expected Result**:
```
Redirected to: /dashboard
Shows: Locked accounts & audit log
```

✅ **PASS**: Different redirects per role  
❌ **FAIL**: Same destination for both roles

---

### TC-4.4: Role Enforcement in Database

**Objective**: Verify role field persists correctly

**Steps**:
```bash
sqlite3 users.db "SELECT email, role FROM users;"
```

**Expected Result**:
```
user@example.com|user
admin@example.com|admin
...
```

✅ **PASS**: Roles stored correctly  
❌ **FAIL**: Wrong roles or missing field

---

### TC-4.5: Non-Authenticated User Access

**Objective**: Verify unauthenticated users can't access protected pages

**Steps**:
1. Ensure not logged in (logout if needed)
2. Try to access /welcome directly → Should redirect
3. Try to access /dashboard directly → Should redirect

**Expected Result**:
```
HTTP 401 Unauthorized or 303 redirect to /login
```

✅ **PASS**: Protected pages require login  
❌ **FAIL**: Can access without authentication

---

## 🛡️ Module 5: SQL Injection Prevention

### TC-5.1: SQL Injection on Email Field (Login)

**Objective**: Verify injection attacks don't work

**Steps**:
1. Go to /login
2. Email field: Enter `" OR 1=1 --`
3. Password: Enter anything
4. Click "Sign In"

**Expected Result**:
```
Error: "Invalid credentials"
No unauthorized access
Database not modified
```

**NOT** (should NOT happen):
```
Login successful (SQL executed)
All users returned
Database compromised
```

✅ **PASS**: Injection blocked  
❌ **FAIL**: Injection works, user logged in

---

### TC-5.2: SQL Injection - Union Attack

**Objective**: Test UNION-based SQL injection

**Steps**:
1. Go to /login
2. Email: `' UNION SELECT * FROM users --`
3. Password: Anything
4. Click "Sign In"

**Expected Result**:
```
Error: "Invalid credentials"
No data extracted
```

✅ **PASS**: UNION attack blocked  
❌ **FAIL**: Unexpected response or data leakage

---

### TC-5.3: SQL Injection - Drop Table (Destructive)

**Objective**: Verify destructive SQL is prevented

**Steps**:
1. Go to /register
2. Email: `'; DROP TABLE users; --`
3. Password: Test123
4. Role: user
5. Click "Register Securely"

**Expected Result**:
```
Registration fails or user created with literal email
Database tables still exist
No harm done
```

**Verify**:
```bash
sqlite3 users.db ".tables"
# Should show: login_attempts  users (NOT empty)
```

✅ **PASS**: DROP prevented, tables intact  
❌ **FAIL**: Tables deleted or missing

---

### TC-5.4: Parameterized Queries Used

**Objective**: Code review - verify parameterized queries throughout

**Steps**:
1. Open `main.py`
2. Search for all `conn.execute()` calls
3. Verify pattern: `?` placeholders, not f-strings

**Expected Result**:
All queries like:
```python
conn.execute("SELECT * FROM users WHERE email = ?", (email,))
```

NOT like:
```python
conn.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

✅ **PASS**: All queries parameterized  
❌ **FAIL**: Any f-string SQL found

---

### TC-5.5: Special Characters Handled

**Objective**: Verify legitimate special chars work

**Steps**:
1. Register with email: `user+test@example.com`
2. Password: `Pass!@#$%^&*123`
3. Register successfully
4. Login with same credentials → Should succeed

**Expected Result**:
```
Registration: Success
Login: Success
Database stores literal values, no SQL interpretation
```

✅ **PASS**: Special chars handled as data  
❌ **FAIL**: Registration fails or login doesn't work

---

## 📊 Integration Tests

### TC-6.1: Full Registration → Login → Dashboard Flow

**Objective**: End-to-end user workflow

**Steps**:
1. Register new user: `flow@test.com`, password: `FlowTest123`, role: `user`
2. See success message
3. Go to login
4. Login with new credentials
5. Redirected to /welcome
6. Click logout
7. Login again → Should work

**Expected Result**:
- Each step succeeds without errors
- Data persists (can login multiple times)

✅ **PASS**: Complete flow works  
❌ **FAIL**: Any step fails

---

### TC-6.2: Admin Complete Workflow

**Objective**: Admin registration, login, unlock operations

**Steps**:
1. Register admin: `newadmin@test.com`, password: `AdminTest123`, role: `admin`
2. Login as new admin
3. Redirect to /dashboard
4. See "Locked Accounts" and "Audit Log"
5. If any locked accounts, click unlock
6. See success message
7. Logout

**Expected Result**:
- Admin can perform all operations
- Dashboard loads correctly
- Unlock button functions

✅ **PASS**: Admin workflow complete  
❌ **FAIL**: Any operation fails

---

## 🔧 Performance Tests

### TC-7.1: Dashboard Load Time

**Objective**: Verify dashboard responds quickly

**Steps**:
1. Login as admin
2. Open /dashboard
3. Measure load time (browser DevTools: F12 → Network)

**Expected Result**:
```
Load time: < 500ms
No timeouts or hangs
```

✅ **PASS**: Fast response  
❌ **FAIL**: Slow or timeout

---

### TC-7.2: Database Query Performance

**Objective**: Verify large audit log doesn't slow system

**Steps**:
1. Create 100+ login attempts (run script)
2. Load /dashboard
3. Measure page load

**Expected Result**:
```
Page still responsive
No noticeable lag
All rows display
```

✅ **PASS**: Scales reasonably  
❌ **FAIL**: Slow with large data

---

## 🎯 Security Test Cases Summary

| Module | Test Count | Status |
|--------|-----------|--------|
| Password Hashing | 4 | ⬜ Pending |
| Brute-Force | 4 | ⬜ Pending |
| Audit Logging | 5 | ⬜ Pending |
| RBAC | 5 | ⬜ Pending |
| SQL Injection | 5 | ⬜ Pending  |
| Integration | 2 | ⬜ Pending |
| Performance | 2 | ⬜ Pending |
| **TOTAL** | **27** | ⬜ Pending |

---

## 📝 Test Execution Checklist

Use this checklist to track test progress:

### Module 1: Password Hashing
- [ ] TC-1.1: Not plaintext in DB
- [ ] TC-1.2: Deterministic hashing
- [ ] TC-1.3: Different hashes for different passwords
- [ ] TC-1.4: Password validation

### Module 2: Brute-Force
- [ ] TC-2.1: 3-strike lockout
- [ ] TC-2.2: Lock persists
- [ ] TC-2.3: Counter resets
- [ ] TC-2.4: Admin unlock

### Module 3: Audit Logging
- [ ] TC-3.1: Success logged
- [ ] TC-3.2: Failure logged
- [ ] TC-3.3: UTC timestamp
- [ ] TC-3.4: Lock status shown
- [ ] TC-3.5: All attempts visible

### Module 4: RBAC
- [ ] TC-4.1: User can't access dashboard
- [ ] TC-4.2: Admin can access dashboard
- [ ] TC-4.3: Different redirects per role
- [ ] TC-4.4: Role in database
- [ ] TC-4.5: Unauthenticated blocked

### Module 5: SQL Injection
- [ ] TC-5.1: OR 1=1 blocked
- [ ] TC-5.2: UNION blocked
- [ ] TC-5.3: DROP blocked
- [ ] TC-5.4: Parameterized queries
- [ ] TC-5.5: Special chars handled

### Integration & Performance
- [ ] TC-6.1: User complete flow
- [ ] TC-6.2: Admin complete flow
- [ ] TC-7.1: Dashboard load time
- [ ] TC-7.2: Database scaling

---

## 🎓 Test Results Template

```markdown
# AccessGuard Test Results
Date: [DATE]
Tester: [NAME]

## Summary
- **Total Tests**: 27
- **Passed**: [ ]/27
- **Failed**: [ ]/27
- **Skipped**: [ ]/27

## Results by Module
- Password Hashing: [ ] PASS / [ ] FAIL
- Brute-Force: [ ] PASS / [ ] FAIL
- Audit Logging: [ ] PASS / [ ] FAIL
- RBAC: [ ] PASS / [ ] FAIL
- SQL Injection: [ ] PASS / [ ] FAIL

## Issues Found
1. [Description]
2. [Description]

## Recommendations
- [Recommendation]
- [Recommendation]

## Overall Assessment
[ ] Production Ready
[ ] Ready with Caveats
[ ] Not Ready
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
