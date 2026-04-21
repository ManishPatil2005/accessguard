# Troubleshooting Guide

## Installation Issues

### "Python not found" Error
**Problem**: Running `python` or `python3` returns "not found"

**Solutions**:
1. **Reinstall Python**:
   - Visit https://www.python.org/downloads/
   - Download Python 3.13+
   - **Important**: Check "Add Python to PATH" during installation
   - Restart terminal/CMD after installation

2. **Check Installation**:
   ```bash
   python --version
   # Should show: Python 3.13.x or higher
   ```

3. **Use `python3` on Linux/Mac**:
   ```bash
   python3 --version
   python3 -m venv .venv
   ```

---

### "pip: command not found"
**Problem**: `pip install` doesn't work

**Solutions**:
1. **Reinstall pip**:
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Verify pip is installed**:
   ```bash
   python -m pip --version
   ```

3. **Use module syntax** (always works):
   ```bash
   # Instead of: pip install fastapi
   # Use: python -m pip install fastapi
   ```

---

### Virtual Environment Not Activating

**Problem**: `.venv\Scripts\activate` doesn't work

**Solutions**:

For **Windows PowerShell**:
```powershell
# PowerShell requires execution policy change
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

For **Windows CMD**:
```cmd
.\.venv\Scripts\activate.bat
```

For **Linux/Mac**:
```bash
source .venv/bin/activate
```

**Verify activation**:
```bash
# Should show (.venv) at start of terminal prompt
which python  # Linux/Mac
where python  # Windows
# Should point to .venv directory
```

---

### ImportError: No module named 'fastapi'

**Problem**: Running code fails with import error

**Solutions**:
1. **Ensure virtual environment is activated**:
   ```bash
   # Windows
   .\.venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **Reinstall dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   pip list
   # Should show: fastapi, uvicorn, jinja2, etc.
   ```

---

## Runtime Issues

### Port Already in Use

**Problem**: "Address already in use" when starting server

**Error Message**:
```
ERROR:     [Errno 98] Address already in use
```

**Solutions**:

1. **Use different port**:
   ```bash
   python main.py --port 8001
   # Access at http://localhost:8001
   ```

2. **Kill existing process** (Windows):
   ```powershell
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

3. **Kill existing process** (Linux/Mac):
   ```bash
   lsof -i :8000
   kill -9 <PID>
   ```

---

### Database Error: "database is locked"

**Problem**: SQLite error when accessing database

**Causes**:
- Multiple FastAPI instances running
- Database file corrupted
- Permission issues

**Solutions**:
1. **Kill all Python processes**:
   - Windows: `taskkill /IM python.exe /F`
   - Linux/Mac: `killall python`

2. **Delete and recreate database**:
   ```bash
   rm users.db  # or del users.db on Windows
   python main.py
   # Database will be recreated on startup
   ```

3. **Check file permissions**:
   ```bash
   # Linux/Mac
   chmod 644 users.db
   ```

---

### Jinja2 Template Error

**Problem**: "TemplateNotFound" error

**Error Message**:
```
jinja2.exceptions.TemplateNotFound: home.html
```

**Solutions**:
1. **Verify templates directory exists**:
   ```bash
   ls templates/  # Linux/Mac
   dir templates  # Windows
   # Should show: base.html, home.html, login.html, etc.
   ```

2. **Check working directory**:
   ```bash
   # Must run from project root
   # NOT from subdirectory
   cd /path/to/accessguard
   python main.py
   ```

3. **Verify file names**:
   - Exact case-sensitive match required
   - Check for typos in template names

---

## Browser Issues

### Page Won't Load

**Problem**: Browser shows "Cannot reach localhost"

**Solutions**:
1. **Verify server is running**:
   - Terminal should show: "Application startup complete"
   - Check for errors in terminal output

2. **Check correct URL**:
   - http://localhost:8000 ✓
   - http://127.0.0.1:8000 ✓
   - http://0.0.0.0:8000 ✗ (wrong)

3. **Try different browser**:
   - Chrome, Firefox, Safari all work
   - Clear browser cache: Ctrl+Shift+Delete

---

### CSS Not Loading (Unstyled Page)

**Problem**: Page loads but looks plain, no styling

**Solutions**:
1. **Check static files are mounted**:
   - Open browser console (F12)
   - Check Network tab for 404 errors
   - Should see: `GET /static/style.css 200 OK`

