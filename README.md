# AccessGuard – Secure Authentication System

<div align="center">

[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-purple)](LICENSE)
[![Code style: PEP 8](https://img.shields.io/badge/code%20style-PEP8-orange)](https://pep8.org/)
[![Security: Parameterized SQL](https://img.shields.io/badge/security-parameterized%20SQL-brightgreen)](./SECURITY.md)

**A Production-Ready Secure Authentication and Login Monitoring System**  
*Perfect for cybersecurity labs, portfolio projects, and learning secure coding practices*

[Quick Start](#quick-start) • [Features](#-key-features) • [Documentation](#-documentation) • [Contributing](#contributing) • [Security](#-security)

</div>

---

## 📋 Overview

AccessGuard is a complete, secure authentication system that demonstrates **real-world cybersecurity best practices**. It's built with FastAPI, SQLite, and a modern glassmorphism UI.

### Perfect For:
✅ Learning secure authentication implementation  
✅ Cybersecurity portfolio projects  
✅ Interview preparation and demonstrations  
✅ Understanding OWASP security principles  
✅ Role-based access control (RBAC) study  

---

## 🔐 Key Features

### Authentication
- **Secure Registration**: Email validation, password requirements, hashing
- **Secure Login**: Encrypted password verification, session management  
- **Session Management**: Secure cookie-based sessions (Starlette middleware)
- **User Roles**: Admin and User roles with different permissions

### Security
- **Brute-Force Protection**: 3-strike lockout mechanism
- **SQL Injection Prevention**: 100% parameterized queries
- **Password Hashing**: SHA-256 cryptographic hashing
- **RBAC**: Role-Based Access Control with explicit permission checks

### Monitoring & Audit
- **Login Audit Logging**: Complete timestamp for every authentication attempt
- **Account Status Tracking**: Lock status, failed attempts, creation date
- **Admin Dashboard**: View locked accounts and complete audit trail
- **Real-time Updates**: Immediate reflection of changes

### User Experience
- **Glassmorphism UI**: Modern, responsive design
- **Error Messages**: Clear, helpful feedback
- **Mobile Responsive**: Works on all screen sizes
- **Accessibility**: Semantic HTML, good contrast

---

## 📊 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI 0.104.1 |
| **Server** | Uvicorn (ASGI) |
| **Database** | SQLite 3 |
| **Frontend** | Jinja2 Templates + CSS3 |
| **Styling** | Glassmorphism Design |
| **Session Management** | Starlette SessionMiddleware |
| **Python Version** | 3.13+ |

---

## ⚡ Quick Start (2 minutes)

### 1. Prerequisites
- **Python 3.13+** ([Download](https://www.python.org/downloads/))
- **pip** (usually included with Python)
- **Git** (optional, for cloning)

### 2. Clone & Setup
```bash
# Clone repository
git clone https://github.com/ManishPatil2005/accessguard.git
cd accessguard

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Application
```bash
python main.py
```

### 4. Visit in Browser
```
http://localhost:8000
```

---

## 🎮 Try It Out

### Register New User
1. Go to `/register`
2. **Email**: `user@example.com`
3. **Password**: `MyPassword123` (8+ characters)
4. **Role**: Select "User"
5. Click **Register**

### Login as User
1. Go to `/login`
2. **Email**: `user@example.com`
3. **Password**: `MyPassword123`
4. See personalized **Welcome Page**

### Test Brute-Force Protection
1. Try logging in 3 times with **wrong password**
2. Account becomes **LOCKED** 🔒
3. See error: "Account locked. Contact an admin."

### Login as Admin
1. Register new account with **role: Admin**
2. **Email**: `admin@example.com`
3. **Password**: `AdminPass123`
4. Access **Admin Dashboard** `/dashboard`

### Admin Features
1. **View locked accounts** in dashboard
2. **See login audit log** (all attempts, timestamps)
3. **Unlock accounts** with one click
4. **Monitor security** in real-time

---

## 📡 API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page |
| `GET` | `/register` | Registration form |
| `POST` | `/register` | Create new account |
| `GET` | `/login` | Login form |
| `POST` | `/login` | Authenticate user |
| `GET` | `/logout` | Clear session |

### Protected Endpoints (Authentication Required)
| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/welcome` | User | User home page |
| `GET` | `/dashboard` | Admin | Admin security dashboard |
| `POST` | `/unlock/{email}` | Admin | Unlock user account |

### System Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/docs` | Swagger API documentation |
| `GET` | `/openapi.json` | OpenAPI schema |

**For detailed API documentation**, see [API.md](API.md)

---

## 🏗️ Project Structure

```
accessguard/
├── main.py                    # FastAPI application (all backend logic)
├── requirements.txt           # Python dependencies
├── users.db                   # SQLite database (auto-created)
├── runtime.txt               # Python runtime version
├── Procfile                  # Deployment configuration
│
├── static/
│   └── style.css            # Glassmorphism styling
│
├── templates/               # Jinja2 HTML templates
│   ├── base.html           # Base template (extends into others)
│   ├── home.html           # Landing page
│   ├── register.html       # Registration form
│   ├── login.html          # Login form
│   ├── welcome.html        # User home page
│   └── dashboard.html      # Admin security dashboard
│
└── docs/                    # Documentation files
    ├── README.md           # This file
    ├── API.md             # API endpoint reference
    ├── SETUP.md           # Installation guide
    ├── DEVELOPMENT.md     # Development workflow
    ├── ARCHITECTURE.md    # System design
    ├── FEATURES.md        # Feature documentation
    ├── SECURITY.md        # Security details
    ├── TROUBLESHOOTING.md # Common issues & fixes
    ├── TESTING.md         # Testing guidelines
    ├── CODE_OF_CONDUCT.md # Community guidelines
    └── CONTRIBUTING.md    # Contribution guide
```

---

## 🔒 Security Features

### Authentication & Password
```python
# ✓ Password hashing (SHA-256)
password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

# ✓ Never stored plain text
# ✓ Safe comparison (hash vs hash)
hash_password(input) == stored_hash
```

### SQL Injection Prevention
```python
# ✓ ALWAYS parameterized queries
conn.execute("SELECT * FROM users WHERE email = ?", (email,))

# ✗ NEVER string formatting
# conn.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### Brute-Force Protection
```python
# 3-strike lockout
if failed_attempts >= LOCK_THRESHOLD:
    account_locked = True
    # Requires admin unlock
```

### RBAC (Role-Based Access Control)
```python
# Explicit role checking
if session_role != "admin":
    raise HTTPException(status_code=403)  # Forbidden
```

**See [SECURITY.md](SECURITY.md) for detailed security documentation**

---

## 📚 Documentation

Comprehensive documentation included:

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview (this file) |
| [SETUP.md](SETUP.md) | Installation & execution guide |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Development workflow & standards |
| [API.md](API.md) | Complete API endpoint reference |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design & data flow |
| [FEATURES.md](FEATURES.md) | Detailed feature documentation |
| [SECURITY.md](SECURITY.md) | Security implementation details |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues & solutions |
| [TESTING.md](TESTING.md) | Testing guide & test cases |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [CHANGELOG.md](CHANGELOG.md) | Version history & changes |

---

## 🧪 Testing

### Quick Test
```bash
# Verify setup
python -c "import main; print('✓ Backend OK')"

# Start server
python main.py

# Open browser
http://localhost:8000

# Test in browser:
# 1. Register account
# 2. Login successfully
# 3. Try wrong password 3x (locks account)
# 4. Register as admin
# 5. Unlock from dashboard
```

**For comprehensive testing guide**, see [TESTING.md](TESTING.md)

---

## 🚀 Deployment

### Deploy to Render
1. **Push to GitHub**:
   ```bash
   git push origin main
   ```

2. **Connect to Render**:
   - Visit https://render.com
   - Connect GitHub account
   - Create new Web Service
   - Select this repository

3. **Configure**:
   - **Runtime**: Python 3.13
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `python main.py`

**See [DEPLOYMENT.md](DEPLOYMENT-GUIDE.md) for detailed instructions**

---

## 📈 Database Schema

### users table
```sql
CREATE TABLE users (
    email TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,  -- 'admin' or 'user'
    failed_attempts INTEGER DEFAULT 0,
    is_locked INTEGER DEFAULT 0,  -- 1 = locked
    created_at TEXT NOT NULL
);
```

### login_attempts table
```sql
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    success INTEGER NOT NULL,  -- 1 = success, 0 = failure
    is_locked INTEGER NOT NULL -- 1 = locked account
);
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. **Report bugs**: [Create an issue](https://github.com/ManishPatil2005/accessguard/issues)
2. **Suggest features**: [Describe your idea](https://github.com/ManishPatil2005/accessguard/issues)
3. **Submit code**: See [CONTRIBUTING.md](CONTRIBUTING.md)

**Contribution Process**:
```bash
# 1. Fork repository
# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes & test
python main.py

# 4. Commit with clear messages
git commit -m "feat: add email verification"

# 5. Push and create pull request
git push origin feature/your-feature
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📝 License

AccessGuard is MIT licensed - see [LICENSE](LICENSE) file.

### What You Can Do:
✅ Use commercially  
✅ Modify code  
✅ Distribute  
✅ Use privately  

### Conditions:
📋 Include license  
📋 Describe changes  

---

## 🎓 Learning Outcomes

By studying this project, you'll learn:

- **Authentication**: Secure user login systems
- **Password Security**: Hashing, salting, validation
- **SQL Injection Prevention**: Parameterized queries
- **Session Management**: Secure cookie handling
- **RBAC**: Role-based access control
- **Web Development**: FastAPI, Jinja2, CSS
- **Database Design**: SQLite schema design
- **Security Best Practices**: OWASP principles
- **Code Standards**: PEP 8, clean code
- **DevOps**: Deployment, environment variables

---

## 🐛 Troubleshooting

### Common Issues:
- **"Port already in use"**: Use different port or kill process
- **"Template not found"**: Run from project root directory  
- **"Import error"**: Activate virtual environment & reinstall dependencies

**See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions**

---

## 💡 Future Enhancements

- [ ] Email verification on registration
- [ ] Two-factor authentication (2FA)
- [ ] Password reset functionality
- [ ] Bcrypt/Argon2 password hashing
- [ ] Rate limiting on login
- [ ] CSRF token protection
- [ ] Audit log export (CSV/PDF)
- [ ] Dark/light mode toggle
- [ ] Account settings page
- [ ] Docker containerization

---

## 📞 Support

### Getting Help
1. **Read docs**: Start with SETUP.md or TROUBLESHOOTING.md
2. **Check issues**: Search existing issues on GitHub
3. **Ask community**: Create new issue with details
4. **Report security**: See [SECURITY.md](SECURITY.md) for security issues

---

## 🌟 Star History

If you find this project helpful, please consider:
- ⭐ **Starring** the repository
- 🔗 **Sharing** with others
- 🐛 **Reporting** issues
- 💬 **Contributing** improvements

---

## 👤 Author

**Manish Patil**
- GitHub: [@ManishPatil2005](https://github.com/ManishPatil2005)
- Project: [AccessGuard](https://github.com/ManishPatil2005/accessguard)

---

<div align="center">

**Made with ❤️ for the cybersecurity community**

[⬆ back to top](#accessguard--secure-authentication-system)

</div>
