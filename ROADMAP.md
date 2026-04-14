# ROADMAP.md - Future Development Plan

## Version 1.0 - Current Release ✅
**Released**: April 14, 2026

### Features
- ✅ User registration and login
- ✅ Password hashing (SHA-256)
- ✅ Brute-force protection (3-strike lockout)
- ✅ Login audit logging
- ✅ Role-based access control (admin/user)
- ✅ SQL injection prevention
- ✅ Admin dashboard with monitoring
- ✅ Glassmorphism UI
- ✅ Comprehensive documentation

---

## Version 1.1 - Q2 2026🚀

### Features
- [ ] Email verification on registration
- [ ] "Remember Me" checkbox for lasting sessions
- [ ] User profile page (view/edit email, name)
- [ ] Better error messages with inline validation
- [ ] Dark mode toggle CSS
- [ ] Export audit logs to CSV
- [ ] Rate limiting (IP-based)

### Backend Changes
```python
# Add to users table
ALTER TABLE users ADD COLUMN full_name TEXT;
ALTER TABLE users ADD COLUMN verified BOOLEAN DEFAULT 0;

# Add email verification table
CREATE TABLE email_verifications (
    id INTEGER PRIMARY KEY,
    email TEXT,
    token TEXT,
    expires_at TEXT
);
```

### API Changes
```
POST /verify-email/{token}  → Verify email with token
GET  /profile              → View user profile
PUT  /profile              → Update profile
POST /resend-verification  → Resend verification email
```

---

## Version 1.2 - Q3 2026

### Features
- [ ] Password reset functionality
- [ ] Security questions as additional auth
- [ ] Admin user management (create/delete users)
- [ ] Session timeout warnings
- [ ] Device management (see active sessions)
- [ ] Login history per user
- [ ] Suspicious activity alerts

### Database Changes
```sql
CREATE TABLE password_resets (
    id INTEGER PRIMARY KEY,
    email TEXT,
    token TEXT,
    expires_at TEXT
);

CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY,
    user_email TEXT,
    session_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT,
    last_activity TEXT
);
```

---

## Version 2.0 - Q4 2026

### Major Features
- [ ] Multi-Factor Authentication (MFA)
  - SMS-based OTP
  - TOTP (Google Authenticator)
  - Email-based OTP
- [ ] Single Sign-On (SSO)
  - Google OAuth
  - Microsoft OAuth
- [ ] Two-Factor Authentication (2FA)
- [ ] Passwordless login (magic links)
- [ ] API keys for programmatic access
- [ ] Webhook support for events

### MFA Implementation
```python
@app.post("/login/mfa")
def mfa_challenge(request: Request):
    # Send OTP via SMS or email
    # Require verification before session

@app.post("/verify-mfa")
def verify_mfa(request: Request, otp: str):
    # Validate OTP
    # Create session if valid
```

---

## Version 2.1 - Q1 2027

### Features
- [ ] OAuth2 server (allow other apps to use AccessGuard for auth)
- [ ] JWT token-based auth (for APIs)
- [ ] Refresh tokens
- [ ] Scopes and granular permissions
- [ ] Admin API for user management
- [ ] Batch user operations

---

## Version 3.0 - Production Ready - Q2 2027

### Infrastructure
- [ ] Docker containerization
- [ ] Kubernetes deployment config
- [ ] PostgreSQL migration with scripts
- [ ] Redis caching layer
- [ ] Elasticsearch for audit log search
- [ ] Prometheus metrics export
- [ ] Datadog/New Relic integration

### Security
- [ ] Bcrypt/Argon2 password hashing
- [ ] OWASP Top 10 security audit
- [ ] Penetration testing
- [ ] Security headers (HSTS, CSP, etc.)
- [ ] CORS configuration per environment
- [ ] IP whitelisting for admin panel
- [ ] WAF (Web Application Firewall) rules

### Performance
- [ ] Query optimization and indexing
- [ ] Connection pooling
- [ ] CDN for static assets
- [ ] Caching strategy
- [ ] Load testing framework
- [ ] Performance monitoring dashboard

---

## Version 3.1 - Enterprise Features - Q3 2027

### Admin Features
- [ ] Tenant management (multi-tenant)
- [ ] User directory integration (LDAP/Active Directory)
- [ ] Compliance reports (GDPR, SOC 2)
- [ ] Audit log retention policies
- [ ] Risk scoring and alerts
- [ ] Anomaly detection

### User Features
- [ ] Profile customization
- [ ] Preference management
- [ ] API documentation portal
- [ ] Activity dashboard (individual)
- [ ] Data export (GDPR)
- [ ] Account deletion

---

## Breaking Changes Planned

### v1.0 → v1.1
- None expected

### v1.1 → v2.0
- Session table schema change (new columns)
- Users table change (profile fields)
- API response format changes (backward compatible endpoints)

### v2.0 → v3.0
- Database migration from SQLite to PostgreSQL
- Password hashing algorithm change (important: all users must rehash on next login)
- API versioning (/api/v1/ vs /api/v2/)

---

## Development Workflow

### Feature Branches
```bash
git checkout -b feature/email-verification
# develop feature
git push origin feature/email-verification
# Create PR, merge after review
```

### Release Process
1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Tag release: `git tag v1.1.0`
4. Build Docker image
5. Deploy to staging
6. Run smoke tests
7. Deploy to production

---

## Community Contributions

We welcome contributions in these areas:
- [ ] Database optimization
- [ ] UI/UX improvements
- [ ] Documentation translations
- [ ] Additional authentication methods
- [ ] Platform-specific guides (Docker, K8s, etc.)
- [ ] Security research and disclosure

See CONTRIBUTING.md for guidelines.

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
