# HARDENING.md - Security Hardening Checklist

## Pre-Production Security Audit

### Authentication & Passwords
- [x] Passwords hashed (SHA-256)
- [ ] **UPGRADE**: Use bcrypt/Argon2 with salt
- [ ] Password minimum length enforced (8+ chars)
- [ ] Password complexity requirements
- [ ] No password reuse allowed
- [ ] Password expiration policy

### Account Management
- [x] Brute-force lockout (3 strikes)
- [ ] Account unlock time limit (auto-unlock after 30 min)
- [ ] Email verification required
- [ ] Account deactivation workflow
- [ ] User account audit trail

### Session Security
- [x] Secure session cookies (HTTPOnly, Secure flags)
- [x] Session timeout (1 hour)
- [ ] Implement CSRF tokens
- [ ] Session fixation prevention
- [ ] Logout clears all sessions

### API Security
- [ ] CORS configured (restrict to trusted domains)
- [ ] Rate limiting on login endpoint (max 10 requests/minute)
- [ ] API versioning
- [ ] Request size limits
- [ ] Timeout on long-running requests

### Data Protection
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] Encrypt data at rest
- [ ] Encrypt data in transit (TLS 1.2+)
- [ ] Secure database connection
- [ ] Database encryption enabled

### Error Handling
- [x] No sensitive data in error messages
- [x] Proper HTTP status codes
- [ ] Custom error pages (hide stack traces)
- [ ] Error logging (secure location)
- [ ] Debug mode disabled in production

### Input Validation
- [x] All inputs parameterized (SQL injection prevention)
- [ ] Input length limits
- [ ] Email format validation
- [ ] Whitelist allowed characters
- [ ] XSS prevention (sanitize HTML output)

### Logging & Monitoring
- [x] Login attempts logged
- [x] Failed auth logged
- [x] Unlock operations logged
- [ ] Admin actions logged
- [ ] Access logs retained (90+ days)
- [ ] Log file encryption

### Infrastructure
- [ ] Web server hardening (Nginx/Apache)
- [ ] Firewall rules configured
- [ ] WAF (Web Application Firewall) enabled
- [ ] DDoS protection
- [ ] Intrusion detection system

### Access Control
- [x] RBAC implemented (admin/user)
- [ ] Principle of least privilege
- [ ] Admin approval for sensitive operations
- [ ] Session-based authorization
- [ ] Multi-factor authentication (MFA)

### Compliance
- [ ] Privacy policy updated
- [ ] Data retention policy documented
- [ ] GDPR compliance (if EU users)
- [ ] SOC 2 guidelines followed
- [ ] Regular security audits scheduled

## Post-Deployment Monitoring

### Daily Tasks
- [ ] Check error logs
- [ ] Review failed login attempts
- [ ] Monitor locked accounts
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Review audit logs
- [ ] Check system performance
- [ ] Verify all services running
- [ ] Test backup restoration

### Monthly Tasks
- [ ] Security audit
- [ ] Dependency updates
- [ ] Performance analysis
- [ ] Capacity planning

### Quarterly Tasks
- [ ] Penetration testing
- [ ] Security training
- [ ] Policy review
- [ ] Disaster recovery drill

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
