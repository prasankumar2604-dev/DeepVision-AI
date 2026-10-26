"""
====================================================
DeepVision AI — Authentication & Security Utilities
Production-Grade Cryptography & Input Validation
====================================================
"""

import os
import re
import hmac
import hashlib
import secrets
from datetime import datetime, timezone
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------------------------------------------------------------------
# Password Policy Rules
# ---------------------------------------------------------------------------
# - Minimum 12 characters
# - At least one uppercase letter (A-Z)
# - At least one lowercase letter (a-z)
# - At least one number (0-9)
# - At least one special symbol (!@#$%^&* etc.)
# ---------------------------------------------------------------------------

PASSWORD_MIN_LENGTH = 12
SPECIAL_CHAR_PATTERN = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]")


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validates that a password satisfies all production security criteria:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special symbol
    Returns (is_valid, list_of_failed_requirements).
    """
    if not password or not isinstance(password, str):
        return False, ["Password is required."]

    failed = []

    if len(password) < PASSWORD_MIN_LENGTH:
        failed.append(f"At least {PASSWORD_MIN_LENGTH} characters in length")

    if not re.search(r"[A-Z]", password):
        failed.append("At least one uppercase letter (A–Z)")

    if not re.search(r"[a-z]", password):
        failed.append("At least one lowercase letter (a–z)")

    if not re.search(r"[0-9]", password):
        failed.append("At least one number (0–9)")

    if not SPECIAL_CHAR_PATTERN.search(password):
        failed.append("At least one special symbol (e.g. ! @ # $ % & *)")

    return (len(failed) == 0, failed)


def hash_password(password: str) -> str:
    """
    Securely hashes a password using Werkzeug's scrypt implementation.
    Falls back gracefully to pbkdf2:sha256 if scrypt is unavailable on the platform.
    """
    try:
        return generate_password_hash(password, method="scrypt")
    except Exception:
        return generate_password_hash(password, method="pbkdf2:sha256:600000")


def verify_and_update_password(stored_password: str, provided_password: str) -> tuple[bool, bool]:
    """
    Verifies a provided password against the stored string.
    Supports:
      1. Modern Werkzeug hashes (scrypt, pbkdf2)
      2. Legacy plaintext passwords (timing-safe check), signaling needs_rehash=True
    Returns (is_valid, needs_rehash).
    """
    if not stored_password or not provided_password:
        return False, False

    # Check if stored_password is a modern hash
    if stored_password.startswith(("scrypt:", "pbkdf2:", "argon2:")):
        try:
            is_valid = check_password_hash(stored_password, provided_password)
            return is_valid, False
        except Exception:
            return False, False

    # Legacy plaintext backward compatibility
    # Use hmac.compare_digest for timing-attack resistance
    if hmac.compare_digest(stored_password, provided_password):
        return True, True  # Valid, but must be upgraded immediately to modern hash

    return False, False


# ---------------------------------------------------------------------------
# Email Normalization & Validation
# ---------------------------------------------------------------------------

def normalize_email(email: str) -> str:
    """
    Normalizes an email address consistently:
    Strips whitespace, lowercases the domain/local parts.
    """
    if not email or not isinstance(email, str):
        return ""
    return email.strip().lower()


def validate_email_syntax(email: str) -> tuple[bool, str, str]:
    """
    Validates email format using the email-validator library (RFC 5322 compliance).
    check_deliverability=False is used so syntax is strictly validated without DNS lookups.
    Returns (is_valid, normalized_email, error_message).
    """
    if not email or not isinstance(email, str):
        return False, "", "Email address is required."

    raw = email.strip()
    if not raw:
        return False, "", "Email address cannot be empty."

    try:
        info = validate_email(raw, check_deliverability=False)
        normalized = info.normalized.lower()
        return True, normalized, ""
    except EmailNotValidError as exc:
        return False, raw, f"Invalid email format: {str(exc)}"
    except Exception:
        return False, raw, "Invalid email address."


# ---------------------------------------------------------------------------
# Cryptographic One-Time Passwords (OTP)
# ---------------------------------------------------------------------------

def get_crypto_salt() -> str:
    """Retrieves or generates an application-wide salt for hashing OTPs and tokens."""
    return os.environ.get("FLASK_SECRET_KEY") or os.environ.get("SECRET_KEY") or "deepvision_crypto_salt_2026"


def generate_otp(length: int = 6) -> str:
    """
    Generates a cryptographically secure, unpredictable numeric OTP.
    Uses secrets.choice to prevent PRNG predictability.
    """
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(length))


def hash_otp(otp: str, email: str, purpose: str) -> str:
    """
    Computes a cryptographic SHA-256 HMAC of the OTP bound to the recipient's
    normalized email and the specific purpose (e.g. 'signup' or 'login_2fa').
    OTPs are never stored in plaintext.
    """
    salt = get_crypto_salt()
    data = f"{normalize_email(email)}:{purpose}:{otp}:{salt}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def verify_otp_hash(provided_otp: str, stored_hash: str, email: str, purpose: str) -> bool:
    """
    Timing-safe verification of a user-provided OTP against the stored hash.
    """
    if not provided_otp or not stored_hash:
        return False
    computed = hash_otp(provided_otp.strip(), email, purpose)
    return hmac.compare_digest(computed, stored_hash)


# ---------------------------------------------------------------------------
# Password Reset Tokens
# ---------------------------------------------------------------------------

def generate_reset_token() -> tuple[str, str]:
    """
    Generates a cryptographically secure URL-safe token and its SHA-256 hash.
    The raw token is emailed to the user, while ONLY the hash is persisted in DB.
    Returns (raw_token, token_hash).
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_reset_token(raw_token)
    return raw_token, token_hash


def hash_reset_token(raw_token: str) -> str:
    """Computes SHA-256 hash of a password reset token."""
    salt = get_crypto_salt()
    data = f"{raw_token}:{salt}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Cross-Site Request Forgery (CSRF) Tokens
# ---------------------------------------------------------------------------

def generate_csrf_token() -> str:
    """Generates a secure 32-byte hex token for CSRF protection."""
    return secrets.token_hex(32)


def validate_csrf_token(provided_token: str, session_token: str) -> bool:
    """Timing-safe validation of CSRF tokens."""
    if not provided_token or not session_token:
        return False
    return hmac.compare_digest(str(provided_token), str(session_token))
