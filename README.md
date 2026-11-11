# Secure POS API

A point-of-sale backend for small retail businesses (shops, pharmacies, supermarkets), built with **FastAPI**, **SQLAlchemy** and **PostgreSQL**, and hardened against common API attacks.

It handles products, stock, suppliers, customers, staff accounts, sales with split payments, and receipts. Every route is protected by login and role checks, and every push runs automated tests and security scans.

---

## Security features

| Threat | Protection | Where |
|---|---|---|
| Anyone calling the API | JWT login required on every route (401 without a valid token) | `app/main.py`, `app/dependencies.py` |
| Staff doing more than their job | Role-based access. **Admin**: everything. **Cashier**: view products, make sales, add customers. No price changes, no deleting sales, no access to users or suppliers. Unknown roles are denied | `app/dependencies.py` |
| Password guessing | 5 failed logins per IP + username in 15 minutes → **429**, even if the next password is right | `app/core/rate_limit.py` |
| Finding valid usernames | Same error and the same response time for "wrong user" and "wrong password" | `app/services/auth_service.py` |
| Stolen or forged tokens | Tokens expire after 15 minutes; signature, expiry and subject are checked; deleted or inactive users are rejected | `app/core/security.py` |
| Weak or stolen password database | Argon2 hashing; 12–128 character passwords; hashes are never returned by the API | `app/core/security.py`, `app/schemas/user.py` |
| Recording a sale as someone else | The seller is taken from the login token, never from the request | `app/routers/sale.py` |
| Price tampering | Prices, totals and stock are calculated on the server; client totals are ignored | `app/services/sale_services.py` |
| Other websites calling the API | CORS allows only the configured frontend origin | `app/main.py` |
| Clickjacking, MIME sniffing, caching of sales data | Security headers on every response | `app/main.py` |
| Secrets leaking through code | All secrets in `.env`; the app refuses to start without them; `.env` is git-ignored | `app/core/security.py`, `app/database.py` |
| Over-privileged database user | The app connects as a dedicated `pos_user` that only owns `pos_db` | Setup below |
| Vulnerable libraries, unsafe code, leaked secrets | **pip-audit**, **Bandit** and **Gitleaks** run in CI on every push; Dependabot alerts on | `.github/workflows/tests.yml` |

## Features

- Product catalogue with categories and suppliers
- Stock tracking, deducted automatically on each sale
- Sales with multiple items and split payments (e.g. cash + mobile money)
- Automatic sale numbers and receipts
- Customer records with loyalty points

## Tech stack

Python 3.12 · FastAPI · SQLAlchemy · PostgreSQL · Pydantic · PyJWT · Argon2 (pwdlib) · Pytest · GitHub Actions

## Architecture

```
Request → Router → Service → Repository → Model → PostgreSQL
            │         │
            │         └─ business rules: prices, stock, payments, 404s
            └─ auth + role check runs before every protected route
```

```
app/
├── core/          security.py (JWT, hashing), rate_limit.py
├── models/        SQLAlchemy tables
├── schemas/       Pydantic validation (input rules live here)
├── repository/    database access
├── services/      business logic
├── routers/       HTTP endpoints
├── dependencies.py  login and role checks
└── main.py        app setup, CORS, security headers, route protection
scripts/create_admin.py   creates the first admin safely
tests/                    140+ tests
```

## Run it locally

**1. Install**

```bash
git clone https://github.com/jovaumurerwa/secure-pos.git
cd secure-pos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**2. Create the database and a dedicated user** (in psql or DBeaver, as the postgres admin)

```sql
CREATE USER pos_user WITH PASSWORD 'choose-a-strong-password';
CREATE DATABASE pos_db OWNER pos_user;
```

**3. Configure secrets**

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # paste the output as JWT_SECRET in .env
```

Then set `DATABASE_URL` in `.env` with your `pos_user` password.

**4. Create the first admin** (the password is typed hidden, never stored in code)

```bash
python scripts/create_admin.py
```

**5. Start the API**

```bash
uvicorn main:app --app-dir app --reload
```

Open http://127.0.0.1:8000/docs, click **Authorize**, and log in.

## API overview

| Resource | Path | Admin | Cashier |
|---|---|---|---|
| Login, current user | `/auth/login`, `/auth/me` | ✅ | ✅ |
| Products, categories | `/products`, `/categories` | full | view only |
| Sales, sale items, payments, receipts | `/sales`, `/sale-items`, `/payments`, `/receipts` | full | view + create |
| Customers | `/customers` | full | view + create |
| Users, suppliers | `/users`, `/suppliers` | full | ❌ |

**Checkout:** `POST /sales/` takes the items and payments in one request. The server looks up real prices, checks and deducts stock, calculates totals, checks that payments add up, records the logged-in cashier, and saves everything in one transaction.

## Tests

```bash
pytest -v
```

The tests use a throwaway SQLite database and cover:

- CRUD, validation (422), not found (404) and bad references (400) for every resource
- The full checkout flow: server-side prices, stock deduction, split payments, mismatched totals
- **Security:** no token, garbage token, expired token, forged signature, deleted user, inactive user, same message for wrong user and wrong password, role permissions, privilege escalation (a cashier making herself admin), rate limiting, password rules, security headers and CORS

## Design decisions and trade-offs

- **Route protection is set in one place** (`main.py`), so a new route can't be left open by mistake.
- **The rate limiter is in memory.** It is simple and fast, but it resets on restart and isn't shared between servers. With several servers, I would move it to Redis.
- **Tokens are short-lived (15 minutes)** to limit damage if one is stolen. A production version would add refresh tokens and logout/revocation.

## What I would add next

- Refresh tokens and token revocation
- Audit log of who changed prices, stock and users
- A Next.js frontend with the token kept in an httpOnly cookie
- Docker setup and deployment

## Author

Jeovanis Umurerwa · [GitHub](https://github.com/jovaumurerwa)
