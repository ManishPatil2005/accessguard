# LOGGING.md - Logging & Observability

## Logging Strategy

### Python Logging Configuration

```python
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log levels
logger.debug("Detailed debugging info")        # Development
logger.info("General info messages")           # Production
logger.warning("Warning messages")             # Attention needed
logger.error("Error messages")                 # Problem occurred
logger.critical("Critical errors")             # System failure
```

### Structured Logging (JSON)

```python
import json

def log_structured(level: str, event: str, **kwargs):
    """Log structured events as JSON"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "event": event,
        "service": "accessguard",
        **kwargs
    }
    logger.info(json.dumps(log_entry))

# Usage
log_structured("info", "user_login", 
    email="user@example.com",
    role="admin",
    ip="192.168.1.100"
)

# Output
# {"timestamp": "2026-04-14T10:30:45", "level": "info", "event": "user_login", "service": "accessguard", "email": "user@example.com", ...}
```

---

## Event Logging in Code

### Login Events

```python
def log_login_event(email: str, success: bool, reason: str = None):
    """Log login attempts"""
    logger.info(f"Login attempt: email={email}, success={success}")
    if reason:
        logger.info(f"Reason: {reason}")

# Examples
log_login_event("user@example.com", True)
log_login_event("user@example.com", False, "Invalid password")
log_login_event("user@example.com", False, "Account locked")
```

### Security Events

```python
def log_security_event(event_type: str, details: dict):
    """Log security-related events"""
    logger.warning(f"SECURITY: {event_type}: {json.dumps(details)}")

# Examples
log_security_event("failed_login_lockout", {
    "email": "attacker@evil.com",
    "attempts": 3,
    "ip": "203.0.113.45"
})

log_security_event("sql_injection_attempt", {
    "endpoint": "/login",
    "input": "email' OR '1'='1",
    "ip": "203.0.113.45"
})
```

### Admin Actions

```python
def log_admin_action(admin_email: str, action: str, target: str):
    """Log all admin actions"""
    logger.info(f"ADMIN: {action} by {admin_email} on {target}")

# Examples
log_admin_action("admin@example.com", "unlock_account", "user@example.com")
```

---

## Log Levels by Module

```
Main application: INFO
Database operations: DEBUG (development), INFO (production)
Security events: WARNING (always)
User actions: INFO
Performance metrics: DEBUG
System errors: ERROR/CRITICAL
```

---

## Log Retention Policy

```
Development:
- Keep logs: 7 days
- Format: stdout + file

Staging:
- Keep logs: 30 days
- Format: file + centralized service
- Retention: Daily rotation

Production:
- Keep logs: 90 days (compliance)
- Format: Structured JSON
- Service: Datadog/Splunk/ELK
- Encryption: At rest
```

---

## Centralized Logging (Production)

### Sending to Datadog

```python
import logging
from datadog_api_client import ApiClient, Configuration

# Configure Datadog
config = Configuration()
config.api_key["apiKeyAuth"] = os.environ.get('DATADOG_API_KEY')

def send_log_to_datadog(message: str, level: str = "info"):
    with ApiClient(config) as api_client:
        logger = logging.getLogger(__name__)
        handler = logging.handlers.DatadogHTTPHandler(
            api_key=config.api_key["apiKeyAuth"],
            hostname="accessguard"
        )
        logger.addHandler(handler)
```

### Using CloudWatch (AWS)

```python
import watchtower

# Add CloudWatch handler
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group='accessguard',
    stream_name='app'
)
logger.addHandler(cloudwatch_handler)

# Logs appear in AWS CloudWatch
```

### Using ELK Stack (Elasticsearch, Logstash, Kibana)

```python
# Send logs to Logstash
import logging
import logstash

handler = logstash.TCPLogstashHandler(
    host='logstash.example.com',
    port=5000,
    version=1
)
logger.addHandler(handler)

# View in Kibana @ kibana.example.com
```

---

## log Analysis

### Find Failed Logins

```bash
# In production logs
grep "failed" app.log | grep "login" | wc -l

# In ELK/Datadog
search: level:error AND event:login_failed
```

### Find Brute-Force Attacks

```bash
# Find multiple failures from same IP
grep "login_failed" app.log | \
  grep "ip:" | \
  awk -F'ip:' '{print $2}' | \
  awk '{print $1}' | \
  sort | uniq -c | sort -rn
```

### Find Admin Unlock Events

```bash
# All admin actions
grep "ADMIN:" app.log | grep "unlock"
```

---

## Log File Location

```
Development:
- app.log (local directory)
- stderr output (terminal)

Production:
- /var/log/accessguard/app.log
- Centralized: Datadog/CloudWatch/ELK
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
