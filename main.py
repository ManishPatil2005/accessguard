from contextlib import asynccontextmanager
from datetime import datetime
import hashlib
import hmac
import os
from pathlib import Path
import shutil
import sqlite3
from typing import Optional, Any

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = str(BASE_DIR / "static")
TEMPLATES_DIR = str(BASE_DIR / "templates")
LOCK_THRESHOLD = 3


def get_db_path() -> str:
    """Resolve database path with fallback for Vercel Serverless read-only filesystem."""
    custom_path = os.getenv("ACCESSGUARD_DB_PATH")
    if custom_path:
        return custom_path

    # On Vercel serverless environment, local filesystem is read-only except /tmp
    if os.getenv("VERCEL") or os.getenv("NOW_REGION"):
        tmp_db = "/tmp/users.db"
        local_db = BASE_DIR / "users.db"
        if not os.path.exists(tmp_db) and local_db.exists():
            try:
                shutil.copyfile(str(local_db), tmp_db)
            except Exception:
                pass
        return tmp_db

    return str(BASE_DIR / "users.db")


def init_db() -> None:
    db_path = get_db_path()
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            is_locked INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL,
            is_locked INTEGER NOT NULL
        )
        """
    )

    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(title="AccessGuard", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("ACCESSGUARD_SESSION_SECRET", "accessguard-dev-secret-change-in-production"),
    max_age=3600,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def render_template(
    request: Request,
    name: str,
    context: Optional[dict[str, Any]] = None,
    status_code: int = 200,
):
    """Universal template renderer compatible across all Starlette/FastAPI versions."""
    ctx = dict(context) if context else {}
    ctx["request"] = request
    try:
        # Starlette 0.35+ signature
        return templates.TemplateResponse(
            request=request,
            name=name,
            context=ctx,
            status_code=status_code,
        )
    except TypeError:
        # Legacy Starlette signature
        return templates.TemplateResponse(
            name,
            ctx,
            status_code=status_code,
        )


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Generate salted PBKDF2-HMAC-SHA256 password hash (100,000 rounds)."""
    salt = os.urandom(16).hex()
    iterations = 100000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations).hex()
    return f"pbkdf2:sha256:{iterations}${salt}${derived}"


def verify_and_upgrade_password(password: str, stored_hash: str, email: Optional[str] = None) -> bool:
    """Verify password against salted PBKDF2 hash or legacy unsalted SHA-256 hash."""
    if stored_hash.startswith("pbkdf2:sha256:"):
        try:
            parts = stored_hash.split("$")
            iterations = int(parts[0].split(":")[2])
            salt = bytes.fromhex(parts[1])
            expected_key = parts[2]
            computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations).hex()
            return hmac.compare_digest(computed, expected_key)
        except Exception:
            return False

    # Legacy unsalted SHA-256 fallback with transparent upgrade
    legacy_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if hmac.compare_digest(legacy_hash, stored_hash):
        if email:
            try:
                new_hash = hash_password(password)
                conn = get_db_connection()
                conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))
                conn.commit()
                conn.close()
            except Exception:
                pass
        return True
    return False


def log_login_attempt(email: str, success: bool, is_locked: bool) -> None:
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO login_attempts (email, timestamp, success, is_locked)
        VALUES (?, ?, ?, ?)
        """,
        (email, timestamp, int(success), int(is_locked)),
    )
    conn.commit()
    conn.close()


def get_user_by_email(email: str) -> Optional[sqlite3.Row]:
    conn = get_db_connection()
    user = conn.execute(
        "SELECT email, password_hash, role, failed_attempts, is_locked, created_at FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    return user


def get_user_account_status(email: str) -> Optional[sqlite3.Row]:
    """Retrieve full user account status for display."""
    conn = get_db_connection()
    user = conn.execute(
        "SELECT email, role, failed_attempts, is_locked, created_at FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    return user


def require_authenticated_user(request: Request) -> tuple[str, str]:
    session_email = request.session.get("user_email")
    session_role = request.session.get("role")
    if not session_email or not session_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return session_email, session_role


def require_admin(request: Request) -> tuple[str, str]:
    session_email, session_role = require_authenticated_user(request)
    if session_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return session_email, session_role


@app.get("/")
def home(request: Request):
    return render_template(request, "home.html")


@app.get("/register")
def register_page(request: Request, message: str = ""):
    return render_template(
        request,
        "register.html",
        {"message": message, "message_type": "info"},
    )


@app.post("/register")
def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
):
    normalized_email = email.strip().lower()
    normalized_role = role.strip().lower()

    if normalized_role not in {"admin", "user"}:
        return render_template(
            request,
            "register.html",
            {"message": "Invalid role selected.", "message_type": "error"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 8:
        return render_template(
            request,
            "register.html",
            {"message": "Password must be at least 8 characters.", "message_type": "error"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    password_hash = hash_password(password)

    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO users (email, password_hash, role, failed_attempts, is_locked, created_at)
            VALUES (?, ?, ?, 0, 0, ?)
            """,
            (normalized_email, password_hash, normalized_role, created_at),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return render_template(
            request,
            "register.html",
            {"message": "Account already exists.", "message_type": "error"},
            status_code=status.HTTP_409_CONFLICT,
        )

    conn.close()
    return render_template(
        request,
        "register.html",
        {"message": "Registration successful. Please sign in.", "message_type": "success"},
        status_code=status.HTTP_201_CREATED,
    )


