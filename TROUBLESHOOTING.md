# TROUBLESHOOTING.md - Common Issues & Solutions

## Installation Issues

### Python Not Found
```
Error: 'python' is not recognized as an internal or external command
```
**Solution**:
- Verify Python is installed: `python --version`
- Add Python to PATH (Windows: Settings → Environment Variables)
- Use `python3` instead of `python` on Linux/macOS

### Virtual Environment Issues
```
Error: No module named venv
```
**Solution**:
```bash
# Linux/macOS
python3 -m venv .venv

# Windows
python -m venv .venv
```

### Pipe Not Installed
```
Error: No module named 'pip'
```
**Solution**:
```bash
python -m ensurepip --upgrade
pip install --upgrade pip
```

### Permission Denied
```
Error: PermissionError: [Errno 13] Permission denied
```
**Solution**:
```bash
# Linux/macOS
sudo pip install -r requirements.txt

# Or better: use venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Startup Issues

### Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**:
```bash
pip install -r requirements.txt
```

### Port Already in Use
```
ERROR: Address already in use
```
**Solution**:
1. Find process: `lsof -i :8000` (Linux/macOS)
2. Kill process: `kill -9 <PID>`
3. Or change port in main.py: `port=8001`

### Database Lock
```
sqlite3.OperationalError: database is locked
```
**Solution**:
- Close other connections to database
- Restart server
- Check for long-running queries

---

## Login Issues

### Invalid Credentials (Correct Password)
**Cause**: Account locked or password hash mismatch

**Solution**:
1. Check if account is locked (login as admin, check /dashboard)
2. Verify password is exactly correct (avoid copy-paste from email)
3. Delete account and re-register if issues persist

### Account Locked After 3 Attempts
**Expected behavior**: This is the brute-force protection working

**Solution**:
1. Contact admin for unlock
2. Admin goes to /dashboard → Locked Accounts
3. Click "Unlock" button next to your email
4. Try login again

### Session Expires Too Quickly
**Cause**: Session max_age set to 1 hour

**Solution**:
1. Edit main.py: Change `max_age=3600` to desired seconds
2. Restart server
3. Login again

---

## Database Issues

### Database File Missing
```
FileNotFoundError: [Errno 2] No such file or directory: 'users.db'
```
**Solution**: 
- Database auto-creates on startup
- Ensure write permissions in project directory
- Run: `python main.py` to create

### Cannot Insert User (Duplicate Email)
```
sqlite3.IntegrityError: UNIQUE constraint failed: users.email
```
**Solution**:
- Email already registered
- Use different email
- Or delete existing user from database:
  ```bash
  sqlite3 users.db "DELETE FROM users WHERE email = 'old@example.com';"
  ```

### Database Corruption
```
sqlite3.DatabaseError: database disk image is malformed
```
**Solution**:
1. Back up database: `cp users.db users.db.bak`
2. Delete corrupted database: `rm users.db`
3. Restart server (will recreate clean database)

---

## UI/Display Issues

### CSS Not Loading (White Page)
**Cause**: Static files not served

**Solution**:
1. Verify `static/` directory exists
2. Clear browser cache (Ctrl+Shift+Delete)
3. Hard refresh (Ctrl+Shift+R)
4. Check server logs for errors

### Aurora Background Not Showing
**Cause**: CSS not loading or browser doesn't support effects

**Solution**:
1. Clear cache and refresh
2. Update browser to latest version
3. Check devTools (F12) → Network for CSS errors

### Forms Not Submitting
**Cause**: JavaScript required (should work without)

**Solution**:
1. Hard refresh page
2. Check server logs for errors
3. Verify form field names match endpoint parameters

---

## Permission Issues

### Cannot Write to Database
```
PermissionError: [Errno 13] Permission denied: 'users.db'
```
**Solution**:
```bash
# Linux/macOS
chmod 644 users.db
chmod 755 .

# Windows (Run as Administrator)
```

### Cannot Access /dashboard (Not Admin)
**Cause**: User role is 'user' instead of 'admin'

**Solution**:
1. Create new account with role='admin'
2. Or modify database:
   ```bash
   sqlite3 users.db "UPDATE users SET role='admin' WHERE email='user@example.com';"
   ```

---

## Performance Issues

### Slow Dashboard Load
**Cause**: Large audit log table

**Solution**:
1. Add database indexes:
   ```sql
   CREATE INDEX idx_login_email ON login_attempts(email);
   CREATE INDEX idx_login_timestamp ON login_attempts(timestamp);
   ```

2. Archive old logs:
   ```sql
   DELETE FROM login_attempts WHERE datetime(timestamp) < datetime('now', '-90 days');
   ```

### High CPU Usage
**Cause**: Inefficient query or high traffic

**Solution**:
1. Check server logs
2. Monitor database with: `sqlite3 users.db ".tables"`
3. Migrate to PostgreSQL for production

---

## Security Issues

### Potential SQL Injection Risk
**Concern**: Using f-strings with user input

**Solution**: 
- Verify all queries use parameterized form: `WHERE email = ?`
- Never concatenate user input directly into SQL
- Use `conn.execute(query_template, (param,))`

### Password Visible in Source Code
**Concern**: Test passwords in documentation

**Solution**:
- Never use real credentials in examples
- Use dummy passwords (TestPassword123)
- Production: Use environment variables for secrets

---

## Browser Issues

### Logout Not Working
**Cause**: Session not cleared

**Solution**:
1. Clear cookies manually:
   - F12 → Application → Cookies → Delete all
2. Close browser completely
3. Reopen and login

### Cached Old Version
**Cause**: Old styles or templates cached

**Solution**:
1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. Clear cache: Ctrl+Shift+Delete
3. Incognito mode for testing

---

## Git/Version Control Issues

### Commit Failed with Unknown Author
```
fatal: empty ident <> not allowed
```
**Solution**:
```bash
git config user.email "you@example.com"
git config user.name "Your Name"
git commit -m "message"
```

---

## Getting Help

If issue persists:
1. Check [FAQ.md](FAQ.md) for similar questions
2. Review [SECURITY.md](SECURITY.md) if security-related
3. Check server logs for error details
4. Try test cases in [TESTING.md](TESTING.md)
5. Return to [SETUP.md](SETUP.md) for clean reinstall

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
