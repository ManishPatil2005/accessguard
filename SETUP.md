# SETUP.md - Installation & Execution Guide

## 📋 Prerequisites

Before you begin, ensure you have:

| Requirement | Version | Check Command |
|------------|---------|----------------|
| Python | 3.13+ | `python --version` |
| pip | Latest | `pip --version` |
| Git | Any | `git --version` |
| Terminal/CMD | Any | N/A |

**Download Python**: https://www.python.org/downloads/

---

## 🚀 Installation Steps

### Step 1: Clone or Download Repository

#### Option A: Clone from GitHub
```bash
git clone https://github.com/your-username/AccessGuard.git
cd AccessGuard
```

#### Option B: Download ZIP
1. Visit GitHub repository
2. Click "Code" → "Download ZIP"
3. Extract to desired location
4. Open terminal in extracted folder

### Step 2: Create Virtual Environment (Recommended)

#### On Windows
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

#### On Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Why Virtual Environment?**
- Isolates project dependencies
- Prevents conflicts with system packages
- Easy to clean up (delete .venv folder)
- Industry standard practice

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed?**
```
✓ fastapi (web framework)
✓ uvicorn (application server)
✓ jinja2 (template engine)
✓ python-multipart (form handling)
✓ itsdangerous (secure sessions)
```

**Verify installation**:
```bash
pip list
# Should show all packages above
```

### Step 4: Verify Backend Module

```bash
python -c "import main; print('✓ Backend validated')"
```

**Expected output**:
```
Backend Import: OK
```

If you see errors, check:
1. All dependencies installed: `pip install -r requirements.txt`
2. Python version 3.13+: `python --version`
3. Virtual environment activated (Windows: `.venv\Scripts\activate`)

---

## ▶️ Running the Application

### Start the Server

```bash
python main.py
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
```

### Access the Application

Open your browser and navigate to:
- **Home**: http://127.0.0.1:8000/
- **Register**: http://127.0.0.1:8000/register
- **Login**: http://127.0.0.1:8000/login
- **API Docs**: http://127.0.0.1:8000/docs (Swagger)

### Stop the Server

Press **CTRL+C** in the terminal

---

## 🧪 Quick Test After Installation

### Test 1: Create a Regular User
```
1. Go to http://127.0.0.1:8000/register
2. Email: user@example.com
3. Password: TestPassword123
4. Role: user
5. Click "Register Securely"
✓ Should see success message
```

### Test 2: Login as User
```
1. Go to http://127.0.0.1:8000/login
2. Email: user@example.com
3. Password: TestPassword123
4. Click "Sign In"
✓ Should redirect to /welcome
✓ Should show "Welcome, user@example.com"
```

### Test 3: Create an Admin User
```
1. Go to http://127.0.0.1:8000/register
2. Email: admin@example.com
3. Password: AdminPassword123
4. Role: admin
5. Click "Register Securely"
✓ Should see success message
```

### Test 4: Login as Admin
```
1. Go to http://127.0.0.1:8000/login
2. Email: admin@example.com  
3. Password: AdminPassword123
4. Click "Sign In"
✓ Should redirect to /dashboard
✓ Should show login audit log and locked accounts
```

### Test 5: Brute-Force Protection
```
1. Go to http://127.0.0.1:8000/login
2. Email: user@example.com
3. Password: WrongPassword (intentionally wrong)
4. Click "Sign In" 3 times
✓ First 2 attempts: "Invalid credentials" message
✓ 3rd attempt: "Account locked after 3 failed attempts"
✓ account locked: Cannot login anymore
```

### Test 6: Admin Unlock
```
1. Login as admin@example.com
2. Go to /dashboard
3. Find "user@example.com" in "Locked Accounts" section
4. Click "Unlock" button
✓ Should see "Account unlocked successfully" message
✓ Return to dashboard
## After unlock:
1. Logout
2. Login again as user@example.com with correct password
✓ Should work now (account unlocked)
```

---

## 🗄️ Database

### Auto-Creation
The database (`users.db`) is automatically created on first run.

**Location**: `./users.db` (in project root)

### Manual Database Inspection (SQLite)

#### Install SQLite (if not already installed)
```bash
# Windows
# Already included, use sqlite3 command

# Linux
sudo apt-get install sqlite3

# macOS
brew install sqlite3
```

#### Browse Database
```bash
# Open database shell
sqlite3 users.db

# List tables
.tables
# Output: login_attempts  users

# View users table
SELECT * FROM users;
# Shows: email | password_hash | role | failed_attempts | is_locked | created_at

# View login attempts
SELECT * FROM login_attempts;
# Shows: id | email | timestamp | success | is_locked

# Exit shell
.exit
```

#### Reset Database (Start Fresh)
```bash
# Delete the database file
rm users.db  # Linux/macOS
del users.db  # Windows

# Restart the application: python main.py
# New database will be created
```

