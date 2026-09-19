def test_create_sale_item_nonexistent_sale_returns_404(client, make_product):
    product = make_product()

    response = client.post(
        "/sale-items/sale/999999",
        json={"product_id": product["product_id"], "quantity": 1, "line_discount": 0},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found"


def test_create_sale_item_nonexistent_product_returns_400(client, make_sale):
    sale = make_sale()

    response = client.post(
        f"/sale-items/sale/{sale['sale_id']}",
        json={"product_id": 999999, "quantity": 1, "line_discount": 0},
    )

    assert response.status_code == 400
    assert "Product" in response.json()["detail"]


def test_create_sale_item_missing_required_field_returns_422(client, make_sale):
    sale = make_sale()

    response = client.post(
        f"/sale-items/sale/{sale['sale_id']}", json={"product_id": 1}
    )

    assert response.status_code == 422


def test_list_sale_items_includes_items_from_created_sales(client, make_sale):
    sale = make_sale()

    response = client.get("/sale-items/")

    assert response.status_code == 200
    sale_item_ids = {item["sale_item_id"] for item in response.json()}
    assert sale["sale_items"][0]["sale_item_id"] in sale_item_ids


def test_get_sale_item_success(client, make_sale):
    sale = make_sale()
    sale_item_id = sale["sale_items"][0]["sale_item_id"]

    response = client.get(f"/sale-items/{sale_item_id}")

    assert response.status_code == 200
    assert response.json()["sale_item_id"] == sale_item_id
    assert response.json()["sale_id"] == sale["sale_id"]


def test_get_sale_item_not_found_returns_404(client):
    response = client.get("/sale-items/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale item not found"


def test_update_sale_item_quantity_success(client, make_sale):
    sale = make_sale()
    sale_item_id = sale["sale_items"][0]["sale_item_id"]

    response = client.put(f"/sale-items/{sale_item_id}", json={"quantity": 9})

    assert response.status_code == 200
    assert response.json()["quantity"] == 9


def test_update_sale_item_not_found_returns_404(client):
    response = client.put("/sale-items/999999", json={"quantity": 1})

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale item not found"


def test_delete_sale_item_success(client, make_sale):
    sale = make_sale()
    sale_item_id = sale["sale_items"][0]["sale_item_id"]

    delete_response = client.delete(f"/sale-items/{sale_item_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/sale-items/{sale_item_id}")
    assert get_response.status_code == 404


def test_delete_sale_item_not_found_returns_404(client):
    response = client.delete("/sale-items/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale item not found"
