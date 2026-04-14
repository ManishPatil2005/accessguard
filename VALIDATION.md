# VALIDATION.md - Input Validation & Sanitization

## Email Validation

```python
import re
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email: str) -> tuple[bool, str]:
    """Validate email format and domain"""
    try:
        # RFC 5322 compliant validation
        valid = validate_email(email, check_deliverability=True)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)

# Examples
validate_email_address("user@example.com")       # ✅
validate_email_address("user@example")           # ❌ No TLD
validate_email_address("user @example.com")      # ❌ Space
validate_email_address("user+tag@example.com")   # ✅ Plus addressing
```

## Password Validation

```python
import re

def validate_password(password: str) -> tuple[bool, list]:
    """Validate password strength"""
    errors = []
    
    # Length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    # Uppercase check
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain uppercase letter")
    
    # Lowercase check
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain lowercase letter")
    
    # Number check
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain number")
    
    # Special character check
    if not re.search(r'[!@#$%^&*]', password):
        errors.append("Password must contain special character (!@#$%^&*)")
    
    return len(errors) == 0, errors

# Examples
validate_password("WeakPass")           # ❌ No special char
validate_password("Test@1234")          # ✅ All requirements met
validate_password("test@1234")          # ❌ No uppercase
```

## Form Input Sanitization

```python
from html import escape
import re

def sanitize_email(email: str) -> str:
    """Remove dangerous characters, preserve valid"""
    # Allow: a-z0-9.+_@
    # Remove: everything else
    return re.sub(r'[^a-zA-Z0-9.+_@-]', '', email).strip()

def sanitize_role(role: str) -> str:
    """Only allow predefined roles"""
    allowed_roles = ['admin', 'user']
    return role if role in allowed_roles else 'user'

def html_escape(text: str) -> str:
    """Escape HTML special characters"""
    return escape(text)

# Examples
sanitize_email("user@example.com")           # "user@example.com"
sanitize_email("<script>alert()</script>")   # "scriptaler"
sanitize_role("admin")                       # "admin"
sanitize_role("superadmin")                  # "user" (not allowed)
html_escape("<b>Bold</b>")                   # "&lt;b&gt;Bold&lt;/b&gt;"
```

## SQL Injection Prevention (Already Implemented)

```python
# ✅ SAFE: Parameterized query
db.execute(
    "SELECT * FROM users WHERE email = ?",
    (email,)  # Parameter passed separately
)

# ❌ UNSAFE: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)

# ✅ SAFE: Multiple parameters
db.execute(
    "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
    (email, password_hash, role)
)
```

## XSS Prevention

```python
# ✅ SAFE: Jinja2 auto-escapes by default
<p>{{ user_input }}</p>
<!-- If user_input contains <script>, it renders as &lt;script&gt; -->

# ❌ UNSAFE: Using raw (don't do this)
<p>{{ user_input | safe }}</p>
<!-- This allows HTML/JavaScript execution -->

# ✅ SAFE: Explicit escaping in Python
from jinja2 import escape
safe_input = escape(user_input)

# ✅ SAFE: HTML-escape before storing (belt & suspenders)
db.execute(
    "INSERT INTO comments (text) VALUES (?)",
    (escape(user_text),)
)
```

## CSRF Prevention

```python
# ✅ SAFE: Hidden token in form (not implemented yet)
<form method="POST" action="/login">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="email" name="email">
    <input type="password" name="password">
</form>

# Validate token on POST
@app.post("/login")
def login(request: Request, csrf_token: str = Form(...)):
    if csrf_token != request.session.get("csrf_token"):
        raise HTTPException(status_code=403, detail="CSRF validation failed")
```

## File Upload Validation (Future)

```python
import mimetypes
import os
from pathlib import Path

def validate_upload(filename: str, file_content: bytes) -> tuple[bool, str]:
    """Validate file uploads"""
    
    # Check filename for path traversal attacks
    path = Path(filename)
    if ".." in str(path) or path.is_absolute():
        return False, "Invalid filename"
    
    # Check file size (max 5MB)
    if len(file_content) > 5 * 1024 * 1024:
        return False, "File too large (max 5MB)"
    
    # Check file type (whitelist)
    allowed_types = {'.jpg', '.png', '.pdf'}
    file_ext = path.suffix.lower()
    if file_ext not in allowed_types:
        return False, f"File type not allowed. Allowed: {allowed_types}"
    
    # Check MIME type matches extension
    detected_mime, _ = mimetypes.guess_type(filename)
    allowed_mimes = {
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.pdf': 'application/pdf'
    }
    if detected_mime != allowed_mimes.get(file_ext):
        return False, "File MIME type mismatch"
    
    return True, "OK"

# Example
validate_upload("resume.pdf", file_bytes)      # ✅
validate_upload("../../../etc/passwd", bytes)  # ❌ Path traversal
validate_upload("virus.exe", bytes)            # ❌ Not allowed extension
```

## URL Validation

```python
from urllib.parse import urlparse
import re

def is_safe_redirect_url(url: str, allowed_hosts: list) -> bool:
    """Prevent open redirect attacks"""
    
    # Reject absolute URLs except whitelisted hosts
    if url.startswith("//") or url.startswith("http"):
        try:
            parsed = urlparse(url)
            if parsed.netloc not in allowed_hosts:
                return False
        except ValueError:
            return False
    
    # Allow relative URLs (start with /)
    if not url.startswith("/"):
        return False
    
    # Prevent null bytes
    if "\x00" in url:
        return False
    
    return True

# Examples
is_safe_redirect_url("/dashboard", ["localhost"])        # ✅
is_safe_redirect_url("https://evil.com", ["localhost"]) # ❌
is_safe_redirect_url("javascript:alert()", ["localhost"]) # ❌
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
