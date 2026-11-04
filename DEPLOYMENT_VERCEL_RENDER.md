# 🚀 AccessGuard Deployment Guide: Vercel & Render

This guide explains how to deploy **AccessGuard** using:
1. **Option 1: Pure Vercel Deployment** (FastAPI serverless with `@vercel/python`)
2. **Option 2: Vercel + Render Hybrid Deployment** (Recommended for production-grade database persistence)

---

## ⚡ Option 1: Deploy on Vercel Only

Vercel runs Python applications via AWS Lambda serverless functions.

> [!IMPORTANT]
> **Serverless Filesystem Note**:
> Vercel lambda instances have a read-only root filesystem. The codebase is pre-configured to automatically use `/tmp/users.db` when running under Vercel (`VERCEL=1`), ensuring the database initializes and writes successfully without filesystem errors.
> For long-term persistent production storage across cold starts on serverless, set the `ACCESSGUARD_DB_PATH` environment variable or connect to an external hosted database (e.g. Turso / Supabase / Neon).

### Step-by-Step Vercel Deployment

#### Method A: Deploy via Vercel CLI (Fastest)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from project root (`d:\accessguard`)**:
   ```bash
   vercel
   ```
   - Set up and deploy `d:\accessguard`? **y**
   - Which scope? **Select your account**
   - Link to existing project? **n**
   - Project name? **accessguard**
   - In which directory is your code located? **./**
   - Auto-detected settings: Accept defaults.

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

5. **Set Environment Variable in Vercel**:
   Go to **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**:
   - `ACCESSGUARD_SESSION_SECRET`: `[generate a random secure 64-character string]`

---

#### Method B: Deploy via GitHub & Vercel Dashboard

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Configure Vercel serverless deployment and security hardening"
   git push origin master
   ```

2. **Import into Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new).
   - Select your GitHub repository (`ManishPatil2005/accessguard`).
   - In **Environment Variables**, add:
     - `ACCESSGUARD_SESSION_SECRET`: `<your-random-secret-key>`
   - Click **Deploy**.

---

## 🛡️ Option 2: Vercel + Render Hybrid Deployment (Recommended)

In this enterprise architecture:
- **Render** runs the persistent FastAPI application, background worker threads, and persistent SQLite database.
- **Vercel** acts as the high-speed Global Edge CDN, custom domain router, and static cache.

### Step 1: Deploy Backend to Render

1. Go to [render.com](https://render.com) and sign in.
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository (`accessguard`).
4. Select runtime: **Python 3**.
5. Render auto-detects `render.yaml` or you can configure manually:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variable:
   - `ACCESSGUARD_SESSION_SECRET`: Click "Generate" or set your custom secret.
7. Click **Create Web Service**. Your service URL will be generated (e.g., `https://accessguard.onrender.com`).

---

### Step 2: Route through Vercel (Edge Proxy / Custom Domain)

1. In `vercel.json`, you can proxy requests directly to your Render backend by setting up edge rewrites:
   ```json
   {
     "rewrites": [
       {
         "source": "/(.*)",
         "destination": "https://accessguard.onrender.com/$1"
       }
     ]
   }
   ```
2. Deploy to Vercel (`vercel --prod`).
3. Now your users access your custom Vercel domain (with global DDoS mitigation and Edge CDN caching), while Render handles reliable backend execution and persistent state!

---

## 🔍 Verification & Health Check Checklist

After deploying to either Vercel or Render:

- [ ] **Home Page**: Navigate to `/` (checks template rendering & aurora CSS styling).
- [ ] **Register User**: Register a test account at `/register` (verifies PBKDF2 hashing & DB write).
- [ ] **Lockout Test**: Intentionally type the wrong password 3 times at `/login` (verifies 3-strike security lockout).
- [ ] **Admin Dashboard**: Login with an admin account at `/dashboard` (verifies RBAC and audit logs).
