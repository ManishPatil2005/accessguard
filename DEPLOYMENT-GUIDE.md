# DEPLOYMENT.md - Deploy AccessGuard

## Free Hosting Options

### Option 1: Deploy to Render (Recommended) ⭐

Render.com offers a free tier perfect for this project.

1. **Sign up**: https://render.com (connect GitHub)
2. **Create New Service**:
   - Click "New +" → "Web Service"
   - Connect your repository: `ManishPatil2005/accessguard`
   - Name: `accessguard`
   - Runtime: `Python 3.11`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Plan: `Free`

3. **Deploy**: Click "Create Web Service"

4. **Get URL**: Your app will be live at:
   ```
   https://accessguard-<unique-id>.onrender.com
   ```

---

### Option 2: Deploy to Fly.io

1. **Install flyctl**: https://fly.io/docs/hands-on/install-flyctl/
2. **Login**: `flyctl auth login`
3. **Create app**: `flyctl launch`
4. **Deploy**: `flyctl deploy`

Your app will be live at `https://accessguard.fly.dev`

---

### Option 3: Deploy to Railway.app

1. **Sign up**: https://railway.app (GitHub login)
2. **Click**: "New Project" → "Deploy from GitHub repo"
3. **Select**: `ManishPatil2005/accessguard`
4. **Configure**: Add environment variables if needed
5. **Deploy**: Automatic

---

## Local Development

```bash
# Setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run
python main.py

# Visit http://localhost:8000
```

---

## Database

- **SQLite** - Automatically created on first run
- Reset: Delete `users.db`, restart app

---

## Testing Checklist

- [ ] Registration works
- [ ] Login works
- [ ] Admin dashboard accessible  
- [ ] Brute-force lockout (3 attempts)
- [ ] Account unlock feature works
- [ ] Audit logs show login attempts
- [ ] Logout works

---

**Version**: 1.0.0 | Ready to Deploy 🚀
