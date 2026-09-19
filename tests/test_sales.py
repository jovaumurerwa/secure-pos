import pytest


def test_create_sale_success_computes_totals_and_deducts_stock(
    client, make_user, make_product
):
    user = make_user()
    product = make_product(unit_price=100.00, quantity_in_stock=50)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [
                {"product_id": product["product_id"], "quantity": 3, "line_discount": 0}
            ],
            "payments": [{"payment_method": "Cash", "amount": 300.00}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["subtotal"] == "300.00"
    assert body["total_amount"] == "300.00"
    assert body["status"] == "Completed"
    assert body["sale_number"].startswith("SALE-")
    assert len(body["sale_items"]) == 1
    assert body["sale_items"][0]["unit_price"] == "100.00"
    assert body["sale_items"][0]["line_total"] == "300.00"
    assert len(body["payments"]) == 1

    product_after = client.get(f"/products/{product['product_id']}").json()
    assert product_after["quantity_in_stock"] == 47


def test_create_sale_never_trusts_client_submitted_prices(
    client, make_user, make_product
):
    user = make_user()
    product = make_product(unit_price=25.50, quantity_in_stock=10)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [{"product_id": product["product_id"], "quantity": 2}],
            "payments": [{"payment_method": "Cash", "amount": 51.00}],
        },
    )

    assert response.status_code == 201
    assert response.json()["sale_items"][0]["unit_price"] == "25.50"
    assert response.json()["total_amount"] == "51.00"


def test_create_sale_with_multiple_items_sums_subtotal(client, make_user, make_product):
    user = make_user()
    product_a = make_product(unit_price=100.00, quantity_in_stock=20)
    product_b = make_product(unit_price=50.00, quantity_in_stock=20)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [
                {"product_id": product_a["product_id"], "quantity": 1},
                {"product_id": product_b["product_id"], "quantity": 2},
            ],
            "payments": [{"payment_method": "Cash", "amount": 200.00}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["subtotal"] == "200.00"
    assert len(body["sale_items"]) == 2


def test_create_sale_with_split_payments_success(client, make_user, make_product):
    user = make_user()
    product = make_product(unit_price=100.00, quantity_in_stock=10)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [{"product_id": product["product_id"], "quantity": 1}],
            "payments": [
                {"payment_method": "Cash", "amount": 60.00},
                {"payment_method": "Mobile Money", "amount": 40.00},
            ],
        },
    )

    assert response.status_code == 201
    assert len(response.json()["payments"]) == 2


def test_create_sale_with_discount_reduces_total(client, make_user, make_product):
    user = make_user()
    product = make_product(unit_price=100.00, quantity_in_stock=10)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "discount_amount": 20.00,
            "sale_items": [{"product_id": product["product_id"], "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 80.00}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["subtotal"] == "100.00"
    assert body["discount_amount"] == "20.00"
    assert body["total_amount"] == "80.00"


def test_create_sale_with_walk_in_customer(client, make_user, make_product, make_customer):
    user = make_user()
    customer = make_customer()
    product = make_product(unit_price=100.00, quantity_in_stock=10)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "customer_id": customer["customer_id"],
            "sale_items": [{"product_id": product["product_id"], "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 100.00}],
        },
    )

    assert response.status_code == 201
    assert response.json()["customer_id"] == customer["customer_id"]


def test_create_sale_missing_required_field_returns_422(client, make_user):
    user = make_user()

    response = client.post(
        "/sales/",
        json={"user_id": user["user_id"], "payments": [{"payment_method": "Cash", "amount": 10}]},
    )

    assert response.status_code == 422


def test_create_sale_nonexistent_user_returns_400(client, make_product):
    product = make_product(unit_price=100.00)

    response = client.post(
        "/sales/",
        json={
            "user_id": 999999,
            "sale_items": [{"product_id": product["product_id"], "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 100.00}],
        },
    )

    assert response.status_code == 400
    assert "User" in response.json()["detail"]


def test_create_sale_nonexistent_customer_returns_400(client, make_user, make_product):
    user = make_user()
    product = make_product(unit_price=100.00)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "customer_id": 999999,
            "sale_items": [{"product_id": product["product_id"], "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 100.00}],
        },
    )

    assert response.status_code == 400
    assert "Customer" in response.json()["detail"]


def test_create_sale_nonexistent_product_returns_404(client, make_user):
    user = make_user()

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [{"product_id": 999999, "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 100.00}],
        },
    )

    assert response.status_code == 404


def test_create_sale_inactive_product_returns_404(client, make_user, make_product):
    user = make_user()
    product = make_product(is_active=False, quantity_in_stock=10)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [{"product_id": product["product_id"], "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 100.00}],
        },
    )

    assert response.status_code == 404
    assert "inactive" in response.json()["detail"]


def test_create_sale_with_insufficient_stock_returns_400(client, make_user, make_product):
    user = make_user()
    product = make_product(quantity_in_stock=1)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [{"product_id": product["product_id"], "quantity": 5}],
            "payments": [{"payment_method": "Cash", "amount": 500.00}],
        },
    )

    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

    product_after = client.get(f"/products/{product['product_id']}").json()
    assert product_after["quantity_in_stock"] == 1


def test_create_sale_with_payments_not_matching_total_returns_400(
    client, make_user, make_product
):
    user = make_user()
    product = make_product(unit_price=100.00, quantity_in_stock=10)

    response = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [{"product_id": product["product_id"], "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 50.00}],
        },
    )

    assert response.status_code == 400
    assert "do not match" in response.json()["detail"]


def test_create_sale_generates_sequential_sale_numbers(client, make_user, make_product):
    user = make_user()

    product_a = make_product(unit_price=10.00, quantity_in_stock=10)
    sale_a = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [{"product_id": product_a["product_id"], "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 10.00}],
        },
    ).json()

    product_b = make_product(unit_price=10.00, quantity_in_stock=10)
    sale_b = client.post(
        "/sales/",
        json={
            "user_id": user["user_id"],
            "sale_items": [{"product_id": product_b["product_id"], "quantity": 1}],
            "payments": [{"payment_method": "Cash", "amount": 10.00}],
        },
    ).json()

    assert sale_a["sale_number"] != sale_b["sale_number"]


def test_list_sales_returns_all_created(client, make_sale):
    make_sale()
    make_sale()

    response = client.get("/sales/")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_sale_success(client, make_sale):
    sale = make_sale()

    response = client.get(f"/sales/{sale['sale_id']}")

    assert response.status_code == 200
    assert response.json()["sale_id"] == sale["sale_id"]


def test_get_sale_not_found_returns_404(client):
    response = client.get("/sales/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found"


def test_update_sale_status_success(client, make_sale):
    sale = make_sale()

    response = client.put(f"/sales/{sale['sale_id']}", json={"status": "Refunded"})

    assert response.status_code == 200
    assert response.json()["status"] == "Refunded"


def test_update_sale_not_found_returns_404(client):
    response = client.put("/sales/999999", json={"status": "Refunded"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found"


def test_delete_sale_with_dependents_raises_integrity_error(client, make_sale):
    from sqlalchemy.exc import IntegrityError

    sale = make_sale()

    with pytest.raises(IntegrityError):
        client.delete(f"/sales/{sale['sale_id']}")


def test_delete_sale_not_found_returns_404(client):
    response = client.delete("/sales/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found"
