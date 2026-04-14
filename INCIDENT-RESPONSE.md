# INCIDENT-RESPONSE.md - Incident Response Procedures

## Incident Classification

| Severity | Response Time | Example |
|----------|---------------|---------|
| Critical | 15 mins | Database down, authentication broken |
| High | 1 hour | Performance degradation, security breach detected |
| Medium | 4 hours | Minor security issue, partial service unavailable |
| Low | 1 day | Documentation error, minor bug |

---

## Detection & Alerting

### Automated Alerts

```python
# Events that trigger immediate alerts

CRITICAL_ALERTS = [
    ("database_down", 1),           # Database unavailable
    ("high_error_rate", 0.05),      # >5% error rate
    ("high_lockouts", 50),          # >50 account lockouts/hour
    ("authentication_bypass", 1),   # SQL injection detected
    ("high_latency", 2000),         # p95 > 2 seconds
]

def check_alerts():
    if get_error_rate() > 0.05:
        send_alert("CRITICAL", "High error rate detected", critical=True)
    
    if get_locked_accounts_per_hour() > 50:
        send_alert("HIGH", "Potential attack detected", auto_page=True)
```

---

## Incident Response Steps

### Step 1: Detect & Assess

```
1. Alert triggered (automated or manual report)
2. Check status dashboard
3. Verify with additional metrics
4. Determine severity
5. Page on-call engineer (if critical)
6. Create incident ticket
```

### Step 2: Contain

```
For authentication bypass:
- Immediately block suspicious IPs
- Revoke compromised sessions
- Force password reset for affected users

For database down:
- Activate database failover
- Reroute traffic to backup
- Notify users of delay

For brute-force attack:
- Enable IP-based rate limiting
- Temporarily lock registration
- Alert security team
```

### Step 3: Investigate

```python
def investigate_incident(incident_id: str):
    """Gather evidence"""
    
    # Affected users
    affected = db.execute(
        "SELECT DISTINCT email FROM login_attempts WHERE success = 0 AND timestamp > ?"
    )
    
    # Attack pattern
    ips = db.execute(
        "SELECT ip, COUNT(*) FROM login_attempts WHERE success = 0 GROUP BY ip ORDER BY count DESC"
    )
    
    # Timeline
    events = db.execute(
        "SELECT timestamp, event_type, details FROM audit_log WHERE incident_related ORDER BY timestamp"
    )
    
    return {
        "affected_users": len(affected),
        "attack_sources": ips,
        "timeline": events
    }
```

### Step 4: Remediate

```
1. Fix root cause
2. Apply temporary workaround (if needed)
3. Test fix in staging
4. Deploy fix to production
5. Verify service restored
6. Communicate with users
```

### Step 5: Recover

```
1. Monitor metrics closely (next 2 hours)
2. Check for cascading failures
3. Restore backed-up data (if needed)
4. Re-enable features disabled during incident
5. Remove temporary fixes
6. Return to normal operations
```

---

## Communication Plan

### To Users

```
Initial (within 10 mins):
"We're experiencing an issue with authentication. 
Our team is investigating. We'll provide updates every 15 minutes."

Update (30 mins in):
"The issue has been identified and a fix is being deployed.
We expect service restoration within 15 minutes."

Resolution (45 mins):
"Service restored. We apologize for the disruption.
Incident root cause and preventive measures will be documented."
```

### To Team

```
Incident Channel (@team):
- Alert triggered at 09:00 UTC
- Impact: Authentication unavailable
- Severity: CRITICAL
- On-call: @alice (incident commander)
- Status page: [link]
- Action taken: Failover activated

25 mins later:
- Root cause identified: Database connection pool exhausted
- Fix deployed: Increased pool size to 50
- ETA for restore: 5 minutes

45 mins later:
- Service restored
- Timeline: [link to postmortem doc]
```

---

## Post-Incident Procedures

### Postmortem (Within 48 hours)

```
1. Timeline of events
2. Root cause analysis (5 whys)
3. Immediate actions taken
4. Preventive measures
5. Monitoring improvements
6. Process changes
7. Follow-up actions with owners
```

### Example Postmortem

```markdown
# Incident Postmortem: Database Connection Pool Exhaustion

## Timeline
- 09:00 UTC: Connection pool reached limit
- 09:03 UTC: Alert triggered (error rate > 5%)
- 09:05 UTC: On-call engineer paged
- 09:15 UTC: Fix deployed (increased pool to 50)
- 09:25 UTC: Service restored
- Duration: 25 minutes

## Root Cause
The database connection pool was sized for 20 concurrent connections.
A traffic spike from a load testing partner caused pool exhaustion.

## How We Could Have Prevented This
1. Load testing should have been scheduled in advance
2. Connection pool size should be 50 (not 20)
3. Alerts should trigger at 80% pool usage (not 100%)
4. We needed pre-deployment monitoring

## Actions
- [ ] Increase connection pool to 50 (Owner: @bob)
- [ ] Add pool usage alert at 75% (Owner: @carol)
- [ ] Document load testing procedure (Owner: @dave)
- [ ] Add connection pool metrics to dashboard (Owner: @eve)
```

---

## Prevention Checklist

Before going to production, ensure:

- [ ] Automated alerting configured for all critical metrics
- [ ] Health checks (liveness + readiness) implemented
- [ ] Database failover configured and tested
- [ ] Backups automated and verified restorable
- [ ] Rate limiting implemented
- [ ] Circuit breakers for external services
- [ ] Graceful degradation for failures
- [ ] Load testing done (baseline + spike scenarios)
- [ ] On-call procedure documented
- [ ] Incident response runbook created
- [ ] Security incident plans specific
- [ ] Disaster recovery tested (quarterly)

---

## Contact Information

```
On-Call Engineer: Check #incident-response Slack

Critical Incidents:
- Page on-call: PagerDuty
- War room: Zoom link in channel
- Status page: https://status.accessguard.io

Security Incidents:
- CISO: ciso@accessguard.io
- Security hotline: +1-555-SEC-RESP
- Report: https://bugbounty.accessguard.io

Business Impact:
- CTO: cto@accessguard.io
- Customer Success: support@accessguard.io
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
