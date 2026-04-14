# FAQ.md - Frequently Asked Questions

## General Questions

### Q: What is AccessGuard?
**A**: AccessGuard is a secure authentication and login monitoring system that demonstrates five critical cybersecurity principles: password hashing, brute-force protection, audit logging, role-based access control, and SQL injection prevention.

### Q: Why FastAPI?
**A**: FastAPI is modern, fast, and includes automatic API documentation. It also integrates seamlessly with Jinja2 for templating and Python's native security libraries.

### Q: Can I use this in production?
**A**: The core architecture is sound, but upgrades needed for production: switch from SQLite to PostgreSQL, replace SHA-256 with bcrypt/Argon2, add rate limiting, implement HTTPS, and enable monitoring.

## Security Questions

### Q: Why SHA-256 and not bcrypt?
**A**: SHA-256 is used for educational clarity. SHA-256is fast (bad for passwords). For production, bcrypt or Argon2 is mandatory.

### Q: Is my password safe?
**A**: Your password is hashed using SHA-256 and never stored or transmitted as plaintext. However, production systems should use bcrypt with salt and multiple rounds.

### Q: What if someone gains database access?
**A**: They get hashed passwords only. Without the plaintext, passwords remain protected. Upgrade to bcrypt to further increase cracking time.

### Q: How does account locking work?
**A**: After 3 failed login attempts, an account is locked in the database. Only admins can unlock it. Lock state persists across sessions and browser restarts.

### Q: Is this system vulnerable to SQL injection?
**A**: No. All database queries use parameterized statements (? placeholders), which prevents SQL injection regardless of user input.

## Technical Questions

### Q: What database is used?
**A**: SQLite for simplicity. Each field is a separate column, fully normalized.

### Q: How is session management handled?
**A**: Session-based with secure cookies. Session secret key recommended to be set via environment variable for production.

### Q: Are emails required to be unique?
**A**: Yes, email is the primary key and must be unique.

### Q: What happens if I forget my password?
**A**: Contact admin for unlock. Future versions should include password reset.

### Q: Can I export audit logs?
**A**: Currently via SQLite CLI. Future versions will include CSV/PDF export.

## Installation Questions

### Q: Python version requirement?
**A**: Python 3.13+ required.

### Q: Do I need a virtual environment?
**A**: Strongly recommended. Prevents package conflicts and is industry standard.

### Q: How do I know if installation succeeded?
**A**: Run `python -c "import main; print('OK')"`. If it prints OK, you're good.

### Q: Port already in use?
**A**: Edit main.py line for uvicorn.run() and change port from 8000 to another (e.g., 8001).

### Q: ModuleNotFoundError?
**A**: Run `pip install -r requirements.txt` and ensure virtual environment is activated.

## Usage Questions

### Q: How do I register?
**A**: Go to /register, enter email, password (8+ chars), and role (admin or user).

### Q: How do I unlock my account?
**A**: Contact system admin. They access /dashboard and click "Unlock" button.

### Q: Can I change my password?
**A**: Not in v1.0. Future versions will add password reset.

### Q: What's the difference between admin and user roles?
**A**: Admin: Full dashboard access + unlock accounts. User: Welcome page only.

### Q: How long does session last?
**A**: 1 hour of inactivity. Then logout and login again.

## Performance Questions

### Q: Will this scale to 1000+ users?
**A**: SQLite will struggle. Migrate to PostgreSQL for production-grade performance.

### Q: Database query time?
**A**: < 5ms for typical queries. Indexes recommended for large audit logs.

### Q: How many login attempts can it handle?
**A**: Single-threaded, ~100 concurrent users. Use Gunicorn + Nginx for load balancing in production.

## Troubleshooting

### Q: Server crashes on startup?
**A**: Check error messages. Usually missing dependencies or wrong Python version.

### Q: Login fails with correct password?
**A**: Check if account is locked. Verify password length (8+ chars). Check database exists.

### Q: Dashboard shows no data?
**A**: No login attempts yet. Perform a login first to generate audit log entries.

### Q: CSS not loading?
**A**: Clear browser cache (Ctrl+Shift+Delete). Verify static/ directory exists.

### Q: "Port already in use"?
**A**: Another process using port 8000. Stop it or change port in main.py.

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
