# STANDARDS.md - Code & SQL Standards

## Python Code Standards

### File Structure
```python
"""Module docstring explaining purpose of the file."""

import module1    # Standard library
import module2

import thirdparty  # Third-party imports

from typing import Optional

from fastapi import FastAPI  # Local imports

CONSTANT = "value"  # All caps

def public_function():
    """Function docstring."""
    pass


class PublicClass:
    """Class docstring."""
    pass
```

### Naming Conventions
```python
# Constants
MAX_LOGIN_ATTEMPTS = 3
DB_PATH = "users.db"

# Functions & variables (snake_case)
def hash_password(password: str) -> str:
    normalized_input = password.strip().lower()
    return hashlib.sha256(normalized_input.encode()).hexdigest()

# Classes (PascalCase)
class LoginManager:
    pass

# Private (leading underscore)
def _internal_helper():
    pass
```

### Type Hints
```python
def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    """Fetch user by email, return None if not found."""
    pass

def process_users(users: list[dict]) -> dict[str, int]:
    """Process users and return statistics."""
    pass
```

### Docstrings
```python
def validate_password(password: str) -> bool:
    """
    Validate password strength.
    
    Args:
        password: Input password to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValueError: If password is None
    """
    pass
```

### Comments
```python
# Good: Explains WHY, not WHAT
# Localize email to prevent timing attacks
normalized_email = email.strip().lower()

# Bad: Redundant
# Convert to lowercase
email = email.lower()
```

### Import Organization
```python
# 1. Standard library (alphabetical)
import hashlib
import os
import sqlite3
from datetime import datetime
from typing import Optional

# 2. Third-party (alphabetical)
from fastapi import FastAPI, Form

# 3. Local imports
from .models import User

# 4. Conditional imports (bottom)
if TYPE_CHECKING:
    from typing import Any
```

## SQL Standards

### Query Format
```python
# Good: Parameterized, readable
conn.execute(
    """
    SELECT email, role FROM users
    WHERE email = ?
    LIMIT 1
    """,
    (normalized_email,)
)

# Bad: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"
```

### Naming
```sql
-- Tables (singular, lowercase)
users
login_attempts

-- Columns (lowercase, snake_case)
email
failed_attempts
is_locked
created_at

-- Indexes (idx_table_column)
idx_users_email
idx_login_timestamp

-- Constraints (pk_ or fk_)
PRIMARY KEY (email)
FOREIGN KEY (user_id)
```

### Formatting
```python
# Multi-line queries
conn.execute(
    """
    SELECT email, role, is_locked
    FROM users
    WHERE is_locked = 0
    ORDER BY email
    """,
)

# Where clause
conn.execute(
    "SELECT * FROM users WHERE email = ? AND role = ?",
    (email, role)
)
```

### Best Practices
- Always use parameterized queries
- Avoid SELECT * (specify columns)
- Use indexes for frequently queried columns
- Clean up old audit logs regularly
- Validate constraints with CHECK
- Use transactions for multiple operations

## FastAPI Endpoint Standards

```python
@app.get("/route-name")  # Lowercase, kebab-case
def endpoint_name(request: Request) -> TemplateResponse:  # snake_case
    """One-line description."""
    # Implementation
    return templates.TemplateResponse("template.html", {...})

@app.post("/register")
def register(request: Request, email: str = Form(...)) -> TemplateResponse:
    """Register new user."""
    # Validate
    # Transform
    # Store
    # Respond
    pass
```

### Response Status Codes
```python
# Success
return TemplateResponse(..., status_code=200)  # OK
return TemplateResponse(..., status_code=201)  # Created
return RedirectResponse(..., status_code=303)  # See Other

# Client Error
status_code=400  # Bad Request
status_code=401  # Unauthorized
status_code=403  # Forbidden
status_code=404  # Not Found
status_code=409  # Conflict
status_code=423  # Locked

# Server Error
status_code=500  # Internal Server Error
```

## HTML/CSS Standards

### HTML (Jinja2)
```html
<!-- Good: Semantic, accessible -->
<form method="post" action="/login">
    <label for="email">Email</label>
    <input id="email" name="email" type="email" required>
</form>

<!-- Bad: Non-semantic -->
<div>Login:</div>
<input type="text">
```

### CSS Standards
```css
/* Custom Properties (root) */
:root {
    --primary-color: #2fb5ff;
    --spacing-unit: 4px;
}

/* Selectors (BEM-ish) */
.glass-card { }
.glass-card__title { }
.glass-card--highlighted { }

/* Responsive */
@media (max-width: 600px) {
    .glass-card {
        padding: 12px;
    }
}
```

## Testing Standards

```python
# Naming: test_<function>_<scenario>
def test_login_with_correct_password():
    pass

def test_login_with_wrong_password():
    pass

def test_login_account_locked():
    pass

# Assertions
assert user is not None
assert user["role"] == "admin"
assert response.status_code == 401
```

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
