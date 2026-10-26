"""
====================================================
DeepVision AI — Flask Web Application
Production-Grade Authentication & Neural Forensics
====================================================
"""

import os
import sys
import json
import secrets
from datetime import datetime, timedelta, timezone
import math
from functools import wraps
import sqlite3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort
)
from werkzeug.utils import secure_filename

# Database & Migration Engine
from database import get_connection, create_database

# Security & Cryptography Utilities
from auth_utils import (
    normalize_email,
    validate_email_syntax,
    validate_password_strength,
    hash_password,
    verify_and_update_password,
    generate_otp,
    hash_otp,
    verify_otp_hash,
    generate_reset_token,
    hash_reset_token,
    generate_csrf_token,
    validate_csrf_token,
)

# Email Dispatcher
from mailer import (
    send_signup_otp_email,
    send_login_otp_email,
    send_password_reset_email,
    is_smtp_configured,
)

# AI Prediction Engine
from predict import predict_image

# ----------------------------------------------------
# Secret Key Persistence Across Restarts
# ----------------------------------------------------

def get_or_create_persistent_secret_key() -> str:
    """
    Ensures sessions persist across application restarts:
    1. Checks FLASK_SECRET_KEY or SECRET_KEY environment variables.
    2. If absent, loads or persists a random key in database/.flask_secret.
    """
    env_key = os.environ.get("FLASK_SECRET_KEY") or os.environ.get("SECRET_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    secret_file = os.path.join(os.path.dirname(__file__), "database", ".flask_secret")
    try:
        if os.path.exists(secret_file):
            with open(secret_file, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if saved:
                    return saved
        # Generate persistent key
        new_key = secrets.token_hex(32)
        os.makedirs(os.path.dirname(secret_file), exist_ok=True)
        with open(secret_file, "w", encoding="utf-8") as f:
            f.write(new_key)
        return new_key
    except Exception:
        return "deepvision_persistent_fallback_key_2026"


# ----------------------------------------------------
# Flask App Initialization & Hardening
# ----------------------------------------------------

app = Flask(__name__)

# Run safe database creation and schema migrations
create_database()

# Session and Cookie Security Configuration
app.secret_key = get_or_create_persistent_secret_key()
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

is_prod = os.environ.get("FLASK_ENV") == "production" or os.environ.get("SESSION_COOKIE_SECURE", "false").lower() in ("true", "1")
app.config["SESSION_COOKIE_SECURE"] = is_prod

# Paths Configuration
DATABASE = os.environ.get("DATABASE_PATH", os.path.join("database", "deepvision.db"))
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join("static", "uploads"))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
db_dir = os.path.dirname(DATABASE)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


# ----------------------------------------------------
# Database Helper
# ----------------------------------------------------

def get_db():
    return get_connection(DATABASE)


# ----------------------------------------------------
# DateTime Utilities (Timezone-Aware UTC)
# ----------------------------------------------------

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_db_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_db_time(time_str: str) -> datetime | None:
    if not time_str:
        return None
    clean = str(time_str).replace("T", " ").split(".")[0]
    try:
        return datetime.strptime(clean, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        return None


# ----------------------------------------------------
# CSRF Protection
# ----------------------------------------------------

@app.context_processor
def inject_csrf_token():
    """Provides csrf_token() helper to Jinja templates."""
    if "_csrf_token" not in session:
        session["_csrf_token"] = generate_csrf_token()
    return dict(csrf_token=lambda: session["_csrf_token"])


@app.before_request
def csrf_protect():
    """Validates CSRF token on all state-changing HTTP methods."""
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        # Allow static files if requested
        if request.endpoint == "static":
            return

        token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        expected = session.get("_csrf_token")

        if not token or not validate_csrf_token(token, expected):
            flash("Your security session expired or CSRF token was invalid. Please try again.", "danger")
            return redirect(request.referrer or url_for("home"))


# ----------------------------------------------------
# Authentication Decorator
# ----------------------------------------------------

def login_required(view_func):
    """Enforces authentication check for protected endpoints."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access your DeepVision workspace.", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapper


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------------------------------------------
# Home
# ----------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------------------------------
# Signup Flow (Two-Step Email Verification)
# ----------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        raw_email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # 1. Validate Username
        if not username or len(username) < 3:
            flash("Username must be at least 3 characters long.", "warning")
            return render_template("signup.html")

        # 2. Normalize and Validate Email
        is_email_valid, email, email_err = validate_email_syntax(raw_email)
        if not is_email_valid:
            flash(email_err, "danger")
            return render_template("signup.html")

        # 3. Validate Password Strength
        is_pwd_strong, pwd_failures = validate_password_strength(password)
        if not is_pwd_strong:
            for failure in pwd_failures:
                flash(f"Password requirement failed: {failure}", "danger")
            return render_template("signup.html")

        # 4. Check Password Confirmation Match
        if password != confirm_password:
            flash("Passwords do not match. Please verify both fields.", "danger")
            return render_template("signup.html")

        conn = get_db()
        cursor = conn.cursor()

        # 5. Check if verified user exists with this email
        cursor.execute("SELECT id, is_verified FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user and existing_user["is_verified"] == 1:
            conn.close()
            # Generic warning to prevent enumeration while guiding user
            flash("An account with this email is already registered. Please sign in.", "warning")
            return redirect(url_for("login"))

        # 6. Rate-Limit Check on OTP Generation (60-second cooldown per email)
        cursor.execute(
            """
            SELECT created_at FROM otp_challenges
            WHERE email = ? AND purpose = 'signup' AND used_at IS NULL
            ORDER BY created_at DESC LIMIT 1
            """,
            (email,)
        )
        last_challenge = cursor.fetchone()
        if last_challenge:
            last_created = parse_db_time(last_challenge["created_at"])
            if last_created:
                seconds_elapsed = (utc_now() - last_created).total_seconds()
                if seconds_elapsed < 60:
                    wait_sec = int(60 - seconds_elapsed)
                    conn.close()
                    flash(f"Please wait {wait_sec} second(s) before requesting a new verification code.", "warning")
                    session["pending_otp_email"] = email
                    session["pending_otp_purpose"] = "signup"
                    return redirect(url_for("verify_otp"))

        # Invalidate any prior unused signup challenges for this email
        cursor.execute(
            "UPDATE otp_challenges SET used_at = CURRENT_TIMESTAMP WHERE email = ? AND purpose = 'signup' AND used_at IS NULL",
            (email,)
        )

        # 7. Generate Cryptographically Secure OTP
        otp = generate_otp(6)
        otp_hashed = hash_otp(otp, email, "signup")
        pwd_hash = hash_password(password)

        expires_at = format_db_time(utc_now() + timedelta(minutes=5))
        pending_metadata = json.dumps({"username": username, "password_hash": pwd_hash})

        cursor.execute(
            """
            INSERT INTO otp_challenges (email, otp_hash, purpose, expires_at, metadata)
            VALUES (?, ?, 'signup', ?, ?)
            """,
            (email, otp_hashed, expires_at, pending_metadata)
        )
        conn.commit()
        conn.close()

        # 8. Dispatch OTP Email
        send_signup_otp_email(email, otp)

        # 9. Store Pending Verification Context in Session
        session["pending_otp_email"] = email
        session["pending_otp_purpose"] = "signup"

        if is_smtp_configured():
            flash(f"A 6-digit verification code has been dispatched to {email}. Please enter it below.", "info")
        else:
            flash(
                "A 6-digit verification code has been generated. (Note: SMTP is not configured on this server; check your terminal console for the development code).",
                "info"
            )

        return redirect(url_for("verify_otp"))

    return render_template("signup.html")


# ----------------------------------------------------
# OTP Verification (Signup Activation & Login 2FA)
# ----------------------------------------------------

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = session.get("pending_otp_email")
    purpose = session.get("pending_otp_purpose")

    if not email or not purpose:
        flash("No pending verification session. Please sign in or register.", "warning")
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM otp_challenges
        WHERE email = ? AND purpose = ? AND used_at IS NULL
        ORDER BY created_at DESC LIMIT 1
        """,
        (email, purpose)
    )
    challenge = cursor.fetchone()

    if not challenge:
        conn.close()
        flash("No active verification code found or code has already been used. Please request a new code.", "warning")
        return render_template("verify_otp.html", email=email, purpose=purpose, expires_in_seconds=0, attempts_remaining=0, resend_cooldown=0)

    # Calculate Expiry and Cooldown Durations
    expires_at = parse_db_time(challenge["expires_at"])
    now = utc_now()
    expires_in_seconds = max(0, int((expires_at - now).total_seconds())) if expires_at else 0

    created_at = parse_db_time(challenge["created_at"])
    elapsed_seconds = (now - created_at).total_seconds() if created_at else 999
    resend_cooldown = max(0, int(60 - elapsed_seconds))

    max_attempts = challenge["max_attempts"]
    attempts_taken = challenge["attempts"]
    attempts_remaining = max(0, max_attempts - attempts_taken)

    if request.method == "POST":
        user_otp = request.form.get("otp", "").strip()

        # A. Check Expiry
        if expires_in_seconds <= 0:
            cursor.execute("UPDATE otp_challenges SET used_at = CURRENT_TIMESTAMP WHERE id = ?", (challenge["id"],))
            conn.commit()
            conn.close()
            flash("Verification code has expired (codes expire after 5 minutes). Please click 'Resend Code'.", "danger")
            return redirect(url_for("verify_otp"))

        # B. Check Attempts
        if attempts_taken >= max_attempts:
            cursor.execute("UPDATE otp_challenges SET used_at = CURRENT_TIMESTAMP WHERE id = ?", (challenge["id"],))
            conn.commit()
            conn.close()
            flash("Maximum attempts exceeded. This verification code has been invalidated for your security.", "danger")
            return redirect(url_for("verify_otp"))

        # C. Verify OTP Cryptographic Hash
        is_otp_correct = verify_otp_hash(user_otp, challenge["otp_hash"], email, purpose)

        if not is_otp_correct:
            new_attempts = attempts_taken + 1
            cursor.execute("UPDATE otp_challenges SET attempts = ? WHERE id = ?", (new_attempts, challenge["id"]))
            conn.commit()

            remaining_now = max(0, max_attempts - new_attempts)
            if remaining_now == 0:
                cursor.execute("UPDATE otp_challenges SET used_at = CURRENT_TIMESTAMP WHERE id = ?", (challenge["id"],))
                conn.commit()
                conn.close()
                flash("Incorrect verification code. Maximum attempts reached. This code has been invalidated.", "danger")
            else:
                conn.close()
                flash(f"Incorrect verification code. {remaining_now} attempt(s) remaining.", "danger")
            return redirect(url_for("verify_otp"))

        # D. OTP Is Correct! Mark As Used
        cursor.execute("UPDATE otp_challenges SET used_at = CURRENT_TIMESTAMP WHERE id = ?", (challenge["id"],))

        if purpose == "signup":
            # Activate or Create Account
            metadata_str = challenge["metadata"] or "{}"
            try:
                reg_data = json.loads(metadata_str)
            except Exception:
                reg_data = {}

            username = reg_data.get("username", "User")
            password_hash = reg_data.get("password_hash")

            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """
                    UPDATE users
                    SET username = ?, password = ?, is_verified = 1, failed_login_attempts = 0, locked_until = NULL
                    WHERE id = ?
                    """,
                    (username, password_hash, existing["id"])
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO users (username, email, password, is_verified)
                    VALUES (?, ?, ?, 1)
                    """,
                    (username, email, password_hash)
                )

            conn.commit()
            conn.close()

            session.pop("pending_otp_email", None)
            session.pop("pending_otp_purpose", None)

            flash("Email verified successfully! Your DeepVision AI account is active. Please sign in.", "success")
            return redirect(url_for("login"))

        elif purpose == "login_2fa":
            # Complete 2FA Sign-In
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if not user:
                conn.close()
                flash("User account not found.", "danger")
                return redirect(url_for("login"))

            # Reset failed login counts and lockouts
            cursor.execute("UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = ?", (user["id"],))
            conn.commit()
            conn.close()

            # Session Fixation Defense: Regenerate session
            user_id = user["id"]
            username = user["username"]

            session.clear()
            session["user_id"] = user_id
            session["username"] = username
            session["_csrf_token"] = generate_csrf_token()
            session.permanent = True

            flash(f"Welcome back, {username}! Sign-in authorization confirmed.", "success")
            return redirect(url_for("dashboard"))

    conn.close()
    return render_template(
        "verify_otp.html",
        email=email,
        purpose=purpose,
        expires_in_seconds=expires_in_seconds,
        attempts_remaining=attempts_remaining,
        resend_cooldown=resend_cooldown
    )


# ----------------------------------------------------
# Resend OTP Code
# ----------------------------------------------------

@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    email = session.get("pending_otp_email")
    purpose = session.get("pending_otp_purpose")

    if not email or not purpose:
        flash("Verification session has expired. Please sign in again.", "warning")
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # Rate-Limit Cooldown Check (60 seconds)
    cursor.execute(
        """
        SELECT created_at, metadata FROM otp_challenges
        WHERE email = ? AND purpose = ?
        ORDER BY created_at DESC LIMIT 1
        """,
        (email, purpose)
    )
    last_challenge = cursor.fetchone()

    metadata = "{}"
    if last_challenge:
        metadata = last_challenge["metadata"] or "{}"
        last_created = parse_db_time(last_challenge["created_at"])
        if last_created:
            elapsed = (utc_now() - last_created).total_seconds()
            if elapsed < 60:
                conn.close()
                wait_sec = int(60 - elapsed)
                flash(f"Please wait {wait_sec} second(s) before requesting a new code.", "warning")
                return redirect(url_for("verify_otp"))

    # Invalidate previous unused challenges
    cursor.execute(
        "UPDATE otp_challenges SET used_at = CURRENT_TIMESTAMP WHERE email = ? AND purpose = ? AND used_at IS NULL",
        (email, purpose)
    )

    # Generate fresh OTP
    otp = generate_otp(6)
    otp_hashed = hash_otp(otp, email, purpose)
    expires_at = format_db_time(utc_now() + timedelta(minutes=5))

    cursor.execute(
        """
        INSERT INTO otp_challenges (email, otp_hash, purpose, expires_at, metadata)
        VALUES (?, ?, ?, ?, ?)
        """,
        (email, otp_hashed, purpose, expires_at, metadata)
    )
    conn.commit()
    conn.close()

    # Dispatch via Email
    if purpose == "signup":
        send_signup_otp_email(email, otp)
    else:
        send_login_otp_email(email, otp)

    if is_smtp_configured():
        flash("A new 6-digit verification code has been dispatched to your email.", "info")
    else:
        flash("A new verification code has been generated. (Check server console for local development code).", "info")

    return redirect(url_for("verify_otp"))


# ----------------------------------------------------
# Login (Password Verification + 2FA Step)
# ----------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        raw_email = request.form.get("email", "")
        password = request.form.get("password", "")

        email = normalize_email(raw_email)

        if not email or not password:
            flash("Please enter both email and password.", "warning")
            return render_template("login.html")

        conn = get_db()
        cursor = conn.cursor()

        # Record attempt for IP/Email security tracking
        client_ip = request.remote_addr or "127.0.0.1"

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        # Account Enumeration Protection: Generic error message on failure
        GENERIC_LOGIN_ERROR = "Invalid email or password."

        if not user:
            cursor.execute(
                "INSERT INTO login_attempts (ip_address, email, success) VALUES (?, ?, 0)",
                (client_ip, email)
            )
            conn.commit()
            conn.close()
            flash(GENERIC_LOGIN_ERROR, "danger")
            return render_template("login.html")

        # Check Account Temporary Lockout
        if user["locked_until"]:
            locked_until_dt = parse_db_time(user["locked_until"])
            if locked_until_dt and utc_now() < locked_until_dt:
                minutes_remaining = math.ceil((locked_until_dt - utc_now()).total_seconds() / 60)
                conn.close()
                flash(f"Account temporarily locked due to multiple failed attempts. Please try again in {minutes_remaining} minute(s).", "danger")
                return render_template("login.html")

        # Verify Password & Support Safe Plaintext-to-Hash Migration
        is_pwd_correct, needs_rehash = verify_and_update_password(user["password"], password)

        if not is_pwd_correct:
            # Increment failed attempts
            new_failed = (user["failed_login_attempts"] or 0) + 1
            if new_failed >= 5:
                lock_time = format_db_time(utc_now() + timedelta(minutes=15))
                cursor.execute(
                    "UPDATE users SET failed_login_attempts = ?, locked_until = ? WHERE id = ?",
                    (new_failed, lock_time, user["id"])
                )
                conn.commit()
                conn.close()
                flash("Account locked for 15 minutes due to 5 consecutive failed login attempts.", "danger")
                return render_template("login.html")
            else:
                cursor.execute(
                    "UPDATE users SET failed_login_attempts = ? WHERE id = ?",
                    (new_failed, user["id"])
                )
                cursor.execute(
                    "INSERT INTO login_attempts (ip_address, email, success) VALUES (?, ?, 0)",
                    (client_ip, email)
                )
                conn.commit()
                conn.close()
                remaining = 5 - new_failed
                flash(f"{GENERIC_LOGIN_ERROR} ({remaining} attempt(s) remaining before temporary lockout).", "danger")
                return render_template("login.html")

        # Upgrades legacy password to secure scrypt hash if needed
        if needs_rehash:
            upgraded_hash = hash_password(password)
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (upgraded_hash, user["id"]))
            conn.commit()

        # Check Account Verification Status
        if user["is_verified"] != 1:
            # User has not completed email verification! Issue signup OTP
            otp = generate_otp(6)
            otp_hashed = hash_otp(otp, email, "signup")
            expires_at = format_db_time(utc_now() + timedelta(minutes=5))

            cursor.execute(
                """
                INSERT INTO otp_challenges (email, otp_hash, purpose, expires_at, metadata)
                VALUES (?, ?, 'signup', ?, ?)
                """,
                (email, otp_hashed, expires_at, json.dumps({"username": user["username"], "password_hash": user["password"]}))
            )
            conn.commit()
            conn.close()

            send_signup_otp_email(email, otp)
            session["pending_otp_email"] = email
            session["pending_otp_purpose"] = "signup"

            flash("Your email address is unverified. We have sent a verification code to complete your activation.", "warning")
            return redirect(url_for("verify_otp"))

        # Verified Account -> Trigger Two-Factor Authentication (2FA)
        otp = generate_otp(6)
        otp_hashed = hash_otp(otp, email, "login_2fa")
        expires_at = format_db_time(utc_now() + timedelta(minutes=5))

        # Invalidate any older login OTPs
        cursor.execute(
            "UPDATE otp_challenges SET used_at = CURRENT_TIMESTAMP WHERE email = ? AND purpose = 'login_2fa' AND used_at IS NULL",
            (email,)
        )
        cursor.execute(
            """
            INSERT INTO otp_challenges (email, otp_hash, purpose, expires_at)
            VALUES (?, ?, 'login_2fa', ?)
            """,
            (email, otp_hashed, expires_at)
        )
        cursor.execute(
            "INSERT INTO login_attempts (ip_address, email, success) VALUES (?, ?, 1)",
            (client_ip, email)
        )
        conn.commit()
        conn.close()

        # Dispatch 2FA code
        send_login_otp_email(email, otp)

        session["pending_otp_email"] = email
        session["pending_otp_purpose"] = "login_2fa"

        if is_smtp_configured():
            flash("Two-step verification required. A 6-digit code has been dispatched to your email.", "info")
        else:
            flash("Two-step verification code generated. (Check server terminal console for development OTP).", "info")

        return redirect(url_for("verify_otp"))

    return render_template("login.html")


# ----------------------------------------------------
# Forgot Password Flow
# ----------------------------------------------------

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        raw_email = request.form.get("email", "")
        email = normalize_email(raw_email)

        GENERIC_FORGOT_MSG = "If an active account exists with that email, password reset instructions have been dispatched to your inbox."

        if not email:
            flash("Please provide a valid email address.", "warning")
            return render_template("forgot_password.html")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, email, is_verified FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and user["is_verified"] == 1:
            # Generate single-use reset token
            raw_token, token_hash = generate_reset_token()
            expires_at = format_db_time(utc_now() + timedelta(minutes=15))

            # Invalidate older unused reset tokens for this user
            cursor.execute(
                "UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE user_id = ? AND used_at IS NULL",
                (user["id"],)
            )
            cursor.execute(
                """
                INSERT INTO password_resets (user_id, token_hash, expires_at)
                VALUES (?, ?, ?)
                """,
                (user["id"], token_hash, expires_at)
            )
            conn.commit()

            # Construct reset URL
            base_url = os.environ.get("APP_BASE_URL") or request.host_url.rstrip("/")
            reset_url = f"{base_url}{url_for('reset_password')}?token={raw_token}"

            send_password_reset_email(email, reset_url)

        conn.close()
        flash(GENERIC_FORGOT_MSG, "info")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


# ----------------------------------------------------
# Reset Password (Token Verification & Password Update)
# ----------------------------------------------------

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    raw_token = request.args.get("token") or request.form.get("token", "")
    raw_token = raw_token.strip()

    if not raw_token:
        flash("Password reset token is missing. Please request a new link.", "danger")
        return redirect(url_for("forgot_password"))

    token_hash = hash_reset_token(raw_token)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM password_resets
        WHERE token_hash = ? AND used_at IS NULL
        ORDER BY created_at DESC LIMIT 1
        """,
        (token_hash,)
    )
    reset_record = cursor.fetchone()

    if not reset_record:
        conn.close()
        flash("Password reset link is invalid or has already been used. Please request a new link.", "danger")
        return redirect(url_for("forgot_password"))

    expires_at = parse_db_time(reset_record["expires_at"])
    if not expires_at or utc_now() > expires_at:
        cursor.execute("UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE id = ?", (reset_record["id"],))
        conn.commit()
        conn.close()
        flash("Password reset link has expired (links are valid for 15 minutes). Please request a new link.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        is_strong, failures = validate_password_strength(new_password)
        if not is_strong:
            for failure in failures:
                flash(f"Password requirement failed: {failure}", "danger")
            conn.close()
            return render_template("reset_password.html", token=raw_token)

        if new_password != confirm_password:
            flash("Passwords do not match. Please verify both fields.", "danger")
            conn.close()
            return render_template("reset_password.html", token=raw_token)

        # Update Password and Invalidate Token
        new_hash = hash_password(new_password)
        cursor.execute(
            """
            UPDATE users
            SET password = ?, password_changed_at = CURRENT_TIMESTAMP, failed_login_attempts = 0, locked_until = NULL
            WHERE id = ?
            """,
            (new_hash, reset_record["user_id"])
        )
        cursor.execute(
            "UPDATE password_resets SET used_at = CURRENT_TIMESTAMP WHERE id = ?",
            (reset_record["id"],)
        )
        conn.commit()
        conn.close()

        # Clear session to invalidate existing sessions across devices
        session.clear()

        flash("Your password has been reset successfully! Please sign in with your new credentials.", "success")
        return redirect(url_for("login"))

    conn.close()
    return render_template("reset_password.html", token=raw_token)


# ----------------------------------------------------
# Change Password (Authenticated Users)
# ----------------------------------------------------

@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],))
        user = cursor.fetchone()

        if not user:
            conn.close()
            session.clear()
            return redirect(url_for("login"))

        is_cur_valid, _ = verify_and_update_password(user["password"], current_password)
        if not is_cur_valid:
            conn.close()
            flash("Current password entered is incorrect.", "danger")
            return render_template("change_password.html")

        is_strong, failures = validate_password_strength(new_password)
        if not is_strong:
            conn.close()
            for failure in failures:
                flash(f"New password requirement failed: {failure}", "danger")
            return render_template("change_password.html")

        if new_password != confirm_password:
            conn.close()
            flash("New password and confirm password do not match.", "danger")
            return render_template("change_password.html")

        # Update Password
        new_hash = hash_password(new_password)
        cursor.execute(
            """
            UPDATE users
            SET password = ?, password_changed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_hash, session["user_id"])
        )
        conn.commit()
        conn.close()

        flash("Your password has been updated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("change_password.html")


# ----------------------------------------------------
# Logout
# ----------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out securely.", "info")
    return redirect(url_for("login"))


# ----------------------------------------------------
# Dashboard (Protected Route)
# ----------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM predictions WHERE user_id = ?", (user_id,))
    total_predictions = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as real_cnt FROM predictions WHERE user_id = ? AND prediction = 'Real'", (user_id,))
    real_count = cursor.fetchone()["real_cnt"]

    cursor.execute("SELECT COUNT(*) as fake_cnt FROM predictions WHERE user_id = ? AND prediction = 'Fake'", (user_id,))
    fake_count = cursor.fetchone()["fake_cnt"]

    cursor.execute(
        """
        SELECT * FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (user_id,)
    )
    recent_predictions = cursor.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        real_count=real_count,
        fake_count=fake_count,
        recent_predictions=recent_predictions
    )