@app.get("/login")
def login_page(request: Request, message: str = ""):
    return render_template(
        request,
        "login.html",
        {"message": message, "message_type": "info"},
    )


@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    normalized_email = email.strip().lower()
    user = get_user_by_email(normalized_email)

    if user is None:
        log_login_attempt(normalized_email, success=False, is_locked=False)
        return render_template(
            request,
            "login.html",
            {"message": "Invalid credentials.", "message_type": "error"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if user["is_locked"] == 1:
        log_login_attempt(normalized_email, success=False, is_locked=True)
        return render_template(
            request,
            "login.html",
            {"message": "Account is locked. Contact an admin.", "message_type": "error"},
            status_code=status.HTTP_423_LOCKED,
        )

    if not verify_and_upgrade_password(password, user["password_hash"], normalized_email):
        next_failed_attempts = user["failed_attempts"] + 1
        lock_account = next_failed_attempts >= LOCK_THRESHOLD

        conn = get_db_connection()
        conn.execute(
            "UPDATE users SET failed_attempts = ?, is_locked = ? WHERE email = ?",
            (next_failed_attempts, int(lock_account), normalized_email),
        )
        conn.commit()
        conn.close()

        log_login_attempt(normalized_email, success=False, is_locked=lock_account)

        if lock_account:
            message = "Account locked after 3 failed attempts. Contact an admin."
            status_code = status.HTTP_423_LOCKED
        else:
            message = "Invalid credentials."
            status_code = status.HTTP_401_UNAUTHORIZED

        return render_template(
            request,
            "login.html",
            {"message": message, "message_type": "error"},
            status_code=status_code,
        )

    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET failed_attempts = 0 WHERE email = ?",
        (normalized_email,),
    )
    conn.commit()
    conn.close()

    request.session["user_email"] = normalized_email
    request.session["role"] = user["role"]

    log_login_attempt(normalized_email, success=True, is_locked=False)

    destination = "/dashboard" if user["role"] == "admin" else "/welcome"
    return RedirectResponse(url=destination, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/welcome")
def welcome(request: Request):
    """User-only welcome page. Admins are redirected to dashboard."""
    session_email, session_role = require_authenticated_user(request)

    if session_role == "admin":
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    if session_role != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User access only")

    user_account = get_user_account_status(session_email)
    if not user_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return render_template(
        request,
        "welcome.html",
        {
            "email": session_email,
            "role": session_role,
            "is_locked": user_account["is_locked"],
            "failed_attempts": user_account["failed_attempts"],
            "created_at": user_account["created_at"],
        },
    )


@app.get("/dashboard")
def dashboard(request: Request):
    """Admin-only dashboard for security monitoring and account management."""
    admin_email, admin_role = require_admin(request)

    conn = get_db_connection()

    attempts = conn.execute(
        """
        SELECT email, timestamp, success, is_locked
        FROM login_attempts
        ORDER BY id DESC
        LIMIT 50
        """
    ).fetchall()

    locked_users = conn.execute(
        "SELECT email, failed_attempts, created_at FROM users WHERE is_locked = 1 ORDER BY email"
    ).fetchall()

    all_users = conn.execute(
        "SELECT email, role, is_locked, failed_attempts, created_at FROM users ORDER BY email"
    ).fetchall()

    total_users = len(all_users)
    locked_count = len(locked_users)
    active_users = total_users - locked_count

    conn.close()

    return render_template(
        request,
        "dashboard.html",
        {
            "admin_email": admin_email,
            "attempts": attempts,
            "locked_users": locked_users,
            "all_users": all_users,
            "total_users": total_users,
            "active_users": active_users,
            "locked_count": locked_count,
            "message": request.query_params.get("message", ""),
        },
    )


@app.post("/unlock/{email}")
def unlock_account(request: Request, email: str):
    require_admin(request)

    normalized_email = email.strip().lower()
    conn = get_db_connection()
    existing = conn.execute("SELECT email FROM users WHERE email = ?", (normalized_email,)).fetchone()

    if existing is None:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    conn.execute(
        "UPDATE users SET is_locked = 0, failed_attempts = 0 WHERE email = ?",
        (normalized_email,),
    )
    conn.commit()
    conn.close()

    return RedirectResponse(
        url="/dashboard?message=Account+unlocked+successfully",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
