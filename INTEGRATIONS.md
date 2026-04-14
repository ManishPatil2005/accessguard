# INTEGRATIONS.md - Third-Party Service Integrations

## Email Service Integration (Planned for v1.1)

### Sendgrid
```python
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

sg = sendgrid.SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

def send_verification_email(email: str, token: str):
    message = Mail(
        from_email='noreply@accessguard.io',
        to_emails=email,
        subject='Verify Your AccessGuard Account',
        html_content=f'<a href="https://app.accessguard.io/verify/{token}">Click to verify</a>'
    )
    response = sg.send(message)
    return response.status_code == 202
```

### AWS SES
```python
import boto3

ses = boto3.client('ses', region_name='us-east-1')

def send_verification_email(email: str, token: str):
    return ses.send_email(
        Source='noreply@accessguard.io',
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Verify Your AccessGuard Account'},
            'Body': {'Html': {'Data': f'<a href="...{token}">Verify</a>'}}
        }
    )
```

---

## SMS Service Integration (Planned for v2.0)

### Twilio
```python
from twilio.rest import Client

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

def send_sms_otp(phone: str, otp: str):
    message = client.messages.create(
        body=f'Your AccessGuard OTP is: {otp}. Valid for 5 minutes.',
        from_=os.environ.get('TWILIO_PHONE'),
        to=phone
    )
    return message.sid
```

---

## Push Notification Integration (Planned for v2.0)

### Firebase Cloud Messaging
```python
import firebase_admin
from firebase_admin import credentials, messaging

firebase_admin.initialize_app(credentials.Certificate('serviceAccountKey.json'))

def send_login_notification(device_token: str, location: str):
    message = messaging.Message(
        notification=messaging.Notification(
            title='New Login',
            body=f'Login from {location}'
        ),
        token=device_token,
    )
    return messaging.send(message)
```

---

## Analytics Integration (Planned for v1.2)

### Google Analytics
```html
<!-- Add to base.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>

<!-- Track events -->
<script>
gtag('event', 'login', {
  'email': email_hash,
  'role': role
});
</script>
```

### Mixpanel
```python
from mixpanel import Mixpanel

mp = Mixpanel(os.environ.get('MIXPANEL_TOKEN'))

def track_login(email: str, role: str):
    mp.track(email, 'User Login', {
        'role': role,
        'timestamp': datetime.now().isoformat()
    })
```

---

## Monitoring & Observability (Production)

### Datadog
```python
from datadog import initialize, api
import logging

# Send logs
ddtrace_patched_logger = logging.getLogger()

def log_security_event(event_type: str, details: dict):
    ddtrace_patched_logger.info(
        f'Security event: {event_type}',
        extra={'ddtags': f'env:{os.environ["ENV"]},alert:true'},
        **details
    )
```

### New Relic
```python
import newrelic.agent
newrelic.agent.initialize()

@newrelic.agent.function_trace()
def login(email: str, password: str):
    # Track performance
    pass
```

### Sentry (Error Tracking)
```python
import sentry_sdk

sentry_sdk.init(
    os.environ.get('SENTRY_DSN'),
    traces_sample_rate=1.0
)

try:
    login_user(email, password)
except Exception as e:
    sentry_sdk.capture_exception(e)
```

---

## Version Control Integration

### GitHub Actions (CI/CD)
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: python -m pylint **.py
```

### GitLab CI
```yaml
before_script:
  - pip install -r requirements.txt

test:
  script:
    - pytest
    - pylint **.py

security:
  script:
    - bandit -r .
```

---

## Container Registries (v3.0)

### Docker Hub
```
docker build -t yourname/accessguard:1.0 .
docker push yourname/accessguard:1.0
```

### AWS ECR
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker tag accessguard:1.0 $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/accessguard:1.0
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/accessguard:1.0
```

---

## Secrets Management

### HashiCorp Vault
```python
import hvac

client = hvac.Client(url='http://127.0.0.1:8200', token='s.xxxxxxxx')

secret = client.secrets.kv.v2.read_secret_version(path='accessguard')
DATABASE_URL = secret['data']['data']['database_url']
SECRET_KEY = secret['data']['data']['secret_key']
```

### AWS Secrets Manager
```python
import json
import boto3

client = boto3.client('secretsmanager', region_name='us-east-1')

secret = client.get_secret_value(SecretId='accessguard/secrets')
secrets = json.loads(secret['SecretString'])
DATABASE_URL = secrets['database_url']
SECRET_KEY = secrets['secret_key']
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
