# COMPLIANCE.md - Regulatory & Compliance Guide

## GDPR (General Data Protection Regulation)

### Data Subject Rights Implementation

**Right to Access**
```python
@app.get("/api/my-data")
def get_my_data(request: Request):
    """Return all user data in portable format"""
    email = request.session.get("user_email")
    user = db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    return {
        "user": user,
        "login_attempts": get_login_attempts(email)
    }
```

**Right to Erasure**
```python
@app.post("/api/delete-account")
def delete_account(request: Request):
    """Delete user account and all associated data"""
    email = request.session.get("user_email")
    
    # Delete user
    db.execute("DELETE FROM users WHERE email = ?", (email,))
    
    # Delete login attempts
    db.execute("DELETE FROM login_attempts WHERE email = ?", (email,))
    
    # Delete sessions
    request.session.clear()
    db.commit()
    return {"message": "Account deleted"}
```

### Data Retention
```
- User: Keep until deletion request
- Login attempts: Delete after 90 days
- Session logs: Delete after 30 days
- Audit logs: Delete after 7 years (compliance) or user request
```

### Consent Management
```python
@app.post("/consent")
def set_consent(request: Request, consent: dict):
    """Store user consent for data processing"""
    email = request.session.get("user_email")
    
    db.execute(
        """INSERT INTO user_consents 
           (email, data_processing, analytics, marketing, timestamp)
           VALUES (?, ?, ?, ?, ?)""",
        (email, consent['data_processing'], consent['analytics'], 
         consent['marketing'], datetime.now())
    )
    db.commit()
    return {"status": "accepted"}
```

---

## CCPA (California Consumer Privacy Act)

### California Consumer Rights
1. Right to know what personal info is collected
2. Right to delete personal information
3. Right to opt-out of sale of personal data
4. Right to non-discrimination for exercising rights

### Implementation
```python
@app.get("/privacy-policy")
def privacy_policy():
    """Disclose all data collection practices"""
    return {
        "collected_data": [
            "Email address",
            "Password hash",
            "User role",
            "Login timestamps",
            "IP address (via logs)"
        ],
        "use_purpose": "Authentication and security monitoring",
        "retention_period": "Until deletion request",
        "third_parties": "None (not sold)"
    }

@app.post("/opt-out-sale")
def opt_out_sale(request: Request):
    """User opt-out of data sale"""
    email = request.session.get("user_email")
    db.execute(
        "UPDATE users SET do_not_sell = 1 WHERE email = ?",
        (email,)
    )
    return {"status": "Opted out"}
```

---

## HIPAA (Health Insurance Portability & Accountability Act)

**If AccessGuard handles health data**, implement:

```python
# 1. Encryption in transit (TLS/HTTPS)
# 2. Encryption at rest
# 3. Audit logs for all access
# 4. Access controls (need-to-know basis)
# 5. Risk analysis & vulnerability scanning
# 6. Business associate agreements with vendors
# 7. Incident response plan
# 8. Workforce training

@app.post("/audit-log")
def audit_log_entry(timestamp: datetime, action: str, user: str, resource: str):
    """Every access to PHI must be logged"""
    db.execute(
        "INSERT INTO hipaa_audit_log (timestamp, action, user, resource) VALUES (?, ?, ?, ?)",
        (timestamp, action, user, resource)
    )
```

---

## SOC 2 Type II Compliance

### Control Objectives

**1. Security (CC)**
- Unauthorized access prevention ✅
- Cryptography for sensitive data ⚠️
- Change management procedures ❌

**2. Availability (A)**
- System uptime monitoring ❌
- Disaster recovery plan ❌
- Incident response procedures ⚠️

**3. Processing Integrity (PI)**
- Data validation ✅
- Error handling ✅
- Completeness & accuracy ✅

**4. Confidentiality (C)**
- Access controls ✅
- Sensitivity labeling ⚠️
- Data encryption ⚠️

**5. Privacy (P)**
- Privacy notice disclosure ⚠️
- Consent management ⚠️
- Data minimization ✅

### Implementation Plan
```
Phase 1 (Months 1-3):
- Document all procedures
- Implement audit logging
- Create incident response plan

Phase 2 (Months 4-6):
- Add encryption (TLS + at-rest)
- Implement monitoring
- Set up automated backup & recovery

Phase 3 (Months 7-12):
- Conduct penetration testing
- Prepare for auditor review
- Achieve SOC 2 Type II certification
```

---

## PCI DSS (Payment Card Industry Data Security Standard)

**Only required if AccessGuard handles credit cards.**

```python
# DO NOT implement
# 1. DO NOT store card numbers
# 2. DO NOT handle payment processing directly

# DO implement
# 1. Use Stripe/PayPal for payment processing
# 2. Never log card data
# 3. Use TLS 1.2+ for data in transit
# 4. Validate with PCI DSS assessor

@app.post("/billing/subscribe")
def subscribe(request: Request, plan: str):
    """Use Stripe for payment, never handle cards directly"""
    stripe.Charge.create(
        amount=plans[plan]['price'],
        currency='usd',
        source='tok_visa',
        email=request.session.get("user_email")
    )
```

---

## Accessibility (WCAG 2.1)

### Keyboard Navigation
```html
<!-- All buttons/links must have tabindex -->
<button tabindex="0">Login</button>
<input type="email" tabindex="1" />
<input type="password" tabindex="2" />
```

### Screen Reader Support
```html
<!-- Add ARIA labels -->
<button aria-label="Submit login form">Login</button>
<div role="alert" aria-live="polite">Invalid password</div>
```

### Color Contrast
```css
/* WCAG AA: >= 4.5:1 contrast ratio */
/* Text: #ffffff on #0a1628 = 18.5:1 ✅ */
/* Links: #00d4ff on #0a1628 = 4.8:1 ✅ */
```

### Text Sizing
```css
/* Users must zoom to 200% without horizontal scroll */
body { font-size: 16px; /* Not less than 12px */ }
```

---

## Data Protection Standards

### ISO 27001 (Information Security Management)
```
- Information security policy: 📝
- Access control: ✅
- Incident response: ⚠️
- Security awareness training: ❌
```

### NIST Cybersecurity Framework
```
- Identify: ⚠️ (asset inventory incomplete)
- Protect: ✅ (controls implemented)
- Detect: ✅ (monitoring active)
- Respond: ⚠️ (incident plan exists)
- Recover: ❌ (disaster recovery needed)
```

---

## Compliance Checklist

- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] GDPR consent mechanism
- [ ] CCPA opt-out option
- [ ] Data retention policy
- [ ] Incident response procedure
- [ ] Vulnerability disclosure program
- [ ] Security assessment completed
- [ ] Penetration test results reviewed
- [ ] Audit logs enabled
- [ ] Encryption in transit (HTTPS)
- [ ] Encryption at rest
- [ ] Access control enforcement
- [ ] Regular backups
- [ ] Disaster recovery tested

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
