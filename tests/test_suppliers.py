def test_create_supplier_success(client):
    response = client.post(
        "/suppliers/",
        json={
            "company_name": "Fresh Farms Ltd",
            "contact_name": "Alice",
            "phone": "0722000000",
            "email": "alice@freshfarms.test",
            "address": "45 Farm Rd",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["company_name"] == "Fresh Farms Ltd"
    assert "supplier_id" in body


def test_create_supplier_missing_required_field_returns_422(client):
    response = client.post("/suppliers/", json={"contact_name": "No Company"})

    assert response.status_code == 422


def test_list_suppliers_returns_all_created(client, make_supplier):
    make_supplier(company_name="Fresh Farms Ltd")
    make_supplier(company_name="Global Foods Inc")

    response = client.get("/suppliers/")

    assert response.status_code == 200
    names = {s["company_name"] for s in response.json()}
    assert {"Fresh Farms Ltd", "Global Foods Inc"}.issubset(names)


def test_get_supplier_success(client, make_supplier):
    supplier = make_supplier(company_name="Fresh Farms Ltd")

    response = client.get(f"/suppliers/{supplier['supplier_id']}")

    assert response.status_code == 200
    assert response.json()["company_name"] == "Fresh Farms Ltd"


def test_get_supplier_not_found_returns_404(client):
    response = client.get("/suppliers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"


def test_update_supplier_success(client, make_supplier):
    supplier = make_supplier(company_name="Fresh Farms Ltd")

    response = client.put(
        f"/suppliers/{supplier['supplier_id']}",
        json={"company_name": "Fresh Farms Kenya Ltd"},
    )

    assert response.status_code == 200
    assert response.json()["company_name"] == "Fresh Farms Kenya Ltd"


def test_update_supplier_not_found_returns_404(client):
    response = client.put("/suppliers/999999", json={"company_name": "Ghost Co"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"


def test_delete_supplier_success(client, make_supplier):
    supplier = make_supplier()

    delete_response = client.delete(f"/suppliers/{supplier['supplier_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/suppliers/{supplier['supplier_id']}")
    assert get_response.status_code == 404


def test_delete_supplier_not_found_returns_404(client):
    response = client.delete("/suppliers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Supplier not found"
