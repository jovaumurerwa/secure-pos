# POS System API

A backend REST API for a Point of Sale (POS) system, built with FastAPI, SQLAlchemy, and PostgreSQL. It supports product catalog management, inventory tracking, staff accounts, customer records, sales transactions with split payments, and receipt generation  designed for small to medium retail businesses (supermarkets, convenience stores, pharmacies, restaurant counters).

## Features

- Product catalog with categories and suppliers
- Real-time stock/inventory tracking, automatically deducted on sale
- Staff accounts with role-based access (Admin, Manager, Cashier)
- Customer records with optional loyalty point tracking
- Sales transactions supporting multiple line items per sale
- Split payments (multiple payment methods per sale)
- Automatic receipt issuance
- Server-side price lookup and stock validation  prices and totals are never trusted from the client
- Relationship integrity enforcement (e.g. a sale item cannot reference a product that doesn't exist)

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL
- **Validation:** Pydantic
- **Password hashing:** Passlib (bcrypt)

## Project Structure

app/
├── models/ # SQLAlchemy ORM models (one file per entity)
├── schemas/ # Pydantic request/response schemas
├── repository/ # Data access layer (CRUD against the DB)
├── services/ # Business logic (validation, orchestration, stock/price rules)
├── routers/ # FastAPI route definitions (HTTP layer)
├── database.py # DB engine, session, and dependency injection
└── main.py # FastAPI app entrypoint, router registration

tests/ # Pytest suite (isolated SQLite test DB, one file per entity)
.github/workflows/tests.yml # CI: runs the test suite on push/PR


The architecture follows a layered flow:
**Router → Service → Repository → Model**
Routers stay thin (no business logic). Services hold all business rules — including 404 handling, price/stock lookups, and relationship validation. Repositories handle raw CRUD. Models define the database schema.

## Data Model

The system has 9 entities:

| Entity | Description |
|---|---|
| Category | Product categories |
| Supplier | Product suppliers |
| Product | Catalog items, stock, pricing |
| User | Staff accounts (Admin/Manager/Cashier) |
| Customer | Customer records, loyalty points |
| Sale | A completed transaction |
| SaleItem | Line items within a sale (product + quantity) |
| Payment | Payment(s) applied to a sale (supports splits) |
| Receipt | Proof-of-purchase issued for a sale |

Key relationships:
- Category → Product (one-to-many)
- Supplier → Product (one-to-many)
- Customer → Sale (one-to-many)
- User → Sale (one-to-many, the cashier who processed it)
- Sale → SaleItem (one-to-many)
- Sale → Payment (one-to-many, supports split payments)
- Sale → Receipt (one-to-one)
- Product ↔ Sale (many-to-many, resolved through SaleItem)

## Setup Instructions

### 1. Clone the repository

```bash
git clone git@github.com:marymachariam/pos-system.git
cd pos-system
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Create the database:

```bash
createdb pos_db
```

or via `psql`:

```sql
CREATE DATABASE pos_db;
```

### 5. Configure environment variables

Create a `.env` file inside the `app/` directory:

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pos_db


Adjust the username, password, host, and port to match your local PostgreSQL setup.

### 6. Run the application

```bash
cd app
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
Tables are created automatically on startup.

### 7. Explore the API

Open the interactive Swagger docs at:

http://127.0.0.1:8000/docs


## API Endpoints

All endpoints support standard REST operations (`GET`, `POST`, `PUT`, `DELETE`) unless noted otherwise.

| Resource | Base Path |
|---|---|
| Categories | `/categories` |
| Suppliers | `/suppliers` |
| Products | `/products` |
| Users | `/users` |
| Customers | `/customers` |
| Sales | `/sales` |
| Sale Items | `/sale-items` |
| Payments | `/payments` |
| Receipts | `/receipts` |

**Checkout flow:** `POST /sales/` accepts a nested payload of `sale_items` and `payments` in a single request. The server:
1. Looks up each product's real price and confirms stock is available
2. Deducts stock
3. Calculates subtotal/tax/total from the actual line items (never trusts client-submitted totals)
4. Validates that submitted payments sum to the total
5. Generates a unique sale number
6. Commits the sale, its items, and its payments atomically

## Running Tests

The project has an automated Pytest suite in `tests/` that exercises the API end-to-end through FastAPI's `TestClient`. It never touches the real PostgreSQL development database — before the app is imported, the tests point `DATABASE_URL` at a throwaway, isolated SQLite database file (created fresh per test run and deleted afterwards), and every table is dropped and recreated before each individual test so tests never leak state into one another.

### 1. Install dependencies

Make sure your virtual environment is active, then:

```bash
pip install -r requirements.txt
```

(`pytest` and `httpx` — needed for `TestClient` — are already listed in `requirements.txt`.)

### 2. Run the full suite

From the repository root:

```bash
pytest
```

Add `-v` for per-test output, or target a single file/test, e.g.:

```bash
pytest tests/test_sales.py
pytest tests/test_sales.py::test_create_sale_with_insufficient_stock_returns_400
```

### What's covered

Tests live in `tests/`, one file per entity, plus a shared `tests/conftest.py` with fixtures (`client`, and `make_*` factories for creating categories/suppliers/products/users/customers/sales). For every major entity (Category, Supplier, Product, User, Customer, Sale, SaleItem, Payment, Receipt) the suite covers:

- Successful create/list/get/update/delete operations
- `422` validation errors for missing/invalid request data
- `404` responses for operations on non-existent IDs
- `400` responses for records referencing non-existent related entities (e.g. a product with a bogus `category_id`, a sale item for a product that doesn't exist)
- The full sale checkout flow: server-side price/total calculation, stock deduction, insufficient-stock rejection, split-payment validation, and rejecting sales whose payments don't sum to the total
- Password hashing/verification and JWT helpers in `app/core/security.py`
- A handful of currently-unhandled edge cases (e.g. duplicate usernames/SKUs, deleting a sale that still has payments/items) are documented as expected exceptions rather than silently skipped, so the suite reflects the API's real behaviour today.

### Continuous Integration

A GitHub Actions workflow (`.github/workflows/tests.yml`) runs the full suite automatically on every push and on every pull request (open/update), so the build fails fast if any test breaks.

## Security Notes

- Passwords are hashed with bcrypt before storage; the `password_hash` field is never exposed in API responses.
- Prices and totals for sales are always computed server-side, never accepted directly from the client.
- Database credentials are stored in a `.env` file, excluded from version control via `.gitignore`.

## Author

Mary Macharia