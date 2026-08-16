# Spec: Registration

## Overview
Spendly currently has a `/register` route that renders a form but does not
process submissions — there is no backend logic to create an account. This
step wires up account creation: validating the submitted form, hashing the
password, inserting a new row into the `users` table, and giving the user
feedback on success or failure. It builds directly on the `users` table
created in Step 1 (Database Setup).

## Depends on
- Step 1 — Database Setup (`users` table with `name`, `email`,
  `password_hash`, `created_at` columns; `get_db()` connection helper)

## Routes
- `POST /register` — process the registration form: validate input, check
  for duplicate email, hash the password, insert the new user, then
  redirect to `/login` with a success message — public
- `GET /register` — already exists (renders the form) — no change needed

## Database changes
No database changes. The existing `users` table (`database/db.py`) already
has the columns required (`name`, `email` UNIQUE, `password_hash`,
`created_at`).

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html` — already has an `{% if error %}` block
    wired to display a passed-in `error` variable; no structural change
    needed, just confirm the field names (`name`, `email`, `password`)
    sent by the form match what the route reads from `request.form`
  - `templates/login.html` — add a flash/success message block (using
    Flask's `get_flashed_messages`) so the "account created" message from
    the registration redirect has somewhere to render

## Files to change
- `app.py` — add `SECRET_KEY` config (required for `flash()`), implement
  `POST` handling on the `/register` route
- `templates/login.html` — render flashed messages

## Files to create
- `.claude/specs/02-registration.md` — this spec

## New dependencies
No new dependencies. `werkzeug.security` (already used in `database/db.py`)
provides `generate_password_hash`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash`) — never store
  or log plaintext passwords
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate on the server even though the form has `required` attributes
  client-side (name, email, password all non-empty; password minimum 8
  characters to match the placeholder text)
- Check for an existing email before inserting; on conflict, re-render
  `register.html` with an `error` message and HTTP 200 (do not insert)
- Do not auto-login the user after registration in this step — redirect to
  `/login` with a success flash message (session-based login/logout is a
  separate, not-yet-implemented step)

## Definition of done
- [ ] Visiting `/register` still renders the form (GET unchanged)
- [ ] Submitting the form with a new name/email/password creates exactly
      one new row in `users`, with `password_hash` set to a werkzeug hash
      (not the plaintext password)
- [ ] Submitting with an email that already exists does not insert a
      second row, and re-renders `register.html` with a visible error
      message
- [ ] Submitting with an empty name, email, or password (bypassing the
      client-side `required` check, e.g. via curl) returns a visible error
      instead of a server crash or silent failure
- [ ] Submitting with a password under 8 characters returns a visible
      error and does not create the user
- [ ] On success, the browser is redirected to `/login` and a success
      message is visible on that page
- [ ] All new SQL statements use `?` placeholders — no f-strings or
      `.format()` in query strings
