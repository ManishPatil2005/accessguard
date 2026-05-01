# Deploy AccessGuard to Hugging Face Spaces

## 🚀 Quick Deployment Steps

### Step 1: Create a Hugging Face Account
1. Go to https://huggingface.co/
2. Click **Sign Up** and create an account
3. Verify your email

### Step 2: Create a New Space
1. Go to https://huggingface.co/spaces
2. Click **Create new Space**
3. Fill in:
   - **Space name**: `accessguard` (or any name)
   - **License**: MIT
   - **Space SDK**: Docker
   - **Visibility**: Public (anyone can access)

### Step 3: Push Code to Hugging Face
After creating the space, you'll get a git command. Run this in your terminal:

```bash
cd d:\accessguard
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/accessguard
git push huggingface main
```

**Replace `YOUR_USERNAME` with your Hugging Face username**

### Step 4: Done!
Your app will automatically deploy. Access it at:
```
https://huggingface.co/spaces/YOUR_USERNAME/accessguard
```

---

## 🔧 Alternative: Deploy to Render (Easier, Free Tier Available)

### Step 1: Create Render Account
Go to https://render.com and sign up

### Step 2: Connect GitHub
1. Fork this repo on GitHub
2. Go to Render dashboard
3. Click **New** → **Web Service**
4. Select your GitHub repo
5. Configure:
   - **Name**: accessguard
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Step 3: Deploy
Click **Create Web Service** and wait for deployment

Your live link will be something like:
```
https://accessguard-xxxx.onrender.com
```

---

## 🏠 Local Setup (If you want to run on your computer)

### Prerequisites
- Python 3.13+
- pip

### Installation

1. **Open PowerShell and navigate to project:**
   ```powershell
   cd d:\accessguard
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```powershell
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open in browser:**
   ```
   http://localhost:8000
   ```

---

## 📋 Default Credentials (For Testing)

When you first run the app, the database is empty. You can register a new account:
- **Username**: test@example.com
- **Password**: SecurePass123!

After registration, you can:
- Login with your credentials
- View login audit logs (if admin)
- Test the 3-strike lockout feature

---

## ⚠️ Security Notes

- Change session secret in production
- Use HTTPS in production
- Regularly backup the database
- Monitor audit logs
- Keep dependencies updated
