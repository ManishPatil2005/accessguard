# 🚀 AccessGuard - Complete Setup & Deployment Guide

## ⚡ Quick Start - Run Locally (Windows)

### Option 1: Easiest Way - Run the Setup Script
1. **Navigate to project folder:**
   - Open File Explorer
   - Go to `d:\accessguard`

2. **Double-click `run.bat`**
   - This will automatically:
     ✅ Check Python installation
     ✅ Create virtual environment
     ✅ Install dependencies
     ✅ Start the application
     ✅ Open browser to `http://localhost:8000`

3. **That's it!** The app runs at `http://localhost:8000`

---

## 🌐 Deploy to Cloud (Anyone Can Access Anytime)

### ✅ Recommended: Deploy to Render (Easiest)

**Why Render?**
- ✅ Free tier available
- ✅ Automatic deployment from GitHub
- ✅ Live public URL
- ✅ No credit card needed for testing
- ✅ Perfect for portfolios

**Steps:**

1. **Fork this repository on GitHub:**
   - Go to https://github.com/ManishPatil2005/accessguard
   - Click **Fork**

2. **Sign up on Render:**
   - Go to https://render.com
   - Click **Sign up** (use your GitHub account)

3. **Create Web Service:**
   - In Render dashboard, click **New** → **Web Service**
   - Select your forked repository
   - Fill in:
     - **Name**: `accessguard`
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`
   - Click **Create Web Service**

4. **Your App is Live!** 🎉
   - Get your URL (like: `https://accessguard-xxxx.onrender.com`)
   - Share with anyone!

---

### Alternative: Deploy to Hugging Face Spaces

**Steps:**

1. **Create Hugging Face Account:**
   - Go to https://huggingface.co
   - Sign up with email or GitHub

2. **Create New Space:**
   - Go to https://huggingface.co/spaces
   - Click **Create new Space**
   - Select:
     - **Space SDK**: Docker
     - **Visibility**: Public
     - **License**: MIT

3. **Connect to Your Code:**
   ```bash
   cd d:\accessguard
   git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/accessguard
   git push huggingface main
   ```
   Replace `YOUR_USERNAME` with your Hugging Face username

4. **View Your App:**
   - Go to `https://huggingface.co/spaces/YOUR_USERNAME/accessguard`

---

## 🔒 Testing the Application

### Default Test Account
After launching, you can:
1. **Register:** Click "Register" and create a new account
2. **Login:** Use the credentials you just created
3. **Admin Features:** Check audit logs and locked accounts
4. **Test Security:** Try wrong password 3 times to see lockout

### Features to Test
✅ **Secure Registration** - Email validation, strong passwords  
✅ **Login System** - Hashed passwords, session management  
✅ **Brute Force Protection** - 3 failed attempts = account lock  
✅ **Audit Logging** - View all login attempts by admin  
✅ **Role-Based Access** - Admin can manage users  

---

## 📊 Project Structure

```
accessguard/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── run.bat                # Quick setup script (Windows)
├── app.yaml               # Hugging Face deployment config
├── Dockerfile             # Docker container config
├── static/                # CSS, JS files
├── templates/             # HTML templates
├── users.db              # SQLite database (created on first run)
└── documentation files    # README, SETUP, DEPLOYMENT, etc.
```

---

## ✅ What's Included

- **Secure Authentication System** - Production-ready
- **Brute Force Protection** - 3-strike lockout
- **SQL Injection Prevention** - 100% parameterized queries
- **Password Hashing** - SHA-256 encryption
- **Login Audit Trail** - Track all authentication attempts
- **Admin Dashboard** - Monitor users and security
- **Modern UI** - Glassmorphism design
- **Full Documentation** - Setup, API, security guides

---

## 🆘 Troubleshooting

### Problem: "Python not found" error
**Solution:** 
- Download Python 3.13+ from https://www.python.org/downloads/
- During installation, **CHECK** "Add Python to PATH"
- Restart your terminal and try again

### Problem: Port 8000 already in use
**Solution:**
- Open PowerShell and run:
  ```powershell
  Get-Process | Where-Object { $_.Name -like "*python*" } | Stop-Process -Force
  ```
- Then run `run.bat` again

### Problem: Module not found error
**Solution:**
- Delete `.venv` folder
- Run `run.bat` again to recreate environment

### Problem: Database locked error
**Solution:**
- Make sure only one instance is running
- Close all browser tabs with the app
- Restart the application

---

## 📚 Additional Documentation

- [API Documentation](API.md) - REST API endpoints
- [Architecture](ARCHITECTURE.md) - System design
- [Security Guide](SECURITY.md) - Security implementation
- [Database Schema](DATABASE.md) - Data structure
- [Development Guide](DEVELOPMENT.md) - For developers

---

## 🎯 Next Steps

**For Local Testing:**
1. Double-click `run.bat`
2. Open `http://localhost:8000`
3. Register and test the app

**For Cloud Deployment:**
1. Choose Render or Hugging Face
2. Follow deployment steps above
3. Share the public URL with anyone
4. App runs 24/7 on the cloud!

---

## 🔐 Security Notes

- **Never share** your admin credentials
- **Regularly backup** the database
- **Keep dependencies updated** - Check for security updates
- **Use HTTPS** in production (Render/HF handle this)
- **Strong passwords** - Enforce in production settings

---

## 💡 Tips

- **Portfolio Enhancement** - Deploy to cloud for interviews
- **Learning Resource** - Study the code to learn secure auth
- **Lab Environment** - Perfect for cybersecurity courses
- **Customization** - Modify HTML/CSS for your branding

---

**Questions? Issues? Check the full documentation in the project folders!**