2. **Verify static directory exists**:
   ```bash
   ls static/  # Linux/Mac
   dir static  # Windows
   # Should contain: style.css
   ```

3. **Clear browser cache**:
   - Ctrl+Shift+Delete (most browsers)
   - Close browser completely
   - Reopen and refresh

---

### JavaScript Error in Console

**Problem**: JavaScript console shows errors

**Note**: This project uses minimal JavaScript. Most errors are CSS-related.

**Solutions**:
1. **Ignore browser warnings** about deprecated APIs
2. **Check browser compatibility**:
   - Works on: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
3. **Report issues** if you find actual bugs

---

## Login/Authentication Issues

### Can't Login with Created Account

**Problem**: Registration succeeded, but login fails

**Steps to diagnose**:
1. **Verify email was typed correctly**:
   - Registration email: user@example.com
   - Login email: user@example.com
   - Must be exact match

2. **Check password**:
   - Passwords are case-sensitive
   - Password must be at least 8 characters

3. **Verify account created**:
   - Check database (optional):
     ```bash
     sqlite3 users.db "SELECT email FROM users;"
     ```

---

### "Account is Locked" After 3 Attempts

**Problem**: Account locked after failed login attempts

**This is intentional security feature**

**Solution**:
1. **Register as admin**:
   - Create admin account: admin@example.com
   - Login with admin role

2. **Unlock account from dashboard**:
   - Navigate to `/dashboard`
   - Find locked user email
   - Click "Unlock" button

3. **Try login again**:
   - User account now accessible

---

### Session Lost When Refreshing

**Problem**: Logged in, but refresh loses login

**This might indicate**:
- Session secret key issue
- Browser cookies disabled

**Solutions**:
1. **Enable cookies in browser**:
   - Chrome: Settings → Privacy → Cookies
   - Firefox: Preferences → Privacy

2. **Check environment variable** (production):
   - `ACCESSGUARD_SESSION_SECRET` must be set
   - Development uses default value

---

## Database Issues

### Corrupted Database

**Problem**: Database file exists but has errors

**Solutions**:
1. **Backup and delete**:
   ```bash
   mv users.db users.db.backup  # Linux/Mac
   ren users.db users.db.backup  # Windows
   ```

2. **Restart application**:
   ```bash
   python main.py
   # New database will be created
   ```

3. **Restore from backup** (if needed):
   ```bash
   mv users.db.backup users.db
   ```

---

### Database Modifications

**Problem**: Need to manually edit database

**Solution** (Advanced):
```bash
# Install sqlite3 command-line tool
# Windows: https://www.sqlite.org/download.html
# Linux: apt-get install sqlite3
# Mac: brew install sqlite

# Connect to database
sqlite3 users.db

# View all users
SELECT email, role FROM users;

# Reset failed attempts for a user
UPDATE users SET failed_attempts=0 WHERE email='user@example.com';

# Delete a user
DELETE FROM users WHERE email='user@example.com';
```

---

## Getting Help

### Where to Report Issues
1. **GitHub Issues**: https://github.com/ManishPatil2005/accessguard/issues
2. **Check existing issues** before creating new one
3. **Include**:
   - Python version: `python --version`
   - OS: Windows/Linux/Mac
   - Error message (full text)
   - Steps to reproduce

### Useful Debug Commands
```bash
# Check Python installation
python --version

# Check virtual environment
which python  # Linux/Mac
where python  # Windows

# Check dependencies
pip list

# View error logs (if running with logging)
python main.py --log-level debug
```

---

## Performance Issues

### Application Runs Slowly

**Solutions**:
1. **Reduce concurrent users**:
   - SQLite is single-writer
   - For production, use PostgreSQL/MySQL

2. **Enable caching** (advanced):
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   # Add caching headers to responses
   ```

3. **Monitor resource usage**:
   - Task Manager (Windows) / top (Linux)
   - Check CPU and memory usage

---

## Still Having Issues?

1. **Check documentation**:
   - README.md - Quick start
   - SETUP.md - Installation
   - DEVELOPMENT.md - Development guide
   - API.md - Endpoint reference

2. **Review error message**:
   - Often contains solution
   - Search error message on Google

3. **Enable debug mode**:
   ```python
   # In main.py, change:
   app = FastAPI(title="AccessGuard", debug=True)
   ```

4. **Create GitHub issue**:
   - Include all debug information
   - Be specific about reproduction steps
