---
name: implement-step
description: Find and implement the next unimplemented "Step N" milestone in this Flask course project (app.py placeholder routes, database/db.py stub), writing a matching pytest test. Use when the user says "implement the next step", "do step N", or asks to move the expense tracker forward.
---

This project ("Spendly") is built incrementally. Progress is marked with "Step N" comments:

- `app.py` — placeholder routes under the "Placeholder routes — students will implement these" section each return a string like `"Logout — coming in Step 3"`.
- `database/db.py` — a stub comment describing `get_db()`, `init_db()`, `seed_db()` (Step 1).

## Steps

1. Read `app.py` and `database/db.py` to find the lowest-numbered step that is still a placeholder/stub.
2. If the user named a specific step number, implement that one instead (even out of order) — but confirm with them first if it depends on an earlier step that isn't done yet (e.g. Step 7 "Add expense" needs `database/db.py`'s `get_db()`/`init_db()` from Step 1).
3. Implement only that one step — do not build ahead into later placeholder routes/features.
4. Write a pytest test for the new behavior in `tests/test_*.py` (create the `tests/` directory the first time). Use `pytest-flask` fixtures (e.g. `client`) where useful.
5. Run `pytest` and confirm the new test (and existing ones) pass.
6. Report which step was implemented and what remains as the next placeholder.
