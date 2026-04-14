from contextlib import asynccontextmanager
from datetime import datetime
import hashlib
import os
import sqlite3
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

DB_PATH = "users.db"
LOCK_THRESHOLD = 3


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
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
    secret_key=os.getenv("ACCESSGUARD_SESSION_SECRET", "accessguard-dev-secret"),
    max_age=3600,
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


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
        "SELECT email, password_hash, role, failed_attempts, is_locked FROM users WHERE email = ?",
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
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/register")
def register_page(request: Request, message: str = ""):
    return templates.TemplateResponse(
        "register.html", {"request": request, "message": message, "message_type": "info"}
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
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "message": "Invalid role selected.",
                "message_type": "error",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 8:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "message": "Password must be at least 8 characters.",
                "message_type": "error",
            },
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
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "message": "Account already exists.",
                "message_type": "error",
            },
            status_code=status.HTTP_409_CONFLICT,
        )

    conn.close()
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "message": "Registration successful. Please sign in.",
            "message_type": "success",
        },
        status_code=status.HTTP_201_CREATED,
    )


@app.get("/login")
def login_page(request: Request, message: str = ""):
    return templates.TemplateResponse(
        "login.html", {"request": request, "message": message, "message_type": "info"}
    )


@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    normalized_email = email.strip().lower()
    user = get_user_by_email(normalized_email)

    if user is None:
        log_login_attempt(normalized_email, success=False, is_locked=False)
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "message": "Invalid credentials.",
                "message_type": "error",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if user["is_locked"] == 1:
        log_login_attempt(normalized_email, success=False, is_locked=True)
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "message": "Account is locked. Contact an admin.",
                "message_type": "error",
            },
            status_code=status.HTTP_423_LOCKED,
        )

    if hash_password(password) != user["password_hash"]:
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

        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "message": message,
                "message_type": "error",
            },
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
    session_email, session_role = require_authenticated_user(request)
    if session_role == "admin":
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        "welcome.html",
        {
            "request": request,
            "email": session_email,
            "role": session_role,
        },
    )


@app.get("/dashboard")
def dashboard(request: Request):
    require_admin(request)

    conn = get_db_connection()
    attempts = conn.execute(
        """
        SELECT email, timestamp, success, is_locked
        FROM login_attempts
        ORDER BY id DESC
        """
    ).fetchall()

    locked_users = conn.execute(
        "SELECT email, failed_attempts FROM users WHERE is_locked = 1 ORDER BY email"
    ).fetchall()
    conn.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "attempts": attempts,
            "locked_users": locked_users,
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