# ----------------------------------------------------
# Detect Page (Protected Route)
# ----------------------------------------------------

@app.route("/detect")
@login_required
def detect():
    return render_template("detect.html")


# ----------------------------------------------------
# Predict (Protected Route — Model Inference)
# ----------------------------------------------------

@app.route("/predict", methods=["POST"])
@login_required
def predict():
    if "image" not in request.files:
        flash("No image file was uploaded.", "warning")
        return redirect(url_for("detect"))

    file = request.files["image"]
    if file.filename == "":
        flash("Please select an image file to analyze.", "warning")
        return redirect(url_for("detect"))

    if not allowed_file(file.filename):
        flash("Only JPG, JPEG, PNG, and WEBP images are supported.", "danger")
        return redirect(url_for("detect"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    print("=" * 60)
    print("Uploaded image for analysis:", filepath)

    # Perform AI Inference using existing MobileNetV2 pipeline
    result = predict_image(filepath)
    print("Prediction Result:", result)
    print("=" * 60)

    prediction = result["label"]
    confidence = result["confidence"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO predictions (user_id, image_name, prediction, confidence)
        VALUES (?, ?, ?, ?)
        """,
        (session["user_id"], filename, prediction, confidence)
    )
    conn.commit()
    conn.close()

    # Pass web-accessible forward-slash path to template
    web_image_path = "/" + filepath.replace("\\", "/")

    return render_template(
        "result.html",
        prediction=prediction,
        confidence=confidence,
        image_path=web_image_path
    )


# ----------------------------------------------------
# Result Page (Protected Route)
# ----------------------------------------------------

@app.route("/result")
@login_required
def result():
    return render_template("result.html")


# ----------------------------------------------------
# History (Protected Route)
# ----------------------------------------------------

@app.route("/history")
@login_required
def history():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    )
    predictions = cursor.fetchall()
    conn.close()

    return render_template("history.html", predictions=predictions)


# ----------------------------------------------------
# Main Entry Point
# ----------------------------------------------------

if __name__ == "__main__":
    create_database()
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
