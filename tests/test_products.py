import pytest
from sqlalchemy.exc import IntegrityError


def test_create_product_success(client, make_category, make_supplier):
    category = make_category()
    supplier = make_supplier()

    response = client.post(
        "/products/",
        json={
            "sku": "SKU-TEST-1",
            "name": "Bottled Water 500ml",
            "description": "500ml bottled water",
            "unit_price": 50.00,
            "cost_price": 30.00,
            "quantity_in_stock": 100,
            "reorder_level": 10,
            "category_id": category["category_id"],
            "supplier_id": supplier["supplier_id"],
            "is_active": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "SKU-TEST-1"
    assert body["unit_price"] == "50.00"
    assert "product_id" in body
    assert "created_at" in body


def test_create_product_without_supplier_is_allowed(client, make_category):
    category = make_category()

    response = client.post(
        "/products/",
        json={
            "sku": "SKU-TEST-2",
            "name": "Bread Loaf",
            "unit_price": 60.00,
            "category_id": category["category_id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["supplier_id"] is None


def test_create_product_missing_required_field_returns_422(client, make_category):
    category = make_category()

    response = client.post(
        "/products/",
        json={"name": "No SKU", "unit_price": 10.00, "category_id": category["category_id"]},
    )

    assert response.status_code == 422


def test_create_product_wrong_type_returns_422(client, make_category):
    category = make_category()

    response = client.post(
        "/products/",
        json={
            "sku": "SKU-BAD-TYPE",
            "name": "Bad Price",
            "unit_price": "not-a-decimal",
            "category_id": category["category_id"],
        },
    )

    assert response.status_code == 422


def test_create_product_nonexistent_category_returns_400(client):
    response = client.post(
        "/products/",
        json={
            "sku": "SKU-NO-CAT",
            "name": "Orphan Product",
            "unit_price": 10.00,
            "category_id": 999999,
        },
    )

    assert response.status_code == 400
    assert "Category" in response.json()["detail"]


def test_create_product_nonexistent_supplier_returns_400(client, make_category):
    category = make_category()

    response = client.post(
        "/products/",
        json={
            "sku": "SKU-NO-SUPPLIER",
            "name": "Orphan Supplier Product",
            "unit_price": 10.00,
            "category_id": category["category_id"],
            "supplier_id": 999999,
        },
    )

    assert response.status_code == 400
    assert "Supplier" in response.json()["detail"]


def test_create_product_duplicate_sku_raises_integrity_error(
    client, make_product, make_category
):
    make_product(sku="SKU-DUPLICATE")
    category = make_category()

    with pytest.raises(IntegrityError):
        client.post(
            "/products/",
            json={
                "sku": "SKU-DUPLICATE",
                "name": "Duplicate SKU Product",
                "unit_price": 10.00,
                "category_id": category["category_id"],
            },
        )


def test_list_products_returns_all_created(client, make_product):
    make_product(name="Bottled Water")
    make_product(name="Bread Loaf")

    response = client.get("/products/")

    assert response.status_code == 200
    names = {p["name"] for p in response.json()}
    assert {"Bottled Water", "Bread Loaf"}.issubset(names)


def test_get_product_success(client, make_product):
    product = make_product(name="Bottled Water")

    response = client.get(f"/products/{product['product_id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Bottled Water"


def test_get_product_not_found_returns_404(client):
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product_success(client, make_product):
    product = make_product(quantity_in_stock=100)

    response = client.put(
        f"/products/{product['product_id']}", json={"quantity_in_stock": 75}
    )

    assert response.status_code == 200
    assert response.json()["quantity_in_stock"] == 75


def test_update_product_nonexistent_category_returns_400(client, make_product):
    product = make_product()

    response = client.put(
        f"/products/{product['product_id']}", json={"category_id": 999999}
    )

    assert response.status_code == 400


def test_update_product_nonexistent_supplier_returns_400(client, make_product):
    product = make_product()

    response = client.put(
        f"/products/{product['product_id']}", json={"supplier_id": 999999}
    )

    assert response.status_code == 400


def test_update_product_not_found_returns_404(client):
    response = client.put("/products/999999", json={"quantity_in_stock": 5})

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_delete_product_success(client, make_product):
    product = make_product()

    delete_response = client.delete(f"/products/{product['product_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/products/{product['product_id']}")
    assert get_response.status_code == 404


def test_delete_product_not_found_returns_404(client):
    response = client.delete("/products/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
