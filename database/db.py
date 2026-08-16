import datetime
import sqlite3

from werkzeug.security import generate_password_hash

DB_PATH = "expense_tracker.db"

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    """Return a new SQLite connection with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables if they don't already exist."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    conn.commit()
    conn.close()


def seed_db():
    """Insert sample data for development, if the users table is empty."""
    conn = get_db()

    existing_user = conn.execute("SELECT id FROM users").fetchone()

    if existing_user is None:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        today = datetime.date.today()
        days = [1, 3, 5, 8, 10, 13, 16, 19]  # safe for every month, incl. Feb
        amounts = [12.50, 45.00, 9.99, 60.00, 25.75, 18.20, 8.50, 32.00]
        categories = CATEGORIES + [CATEGORIES[0]]  # all 7, plus one repeat = 8 rows
        descriptions = [
            "Lunch", "Train pass", "Movie ticket", "Electricity bill",
            "Doctor visit", "New shoes", "Coffee", "Groceries",
        ]

        rows = [
            (user_id, amounts[i], categories[i], today.replace(day=days[i]).isoformat(), descriptions[i])
            for i in range(8)
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            rows,
        )

    conn.commit()
    conn.close()
