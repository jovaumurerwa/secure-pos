import pytest

from core.rate_limit import MAX_FAILED_ATTEMPTS


# ---------- Roles: what a cashier can and cannot do ----------

def test_cashier_can_read_products(cashier_client):
    assert cashier_client.get("/products/").status_code == 200


def test_cashier_cannot_create_products(cashier_client, make_category):
    category = make_category()
    response = cashier_client.post("/products/", json={
        "sku": "HACK-1", "name": "Free stuff", "unit_price": 1, "cost_price": 1,
        "quantity_in_stock": 1, "reorder_level": 0, "category_id": category["category_id"],
    })
    assert response.status_code == 403


def test_cashier_cannot_change_prices(cashier_client, make_product):
    product = make_product()
    response = cashier_client.put(f"/products/{product['product_id']}", json={"unit_price": 1})
    assert response.status_code == 403


@pytest.mark.parametrize("path", ["/users/", "/suppliers/"])
def test_cashier_cannot_see_admin_areas(cashier_client, path):
    assert cashier_client.get(path).status_code == 403


def test_cashier_cannot_make_themselves_admin(cashier_client):
    me = cashier_client.get("/auth/me").json()
    response = cashier_client.put(f"/users/{me['user_id']}", json={"role": "Admin"})
    assert response.status_code == 403


def test_cashier_can_make_a_sale_under_own_name(cashier_client, make_product):
    product = make_product(unit_price=100.00, quantity_in_stock=5)
    me = cashier_client.get("/auth/me").json()
    response = cashier_client.post("/sales/", json={
        "sale_items": [{"product_id": product["product_id"], "quantity": 1}],
        "payments": [{"payment_method": "Cash", "amount": 100.00}],
    })
    assert response.status_code == 201, response.text
    assert response.json()["user_id"] == me["user_id"]


def test_cashier_cannot_delete_sales(cashier_client, make_sale):
    sale = make_sale()
    assert cashier_client.delete(f"/sales/{sale['sale_id']}").status_code == 403


def test_admin_can_do_admin_things(client):
    assert client.get("/users/").status_code == 200
    assert client.get("/suppliers/").status_code == 200


# ---------- Input rules ----------

def test_short_password_is_rejected(client):
    response = client.post("/users/", json={
        "full_name": "Weak", "username": "weak_user", "role": "Cashier", "password": "short",
    })
    assert response.status_code == 422


def test_unknown_role_is_rejected(client):
    response = client.post("/users/", json={
        "full_name": "Boss", "username": "boss", "role": "SuperAdmin", "password": "Long-Enough-Pass-1",
    })
    assert response.status_code == 422


def test_weird_username_is_rejected(client):
    response = client.post("/users/", json={
        "full_name": "Bad", "username": "<script>", "role": "Cashier", "password": "Long-Enough-Pass-1",
    })
    assert response.status_code == 422


# ---------- Rate limiting on login ----------

def test_login_is_blocked_after_too_many_wrong_passwords(client, anon_client):
    for _ in range(MAX_FAILED_ATTEMPTS):
        r = anon_client.post("/auth/login", data={"username": "test_admin", "password": "wrong"})
        assert r.status_code == 401

    blocked = anon_client.post("/auth/login", data={"username": "test_admin", "password": "wrong"})
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers


def test_even_correct_password_is_blocked_while_locked(client, anon_client):
    from conftest import TEST_ADMIN_PASSWORD
    for _ in range(MAX_FAILED_ATTEMPTS):
        anon_client.post("/auth/login", data={"username": "test_admin", "password": "wrong"})
    # Otherwise an attacker could keep guessing and just watch for a 200
    r = anon_client.post("/auth/login", data={"username": "test_admin", "password": TEST_ADMIN_PASSWORD})
    assert r.status_code == 429


# ---------- Security headers and CORS ----------

def test_security_headers_are_present(anon_client):
    headers = anon_client.get("/").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"


def test_cors_allows_our_frontend_only(anon_client):
    ok = anon_client.options("/products/", headers={
        "Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET",
    })
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3000"

    evil = anon_client.options("/products/", headers={
        "Origin": "https://evil.example", "Access-Control-Request-Method": "GET",
    })
    assert "access-control-allow-origin" not in evil.headers
