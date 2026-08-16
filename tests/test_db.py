import sqlite3

import pytest

from database import db as db_module


def test_get_db_returns_connection_with_row_factory_and_fk_enabled(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))

    conn = db_module.get_db()
    try:
        assert isinstance(conn, sqlite3.Connection)
        assert conn.row_factory is sqlite3.Row
        fk_status = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk_status == 1
    finally:
        conn.close()


def test_init_db_creates_users_and_expenses_tables(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))

    db_module.init_db()

    conn = db_module.get_db()
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    expense_columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(expenses)")
    }
    conn.close()

    assert "users" in tables
    assert "expenses" in tables
    assert {"date", "created_at"} <= expense_columns


def test_seed_db_inserts_sample_data_once(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))

    db_module.init_db()
    db_module.seed_db()
    db_module.seed_db()  # calling twice should not duplicate the demo user

    conn = db_module.get_db()
    user_count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()[0]
    expense_rows = conn.execute("SELECT category FROM expenses").fetchall()
    conn.close()

    assert user_count == 1
    assert len(expense_rows) == 8
    seeded_categories = {row["category"] for row in expense_rows}
    assert seeded_categories == set(db_module.CATEGORIES)


def test_seed_db_stores_hashed_password_not_plaintext(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))

    db_module.init_db()
    db_module.seed_db()

    conn = db_module.get_db()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()
    conn.close()

    assert row["password_hash"] != "demo123"


def test_duplicate_email_raises_integrity_error(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))

    db_module.init_db()
    conn = db_module.get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("First User", "dup@example.com", "hash1"),
    )
    conn.commit()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Second User", "dup@example.com", "hash2"),
        )

    conn.close()


def test_invalid_user_id_raises_integrity_error(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))

    db_module.init_db()
    conn = db_module.get_db()

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (999, 10.0, "Food", "2026-08-01"),
        )

    conn.close()
