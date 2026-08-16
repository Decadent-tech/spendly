import importlib

from database import db as db_module

import app as app_module


def test_bootstrap_db_creates_tables_and_seeds_demo_user(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB_PATH", str(tmp_path / "test.db"))

    app_module.bootstrap_db()

    conn = db_module.get_db()
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    user_count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()[0]
    expense_count = conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    conn.close()

    assert {"users", "expenses"} <= tables
    assert user_count == 1
    assert expense_count == 8


def test_importing_app_does_not_touch_the_database(monkeypatch):
    """Importing app.py must never create/seed the real DB — only running it
    as a script (python app.py) should. Guards against bootstrap_db() being
    moved out of the `if __name__ == "__main__":` guard.

    Patches database.db (not app's local names) because reloading app.py
    re-runs its `from database.db import ...` statement, which would
    otherwise rebind app's names back to the real functions and mask a
    regression.
    """
    calls = []
    monkeypatch.setattr(db_module, "init_db", lambda: calls.append("init"))
    monkeypatch.setattr(db_module, "seed_db", lambda: calls.append("seed"))

    try:
        importlib.reload(app_module)
        assert calls == []
    finally:
        monkeypatch.undo()
        importlib.reload(app_module)  # restore real bindings for later tests
