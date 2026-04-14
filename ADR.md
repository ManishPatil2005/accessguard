# ADR.md - Architecture Decision Records

## ADR-001: Use FastAPI for Web Framework

**Status**: Accepted  
**Date**: 2026-04-14

### Context
Need to build a web-based authentication system demonstrating security principles.

### Decision
Use FastAPI as the web framework.

### Consequences
**Positive**:
- Modern, fast (async-capable)
- Automatic API documentation (/docs)
- Type hints support
- Integrates seamlessly with Jinja2
- Built-in security features (session management)

**Negative**:
- Not ideal for very large-scale systems (use Kubernetes)
- Limited templating compared to Django

---

## ADR-002: Use SQLite for Database

**Status**: Accepted  
**Date**: 2026-04-14

### Context
Need persistent data storage for users and audit logs.

### Decision
Use SQLite for development/demo; PostgreSQL for production.

### Consequences
**Positive**:
- Zero setup required
- File-based, portable
- Perfect for demos and education
- No separate server needed

**Negative**:
- Not suitable for high-concurrency
- Single-writer limitation
- Must migrate to PostgreSQL for production

---

## ADR-003: Use SHA-256 for Password Hashing

**Status**: Accepted (Educational Only)  
**Date**: 2026-04-14

### Context
Need password hashing for educational demonstration.

### Decision
Use SHA-256 for simplicity in educational context.

### Consequences
**Positive**:
- Deterministic (good for learning)
- Fast
- Built into Python stdlib
- Simple to understand

**Negative**:
- NOT SECURE for production (too fast)
- No salt by default
- Production must use bcrypt/Argon2

---

## ADR-004: Use Session Cookies for Auth

**Status**: Accepted  
**Date**: 2026-04-14

### Context
Need user authentication with minimal complexity.

### Decision
Use Starlette built-in session management with secure cookies.

### Consequences
**Positive**:
- Simple implementation
- HTTPOnly and Secure flags
- Session timeout built-in
- No external dependencies

**Negative**:
- Not suitable for distributed systems
- Future: Consider JWT for APIs

---

## ADR-005: Use Parameterized SQL Queries

**Status**: Accepted  
**Date**: 2026-04-14

### Context
Must prevent SQL injection vulnerabilities.

### Decision
All database queries use parameterized queries with ? placeholders.

### Consequences
**Positive**:
- Complete SQL injection prevention
- Data and SQL separated
- Industry best practice
- Easy to audit

**Negative**:
- Slightly more verbose code
- None really

---

## ADR-006: Use Glassmorphism UI Design

**Status**: Accepted  
**Date**: 2026-04-14

### Context
Need modern, professional UI matching security-focused brand.

### Decision
Implement glassmorphism (frosted glass effect) using pure CSS.

### Consequences
**Positive**:
- Modern aesthetic
- Professional appearance
- Smooth animations
- No JavaScript dependencies

**Negative**:
- Higher CPU on animations
- Not supported on very old browsers

---

## ADR-007: Implement 3-Strike Lockout

**Status**: Accepted  
**Date**: 2026-04-14

### Context
Must balance security against usability for brute-force attacks.

### Decision
Lock accounts after 3 failed attempts, admin unlock only.

### Consequences
**Positive**:
- Effective brute-force prevention
- Persistent (database-backed)
- Clear for users
- Admin control

**Negative**:
- Can lock legitimate users (password typos)
- Future: Consider time-based auto-unlock

---

## ADR-008: Log All Login Attempts

**Status**: Accepted  
**Date**: 2026-04-14

### Context
Need audit trail for security monitoring.

### Decision
Log every login attempt (success/failure) with timestamp and lock status.

### Consequences
**Positive**:
- Complete audit trail
- Detect attack patterns
- Compliance-ready
- Admin dashboard visibility

**Negative**:
- Database grows over time
- Need to archive old logs
- Query performance on large logs

---

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
