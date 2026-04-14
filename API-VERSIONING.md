# API-VERSIONING.md - API Versioning Strategy

## URL-Based Versioning

```python
# Version in URL path
@app.get("/api/v1/users/{email}")
def get_user_v1(email: str):
    """Version 1: Simplified response"""
    return {
        "email": email,
        "role": get_user_role(email)
    }

@app.get("/api/v2/users/{email}")
def get_user_v2(email: str):
    """Version 2: Extended response"""
    user = get_user(email)
    return {
        "email": email,
        "role": user["role"],
        "created_at": user["created_at"],
        "last_login": user["last_login"],
        "is_locked": user["is_locked"],
        "failed_attempts": user["failed_attempts"]
    }
```

## Header-Based Versioning

```python
from fastapi import Header

@app.get("/api/users/{email}")
def get_user(email: str, api_version: str = Header(None)):
    """Version from Accept-Version header"""
    
    if api_version == "v2":
        return {"email": email, "role": "...", "created_at": "...", ...}
    else:  # Default to v1
        return {"email": email, "role": "..."}
```

## Parameter-Based Versioning

```python
@app.get("/api/users/{email}")
def get_user(email: str, v: str = Query("1")):
    """Version as query parameter"""
    
    if v == "2":
        return get_user_v2_response(email)
    else:
        return get_user_v1_response(email)
```

---

## Version Deprecation Policy

```
V1: Current (2026)
V2: Introduced (2026-Q3)
V1: Deprecated (2027-01-01) - 6 months warning
V1: Sunset (2027-07-01) - No longer supported

Timeline:
- Launch V2
- Support both V1 & V2 for 6 months
- Send deprecation warnings to V1 clients
- Archive logs from V1 clients
- Remove V1 code
```

### Deprecation Warning Header

```python
@app.get("/api/v1/users/{email}")
def get_user_v1(email: str, response: Response):
    """V1 endpoint with deprecation notice"""
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Sun, 31 Dec 2027 23:59:59 GMT"
    response.headers["Link"] = '</api/v2/users/{email}>; rel="successors"'
    
    return {"email": email, "role": "..."}
```

---

## Backward Compatibility

### Non-Breaking Changes (Don't need version bump)

```
✅ Add new optional field
✅ Add new optional endpoint
✅ Add new enumeration value
✅ Add new endpoint (same base URL)
```

### Breaking Changes (Require version bump)

```
❌ Remove field
❌ Change field type (string → int)
❌ Change field name
❌ Change response structure
❌ Change error codes
❌ Change required parameters
```

### Example: Add Field Without Breaking

```python
# V1 Response
{
    "email": "user@example.com",
    "role": "admin"
}

# V2 Response (backward compatible)
{
    "email": "user@example.com",
    "role": "admin",
    "created_at": "2026-04-14"  # NEW - optional, doesn't break old clients
}
```

---

## Testing Versioning

```python
def test_api_versioning():
    """Test both API versions"""
    
    # V1 endpoint
    response_v1 = client.get("/api/v1/users/test@example.com")
    assert response_v1.status_code == 200
    assert "email" in response_v1.json()
    assert "created_at" not in response_v1.json()  # V1 doesn't have this
    
    # V2 endpoint
    response_v2 = client.get("/api/v2/users/test@example.com")
    assert response_v2.status_code == 200
    assert "email" in response_v2.json()
    assert "created_at" in response_v2.json()  # V2 has this
    
    # Both return same core data
    assert response_v1.json()["email"] == response_v2.json()["email"]
```

---

## Version Negotiation

```python
from typing import Literal

APIVersion = Literal["v1", "v2", "v3"]

def get_handler(email: str, version: APIVersion = "v1"):
    handlers = {
        "v1": get_user_v1,
        "v2": get_user_v2,
        "v3": get_user_v3,
    }
    return handlers[version](email)

@app.get("/api/users/{email}")
def get_user_auto(
    email: str,
    version: APIVersion = Query("v1")
):
    """Automatically route to correct version"""
    return get_handler(email, version)
```

---

## Migration Path

```
Client → V1 ← Deprecated ← Migrate → V2
              (6 months warning)

1. Client detects deprecation header
2. Client developer reads migration docs
3. Client updates code to use /api/v2
4. Client redeploys with new version
5. V1 sunset date passes
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