---

## ⚙️ Environment Configuration (Optional)

### Create .env File
```bash
# Create file named .env in project root
ACCESSGUARD_SESSION_SECRET=your-secret-key-change-this
ACCESSGUARD_DB_PATH=./users.db
ACCESSGUARD_DEBUG=False
```

### Run with Custom Settings
```bash
export ACCESSGUARD_SESSION_SECRET="production-secret"
python main.py
```

### For Production
```bash
# .env (never commit this)
ACCESSGUARD_SESSION_SECRET=xyz-very-long-random-secret-key-xyz
ACCESSGUARD_DEBUG=False
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "python: command not found"

**Solution**: Use `python3` instead
```bash
python3 --version
python3 main.py
```

Or add Python to PATH (Windows):
1. Settings → Environment Variables
2. Add Python installation directory to PATH
3. Restart terminal

### Issue: "Port 8000 already in use"

**Solution**: Use different port
```bash
# Change this line in main.py:
# uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
# To:
# uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)

# Then access: http://127.0.0.1:8001
```

### Issue: Virtual environment not activating

**Windows**:
```bash
# PowerShell (if .venv/Scripts/activate doesn't work)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1

# Command Prompt
.venv\Scripts\activate.bat
```

**Linux/macOS**:
```bash
source .venv/bin/activate
```

### Issue: "Unexpected token" errors in PowerShell

**Solution**: Use semicolons instead of &&
```bash
# Windows PowerShell
cd project; python main.py  # NOT: && python main.py
```

---

## 📊 Project Structure After Installation

```
AccessGuard/
│
├── main.py                          # ← Run this file
├── requirements.txt                 # Dependencies
│
├── templates/                       # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── welcome.html
│   └── dashboard.html
│
├── static/                          # CSS
│   └── style.css
│
├── users.db                         # ← Auto-created on first run
│
├── .venv/                           # Virtual environment
│   ├── Scripts/                     # (Windows)
│   ├── bin/                         # (Linux/macOS)
│   └── lib/                         # Installed packages
│
├── README.md                        # Main documentation
├── ARCHITECTURE.md                  # System design
├── SECURITY.md                      # Security details
├── SETUP.md                         # ← This file
├── TESTING.md                       # Test procedures
│
└── .git/                            # Git repository (after git init)
```

---

## 🔄 Development Workflow

### During Development
```bash
# Terminal 1: Run the server (auto-reloads on code changes)
python main.py

# Terminal 2: Make code changes
# Edit main.py, templates, or style.css
# Server auto-reloads (reload=True in main.py)

# Test in browser
http://127.0.0.1:8000/
```

### Reload Not Working?
If changes don't reflect:
1. Check server terminal for errors
2. Manually stop (CTRL+C) and restart
3. Clear browser cache (CTRL+SHIFT+DELETE)
4. Hard refresh (CTRL+SHIFT+R)

---

## 🎯 Deployment Checklist

Before deploying to production:

- [ ] Test all 5 cybersecurity features
- [ ] Set unique `ACCESSGUARD_SESSION_SECRET`
- [ ] Set `DEBUG=False`
- [ ] Use HTTPS only
- [ ] Add rate limiting
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Enable security headers
- [ ] Implement logging to external service
- [ ] Run security audit (OWASP Top 10)
- [ ] Get SSL certificate
- [ ] Test on target server

---

## 📚 Additional Resources

### FastAPI Documentation
https://fastapi.tiangolo.com/

### SQLite Documentation  
https://www.sqlite.org/docs.html

### Jinja2 Template Guide
https://jinja.palletsprojects.com/

### Python hashlib Reference
https://docs.python.org/3/library/hashlib.html

### OWASP Security Guidelines
https://owasp.org/

---

## ✅ What You Should See

### After Starting Server
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
```

### At http://127.0.0.1:8000/
```
[AccessGuard Logo]
Protect access. Monitor risk. Respond fast.

[Create Account] [Sign In]
```

### Database Created
```bash
# After first run, should exist:
ls -la users.db  # Linux/macOS
dir users.db     # Windows

# If using SQLite shell:
sqlite3 users.db ".tables"
# Output: login_attempts  users
```

---

## 🎓 Educational Tips

### For Internship Evaluation
1. **Run the full test suite** (see TESTING.md)
2. **Show all 5 security features working**
3. **Explain architecture** (see ARCHITECTURE.md)
4. **Discuss security choices** (see SECURITY.md)
5. **Demonstrate GitHub commits** (50+ commits recommended)

### For Interview
- "I built AccessGuard to demonstrate secure authentication"
- "It implements 5 cybersecurity principles: password hashing, brute-force protection, audit logging, RBAC, and SQL injection prevention"
- "I used FastAPI for the backend, SQLite for persistence, and Jinja2 for the frontend"
- "The system is production-ready with proper error handling and security best practices"

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
