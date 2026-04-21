# Quick Reference Guide

## Installation (One-liner)
```bash
git clone https://github.com/ManishPatil2005/accessguard.git && cd accessguard && python -m venv .venv && .\.venv\Scripts\activate && pip install -r requirements.txt && python main.py
```

## Frequently Used Commands

### Virtual Environment
```bash
# Activate (Windows)
.\.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Deactivate
deactivate
```

### Running the App
```bash
# Start server
python main.py

# Access in browser
http://localhost:8000
```

### Database
```bash
# Access SQLite
sqlite3 users.db

# View users
SELECT email, role FROM users;

# View login attempts
SELECT * FROM login_attempts ORDER BY timestamp DESC LIMIT 10;
```

### Testing
```bash
# Verify imports
python -c "import main"

# Test endpoints
curl http://localhost:8000/
curl -X POST http://localhost:8000/register ...
```

## Project Files at a Glance

| File | Purpose |
|------|---------|
| main.py | FastAPI application |
| requirements.txt | Dependencies |
| users.db | SQLite database |
| static/style.css | Styling |
| templates/*.html | HTML pages |
| README.md | Project overview |
| SETUP.md | Installation guide |
| API.md | Endpoint reference |

## Common Tasks

### Add New Route
```python
@app.get("/new-route")
def new_route(request: Request):
    return templates.TemplateResponse(request, "page.html", {})
```

### Add Admin Check
```python
def require_admin(request: Request):
    session_email, session_role = require_authenticated_user(request)
    if session_role != "admin":
        raise HTTPException(status_code=403)
    return session_email, session_role
```

### Query Database
```python
conn = get_db_connection()
users = conn.execute("SELECT * FROM users WHERE role = ?", ("admin",)).fetchall()
conn.close()
```

## Error Messages Reference

| Message | Cause | Solution |
|---------|-------|----------|
| "Invalid credentials" | Email/password mismatch | Check email spelling and password |
| "Account locked" | 3 failed attempts | Admin must unlock from dashboard |
| "Password too short" | Less than 8 chars | Use 8+ character password |
| "Email exists" | Already registered | Use different email |
| "TemplateNotFound" | HTML file missing | Run from project root |
| "Port already in use" | Port 8000 occupied | Use: `python main.py --port 8001` |

## Development Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] No syntax errors: `python -c "import main"`
- [ ] Server starts: `python main.py`
- [ ] Can register account
- [ ] Can login successfully
- [ ] Brute-force lock works (3 attempts)
- [ ] Admin can unlock
- [ ] Audit log shows entries
- [ ] CSS/styling loads
- [ ] Mobile responsive

## Deployment Checklist

- [ ] All tests pass
- [ ] No debug code in production
- [ ] Environment variables set
- [ ] Database backup available
- [ ] Error logging configured
- [ ] HTTPS enabled
- [ ] Password hashing working
- [ ] Session secret set
- [ ] Documentation updated
- [ ] Changelog updated

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLite Docs**: https://www.sqlite.org
- **Uvicorn**: https://www.uvicorn.org
- **Jinja2**: https://jinja.palletsprojects.com

## Support

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

## License

MIT License - See [LICENSE](LICENSE) file.
