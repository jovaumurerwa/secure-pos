def test_create_customer_success(client):
    response = client.post(
        "/customers/",
        json={
            "full_name": "Grace Wanjiru",
            "phone": "0733000000",
            "email": "grace@shopper.test",
            "loyalty_points": 10,
            "is_walk_in": False,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["full_name"] == "Grace Wanjiru"
    assert body["loyalty_points"] == 10
    assert "customer_id" in body
    assert "created_at" in body


def test_create_customer_defaults_are_applied(client):
    response = client.post("/customers/", json={"full_name": "Walk In Shopper"})

    assert response.status_code == 201
    body = response.json()
    assert body["loyalty_points"] == 0
    assert body["is_walk_in"] is False


def test_create_customer_missing_required_field_returns_422(client):
    response = client.post("/customers/", json={"phone": "0733000000"})

    assert response.status_code == 422


def test_list_customers_returns_all_created(client, make_customer):
    make_customer(full_name="Grace Wanjiru")
    make_customer(full_name="Peter Otieno")

    response = client.get("/customers/")

    assert response.status_code == 200
    names = {c["full_name"] for c in response.json()}
    assert {"Grace Wanjiru", "Peter Otieno"}.issubset(names)


def test_get_customer_success(client, make_customer):
    customer = make_customer(full_name="Grace Wanjiru")

    response = client.get(f"/customers/{customer['customer_id']}")

    assert response.status_code == 200
    assert response.json()["full_name"] == "Grace Wanjiru"


def test_get_customer_not_found_returns_404(client):
    response = client.get("/customers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_update_customer_success(client, make_customer):
    customer = make_customer(loyalty_points=10)

    response = client.put(
        f"/customers/{customer['customer_id']}",
        json={"loyalty_points": 25},
    )

    assert response.status_code == 200
    assert response.json()["loyalty_points"] == 25


def test_update_customer_not_found_returns_404(client):
    response = client.put("/customers/999999", json={"loyalty_points": 5})

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"


def test_delete_customer_success(client, make_customer):
    customer = make_customer()

    delete_response = client.delete(f"/customers/{customer['customer_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/customers/{customer['customer_id']}")
    assert get_response.status_code == 404


def test_delete_customer_not_found_returns_404(client):
    response = client.delete("/customers/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Customer not found"
