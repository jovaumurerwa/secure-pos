import itertools
import os
import sys
from pathlib import Path


# ---------- Test settings (must run BEFORE the app is imported) ----------

TEST_DB_PATH = Path(__file__).parent / "test_pos.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"                    # tests use a throwaway SQLite file
os.environ.setdefault("JWT_SECRET", "test-only-secret-not-for-production")  # fake secret, tests only

# Let tests import app code like "from database import ..."
APP_DIR = Path(__file__).resolve().parent.parent / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import pytest  # noqa: E402
from fastapi.testclient import TestClient
from sqlalchemy import event
from database import Base, engine
from main import app


# SQLite ignores foreign keys unless we switch them on
@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Every test starts with an empty login-attempt counter
@pytest.fixture(autouse=True)
def _reset_rate_limit():
    from core import rate_limit
    rate_limit.reset_all()
    yield


# Every test starts with fresh, empty tables
@pytest.fixture(autouse=True)
def _isolated_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Delete the test database file when all tests finish
def pytest_sessionfinish(session, exitstatus):
    try:
        TEST_DB_PATH.unlink()
    except FileNotFoundError:
        pass


# ---------- Login helpers (NEW in Step 5) ----------

TEST_ADMIN_USERNAME = "test_admin"
TEST_ADMIN_PASSWORD = "Admin-Pass-123!"


def _create_test_admin():
    """Put one admin straight into the database, so tests can log in."""
    from database import session
    from models.user import User
    from core.security import hash_password

    db = session()
    try:
        db.add(User(
            full_name="Test Admin",
            username=TEST_ADMIN_USERNAME,
            password_hash=hash_password(TEST_ADMIN_PASSWORD),
            role="Admin",
            is_active=True,
        ))
        db.commit()
    finally:
        db.close()


def login(test_client, username, password):
    """Log a TestClient in and make it send the token on every request."""
    response = test_client.post("/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200, response.text
    test_client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    return test_client


@pytest.fixture
def cashier_client(client):
    """A client logged in as a Cashier (created by the admin client)."""
    response = client.post("/users/", json={
        "full_name": "Test Cashier",
        "username": "test_cashier",
        "role": "Cashier",
        "password": "Cashier-Pass-123!",
    })
    assert response.status_code == 201, response.text
    with TestClient(app) as test_client:
        yield login(test_client, "test_cashier", "Cashier-Pass-123!")


@pytest.fixture
def anon_client():
    """A client with NO token, used to prove protected routes say 401."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client():
    """A logged-in client. Logs in through the real /auth/login route."""
    _create_test_admin()
    with TestClient(app) as test_client:
        response = test_client.post(
            "/auth/login",
            data={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        test_client.headers["Authorization"] = f"Bearer {token}"  # every request now sends the token
        yield test_client


# ---------- Data factories (unchanged; they use the logged-in client) ----------

@pytest.fixture
def make_category(client):
    def _make(**overrides):
        payload = {
            "name": "Beverages",
            "description": "Drinks and refreshments",
            "is_active": True,
        }
        payload.update(overrides)
        response = client.post("/categories/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def make_supplier(client):
    def _make(**overrides):
        payload = {
            "company_name": "Acme Distributors",
            "contact_name": "Jane Doe",
            "phone": "0700000000",
            "email": "jane@acme.test",
            "address": "123 Market St",
            "is_active": True,
        }
        payload.update(overrides)
        response = client.post("/suppliers/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


_sku_counter = itertools.count(1)


@pytest.fixture
def make_product(client, make_category):
    def _make(**overrides):
        category_id = overrides.pop("category_id", None)
        if category_id is None:
            category_id = make_category()["category_id"]

        payload = {
            "sku": f"SKU-{next(_sku_counter):04d}",
            "name": "Bottled Water 500ml",
            "description": "500ml bottled water",
            "unit_price": 50.00,
            "cost_price": 30.00,
            "quantity_in_stock": 100,
            "reorder_level": 10,
            "category_id": category_id,
            "supplier_id": None,
            "is_active": True,
        }
        payload.update(overrides)
        response = client.post("/products/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


_username_counter = itertools.count(1)


@pytest.fixture
def make_user(client):
    def _make(**overrides):
        payload = {
            "full_name": "Cashier One",
            "username": f"cashier{next(_username_counter)}",
            "role": "Cashier",
            "email": "cashier1@pos.test",
            "is_active": True,
            "password": "supersecret123",
        }
        payload.update(overrides)
        response = client.post("/users/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def make_customer(client):
    def _make(**overrides):
        payload = {
            "full_name": "John Shopper",
            "phone": "0711111111",
            "email": "john@shopper.test",
            "loyalty_points": 0,
            "is_walk_in": False,
        }
        payload.update(overrides)
        response = client.post("/customers/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def make_sale(client, make_user, make_product):
    def _make(**overrides):
        user_id = overrides.pop("user_id", None)
        if user_id is None:
            user_id = make_user()["user_id"]

        if "sale_items" in overrides:
            sale_items = overrides.pop("sale_items")
            payments = overrides.pop("payments")
        else:
            product = make_product(quantity_in_stock=50, unit_price=100.00)
            sale_items = [
                {"product_id": product["product_id"], "quantity": 2, "line_discount": 0}
            ]
            payments = overrides.pop("payments", [{"payment_method": "Cash", "amount": 200.00}])

        payload = {
            "customer_id": overrides.pop("customer_id", None),
            "user_id": user_id,
            "discount_amount": overrides.pop("discount_amount", 0),
            "sale_items": sale_items,
            "payments": payments,
        }
        payload.update(overrides)
        response = client.post("/sales/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make