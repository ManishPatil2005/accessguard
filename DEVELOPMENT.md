# DEVELOPMENT.md - Development Workflow

## Local Development Setup

### Initial Setup
```bash
git clone [repo]
cd AccessGuard
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Code Changes

#### Main Application (main.py)
```python
# Structure:
#  1. Imports
#  2. Database connection
#  3. Helper functions
#  4. Authentication handlers
#  5. Endpoint handlers
#  6. Startup/shutdown
```

#### Templates (templates/)
```
- Templates use Jinja2 syntax
- Inherit from base.html
- Use {% block content %} for expansion
```

#### Styling (static/style.css)
```
- CSS custom properties (--variables)
- Glassmorphism components (.glass-card)
- Responsive design with media queries
```

### Testing Changes
```bash
# Verify backend imports
python -c "import main"

# Start server
python main.py

# Test in browser
http://127.0.0.1:8000/

# Run manual tests (see TESTING.md)
```

### Code Standards

#### Python PEP 8
```python
# Function naming
def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    pass

# Variable naming (snake_case)
normalized_email = email.strip().lower()

# No line width > 100 chars
# Two blank lines between functions
# One blank line between methods
```

#### SQL Standards
```python
# Always parameterized
conn.execute("SELECT * FROM users WHERE email = ?", (email,))

# Never: f-strings
# Never: .format()
# Never: % formatting
```

#### Comments
```python
# Brief:  # One-line comment for simple logic

# Detail (for complex logic):
"""
Multi-line explanation of why this is needed,
what it does, and any alternatives considered.
"""
```

### Commit Guidelines

Format: `<type>: <description>`

```
feature: add email verification
fix: prevent SQL injection in email field
docs: update README with setup instructions
refactor: extract authentication logic
style: fix code formatting in main.py
perf: optimize login query with index
security: upgrade password hashing to bcrypt
test: add test cases for brute-force
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add -A
git commit -m "feature: describe what you did"

# Push to remote
git push origin feature/your-feature

# Create Pull Request
# Request review
# Merge when approved
```

### Common Development Tasks

#### Add New Endpoint
```python
@app.get("/new-route")
def new_route(request: Request):
    # Function body
    pass

# Update templates/base.html: Add nav link
# Update documentation: Add to ROUTES section
# Add test case in TESTING.md
```

#### Fix Bug
```
1. Document the issue
2. Write test case that fails
3. Implement fix
4. Verify test passes
5. Commit: "fix: describe issue and solution"
```

#### Add Database Field
```python
# Update init_db() to add new column
# Add migration script
# Update all queries that touch table
# Update documentation
```

### Debugging Tips

#### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

#### Check Database State
```bash
sqlite3 users.db
SELECT * FROM users WHERE email = 'test@example.com';
.quit
```

#### Browser DevTools (F12)
- Network tab: Check HTTP requests/responses
- Application tab: Check cookies and session
- Console tab: Check for JavaScript errors

---

**Version**: 1.0.0 | **Last Updated**: April 14, 2026
