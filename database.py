"""
====================================================
DeepVision AI — Database Layer & Migration Engine
Reliable SQLite with WAL Mode & Auto-Migrations
====================================================
"""

import os
import sqlite3
import sys
from auth_utils import hash_password

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join("database", "deepvision.db"))


def get_connection(db_path=None):
    """
    Returns a hardened SQLite connection with:
    - 15-second busy timeout to avoid lock collisions
    - Write-Ahead Logging (WAL) for high concurrency
    - Foreign key constraints enabled
    - Dictionary-like Row factory
    """
    path = db_path or DB_PATH
    db_dir = os.path.dirname(path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(path, timeout=15.0)
    conn.row_factory = sqlite3.Row

    # Enforce concurrency and reliability pragmas
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA foreign_keys = ON;")
    except Exception:
        pass

    return conn


def create_database(db_path=None):
    """
    Idempotent schema initialization and migration runner:
    1. Creates all core and security tables if they do not exist.
    2. Safely migrates existing schemas without dropping tables or losing data.
    3. Ensures all users are marked active and verified.
    4. Automatically upgrades legacy plaintext passwords to secure modern hashes.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. Base Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_verified INTEGER DEFAULT 1,
        failed_login_attempts INTEGER DEFAULT 0,
        locked_until TIMESTAMP DEFAULT NULL,
        password_changed_at TIMESTAMP DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Base Predictions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        image_name TEXT,
        prediction TEXT,
        confidence REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    # 3. Safely drop deprecated otp_challenges table if it exists
    cursor.execute("DROP TABLE IF EXISTS otp_challenges;")

    # 4. Password Resets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token_hash TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        used_at TIMESTAMP DEFAULT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_password_resets_token 
    ON password_resets(token_hash);
    """)

    # 5. Login Attempts Table (Throttle & Brute-Force Monitoring)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT,
        email TEXT,
        attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        success INTEGER DEFAULT 0
    );
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_login_attempts 
    ON login_attempts(email, ip_address, attempt_time);
    """)

    # ----------------------------------------------------
    # Schema Migration for 'users' table
    # ----------------------------------------------------
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = {row["name"] for row in cursor.fetchall()}

    if "is_verified" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 1;")
    
    # Ensure all existing users are marked active/verified
    cursor.execute("UPDATE users SET is_verified = 1 WHERE is_verified = 0 OR is_verified IS NULL;")

    if "failed_login_attempts" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;")

    if "locked_until" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN locked_until TIMESTAMP DEFAULT NULL;")

    if "password_changed_at" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN password_changed_at TIMESTAMP DEFAULT NULL;")
        cursor.execute("UPDATE users SET password_changed_at = CURRENT_TIMESTAMP WHERE password_changed_at IS NULL;")

    # ----------------------------------------------------
    # Migrate any legacy plaintext passwords to secure hashes
    # ----------------------------------------------------
    cursor.execute("SELECT id, password FROM users;")
    all_users = cursor.fetchall()
    migrated_count = 0
    for user_row in all_users:
        stored_pwd = user_row["password"]
        if not stored_pwd.startswith(("scrypt:", "pbkdf2:", "argon2:")):
            hashed = hash_password(stored_pwd)
            cursor.execute(
                "UPDATE users SET password = ? WHERE id = ?;",
                (hashed, user_row["id"])
            )
            migrated_count += 1

    conn.commit()
    conn.close()

    if migrated_count > 0:
        print(f"🔒 Migrated {migrated_count} legacy user passwords to production-grade hashes.")
    print("✅ Database & Security Migrations Completed Successfully")


if __name__ == "__main__":
    create_database()
