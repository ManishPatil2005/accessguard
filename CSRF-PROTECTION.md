# CSRF-PROTECTION.md - CSRF Prevention

## What is CSRF?

Cross-Site Request Forgery: Attacker tricks user into performing unwanted actions on another site.

```
Scenario:
1. User logs into bank.com
2. User visits evil.com in another tab
3. evil.com has: <img src="bank.com/transfer?amount=1000&to=attacker">
4. User's browser automatically includes bank.com cookies
5. Transfer happens without user's knowledge
```

---

## CSRF Token Implementation

### Generate Token

```python
import secrets
import hashlib

def create_csrf_token(session_id: str) -> str:
    """Generate CSRF token"""
    token = secrets.token_urlsafe(32)
    
    # Store in session
    # In production: store in Redis with TTL
    
    return token

@app.get("/login")
def login_page(request: Request):
    """Include CSRF token in form"""
    token = create_csrf_token(request.session.get("session_id"))
    request.session["csrf_token"] = token
    
    return template.render(csrf_token=token)
```

### Include Token in Form

```html
<!-- Form includes hidden CSRF token -->
<form method="POST" action="/login">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    
    <label for="email">Email</label>
    <input type="email" id="email" name="email" required>
    
    <label for="password">Password</label>
    <input type="password" id="password" name="password" required>
    
    <button type="submit">Login</button>
</form>
```

### Validate Token

```python
@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), csrf_token: str = Form(...)):
    """Validate CSRF token before processing"""
    
    # Get stored token from session
    stored_token = request.session.get("csrf_token")
    
    # Compare tokens
    if not stored_token or csrf_token != stored_token:
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    
    # Token is valid - proceed with login
    if verify_credentials(email, password):
        request.session.clear()  # Invalidate old session
        request.session["user_email"] = email
        new_token = create_csrf_token(request.session.get("session_id"))
        request.session["csrf_token"] = new_token
        
        return RedirectResponse("/welcome")
```

---

## Double-Submit Cookie Pattern

```python
import hashlib

def create_csrf_cookie(request: Request) -> str:
    """Create CSRF token in cookie"""
    token = secrets.token_urlsafe(32)
    
    # Send as cookie (HttpOnly=False so JS can read)
    response.set_cookie(
        "csrf_token",
        token,
        max_age=3600,
        secure=True,
        same_site="strict"
    )
    
    return token

@app.post("/login")
def login(request: Request, csrf_token: str = Header(...)):
    """
    Token comes from:
    1. Cookie (sent by browser automatically)
    2. Header (JavaScript reads from cookie and sends)
    
    If they match, request is legitimate
    """
    
    cookie_token = request.cookies.get("csrf_token")
    
    if not cookie_token or csrf_token != cookie_token:
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    
    # Proceed with login
```

---

## SameSite Cookie Attribute

### Automatic CSRF Protection

```python
# Most secure: SameSite=Strict
app.add_middleware(
    SessionMiddleware,
    same_site="strict"
)

# Browser won't send cookies for cross-site requests
# No token needed (but still use for defense-in-depth)
```

| SameSite | Description | Risk |
|----------|-------------|------|
| Strict | Never include in cross-site requests | Won't work with federated login |
| Lax | Include in top-level navigation, not API calls | Good balance |
| None | Always include, requires Secure flag | No CSRF protection |

---

## Implementation in AccessGuard

### Current (Not Yet Implemented)

```python
@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # No CSRF protection yet (low priority for demo)
    # Can add later when CSRF risk increases
    pass

@app.post("/unlock/{email}")
def unlock_account(request: Request, email: str):
    # Admin action should have CSRF protection
    # Add implementation
    pass
```

### Future Upgrade

```html
<!-- templates/base.html -->
<form method="POST" action="/logout">
    {% if csrf_token %}
        <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    {% endif %}
    <button type="submit">Logout</button>
</form>
```

---

## CSRF Testing

```python
def test_csrf_protection():
    """Test CSRF token validation"""
    
    # Step 1: Get login page (includes token)
    response = client.get("/login")
    assert response.status_code == 200
    
    # Extract token from form (in real app, parse HTML)
    # token = extract_token(response.text)
    
    # Step 2: Submit without token (should fail)
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "Password123"
        # No csrf_token
    })
    assert response.status_code == 403
    
    # Step 3: Submit with token (should succeed)
    response = client.post("/login", data={
        "email": "test@example.com",
        "password": "Password123",
        "csrf_token": token
    })
    assert response.status_code in [200, 303]  # Redirect or success
```

---

## CSRF vs CORS

| Feature | CSRF | CORS |
|---------|------|------|
| Purpose | Prevent unauthorized actions | Enable cross-origin requests |
| Risk | Attacker makes unwanted requests | Attacker reads data from other sites |
| Protection | CSRF tokens, SameSite cookies | CORS headers |
| Safe Methods | Only protect POST/PUT/DELETE | Applies to GET/POST/etc |

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
