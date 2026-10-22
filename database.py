import sqlite3
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join("database", "deepvision.db"))


def get_connection():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        image_name TEXT,

        prediction TEXT,

        confidence REAL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database Created Successfully")


if __name__ == "__main__":
    create_database()
