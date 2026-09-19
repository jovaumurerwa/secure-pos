def test_create_category_success(client):
    response = client.post(
        "/categories/",
        json={"name": "Snacks", "description": "Chips and crisps", "is_active": True},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Snacks"
    assert body["description"] == "Chips and crisps"
    assert body["is_active"] is True
    assert "category_id" in body


def test_create_category_missing_required_field_returns_422(client):
    response = client.post("/categories/", json={"description": "No name given"})

    assert response.status_code == 422


def test_create_category_wrong_type_returns_422(client):
    response = client.post(
        "/categories/", json={"name": "Snacks", "is_active": "not-a-boolean-ish-string"}
    )

    assert response.status_code == 422


def test_list_categories_returns_all_created(client, make_category):
    make_category(name="Snacks")
    make_category(name="Beverages")

    response = client.get("/categories/")

    assert response.status_code == 200
    names = {c["name"] for c in response.json()}
    assert {"Snacks", "Beverages"}.issubset(names)


def test_get_category_success(client, make_category):
    category = make_category(name="Dairy")

    response = client.get(f"/categories/{category['category_id']}")

    assert response.status_code == 200
    assert response.json()["name"] == "Dairy"


def test_get_category_not_found_returns_404(client):
    response = client.get("/categories/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_update_category_success(client, make_category):
    category = make_category(name="Dairy", is_active=True)

    response = client.put(
        f"/categories/{category['category_id']}",
        json={"name": "Dairy & Eggs"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Dairy & Eggs"

    assert body["is_active"] is True


def test_update_category_not_found_returns_404(client):
    response = client.put("/categories/999999", json={"name": "Ghost"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_delete_category_success(client, make_category):
    category = make_category()

    delete_response = client.delete(f"/categories/{category['category_id']}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/categories/{category['category_id']}")
    assert get_response.status_code == 404


def test_delete_category_not_found_returns_404(client):
    response = client.delete("/categories/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"
