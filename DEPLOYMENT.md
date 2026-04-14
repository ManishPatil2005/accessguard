# DEPLOYMENT.md - Production Deployment Guide

## 🚀 Deployment Checklist

### Pre-Deployment Security Review
- [ ] All parameterized SQL queries (no string concatenation)
- [ ] Password hashing implemented (SHA-256 or better)
- [ ] Brute-force protection active (3-strike lockout)
- [ ] Audit logging complete
- [ ] RBAC enforced on all protected endpoints
- [ ] Error messages don't leak data
- [ ] Rate limiting configured
- [ ] HTTPS enforced
- [ ] Security headers added
- [ ] Environment variables set correctly

### Environment Variables
```bash
ACCESSGUARD_SESSION_SECRET=prod-only-secret-key-change-this
ACCESSGUARD_DB_PATH=/var/lib/accessguard/users.db
ACCESSGUARD_DEBUG=False
ACCESSGUARD_HOST=0.0.0.0
ACCESSGUARD_PORT=8000
```

### Database Backup Strategy
```bash
# Daily backup
0 2 * * * sqlite3 /var/lib/accessguard/users.db ".backup /backup/accessguard-$(date +%Y%m%d).db"

# Retention: Keep 30 days
find /backup -name "accessguard-*.db" -mtime +30 -delete
```

### SSL/TLS Configuration
```nginx
# Nginx reverse proxy
server {
    listen 443 ssl http2;
    server_name accessguard.example.com;
    
    ssl_certificate /etc/letsencrypt/live/accessguard.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/accessguard.example.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP redirect
server {
    listen 80;
    server_name accessguard.example.com;
    return 301 https://$server_name$request_uri;
}
```

### Performance Optimization
- Use PostgreSQL instead of SQLite for high-load
- Enable connection pooling
- Add caching layer (Redis)
- Use CDN for static assets
- Configure database indexes

### Monitoring & Alerting
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

login_attempts = Counter('accessguard_login_attempts_total', 'Total login attempts')
failed_logins = Counter('accessguard_failed_logins_total', 'Failed login attempts')
locked_accounts = Gauge('accessguard_locked_accounts', 'Locked accounts count')
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
