def test_create_payment_success(client, make_sale):
    sale = make_sale()

    response = client.post(
        f"/payments/sale/{sale['sale_id']}",
        json={"payment_method": "Cash", "amount": 50.00, "transaction_ref": "TXN-001"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["payment_method"] == "Cash"
    assert body["amount"] == "50.00"
    assert body["sale_id"] == sale["sale_id"]
    assert body["status"] == "Approved"
    assert "payment_id" in body


def test_create_payment_nonexistent_sale_returns_404(client):
    response = client.post(
        "/payments/sale/999999",
        json={"payment_method": "Cash", "amount": 10.00},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Sale not found"


def test_create_payment_missing_required_field_returns_422(client, make_sale):
    sale = make_sale()

    response = client.post(
        f"/payments/sale/{sale['sale_id']}", json={"payment_method": "Cash"}
    )

    assert response.status_code == 422


def test_create_payment_wrong_type_returns_422(client, make_sale):
    sale = make_sale()

    response = client.post(
        f"/payments/sale/{sale['sale_id']}",
        json={"payment_method": "Cash", "amount": "not-a-number"},
    )

    assert response.status_code == 422


def test_list_payments_includes_payments_from_created_sales(client, make_sale):
    sale = make_sale()

    response = client.get("/payments/")

    assert response.status_code == 200
    payment_ids = {p["payment_id"] for p in response.json()}
    assert sale["payments"][0]["payment_id"] in payment_ids


def test_get_payment_success(client, make_sale):
    sale = make_sale()
    payment_id = sale["payments"][0]["payment_id"]

    response = client.get(f"/payments/{payment_id}")

    assert response.status_code == 200
    assert response.json()["payment_id"] == payment_id


def test_get_payment_not_found_returns_404(client):
    response = client.get("/payments/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_update_payment_status_success(client, make_sale):
    sale = make_sale()
    payment_id = sale["payments"][0]["payment_id"]

    response = client.put(f"/payments/{payment_id}", json={"status": "Refunded"})

    assert response.status_code == 200
    assert response.json()["status"] == "Refunded"


def test_update_payment_not_found_returns_404(client):
    response = client.put("/payments/999999", json={"status": "Refunded"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_delete_payment_success(client, make_sale):
    sale = make_sale()
    payment_id = sale["payments"][0]["payment_id"]

    delete_response = client.delete(f"/payments/{payment_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/payments/{payment_id}")
    assert get_response.status_code == 404


def test_delete_payment_not_found_returns_404(client):
    response = client.delete("/payments/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"
