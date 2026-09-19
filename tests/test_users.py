import pytest


def test_create_user_success(client):
    response = client.post(
        "/users/",
        json={
            "full_name": "Cashier One",
            "username": "cashier_a",
            "role": "Cashier",
            "email": "cashier_a@pos.test",
            "is_active": True,
            "password": "supersecret123",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "cashier_a"
    assert body["role"] == "Cashier"
    assert "user_id" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_create_user_missing_required_field_returns_422(client):
    response = client.post(
        "/users/",
        json={"full_name": "No Password", "username": "nopass", "role": "Cashier"},
    )

    assert response.status_code == 422


def test_create_user_duplicate_username_raises_integrity_error(client, make_user):
    from sqlalchemy.exc import IntegrityError

    make_user(username="cashier_dup")

    with pytest.raises(IntegrityError):
        client.post(
            "/users/",
            json={
                "full_name": "Another Cashier",
                "username": "cashier_dup",
                "role": "Cashier",
                "password": "anotherpass123",
            },
        )


def test_list_users_returns_all_created(client, make_user):
    make_user(username="cashier_list_1")
    make_user(username="cashier_list_2")

    response = client.get("/users/")

    assert response.status_code == 200
    usernames = {u["username"] for u in response.json()}
    assert {"cashier_list_1", "cashier_list_2"}.issubset(usernames)


def test_get_user_success(client, make_user):
    user = make_user(username="cashier_get")

    response = client.get(f"/users/{user['user_id']}")

    assert response.status_code == 200
    assert response.json()["username"] == "cashier_get"


def test_get_user_not_found_returns_404(client):
    response = client.get("/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user_success(client, make_user):
    user = make_user(full_name="Original Name")

    response = client.put(
        f"/users/{user['user_id']}", json={"full_name": "Updated Name"}
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


def test_update_user_password_is_rehashed_and_not_exposed(client, make_user):
    user = make_user()

    response = client.put(
        f"/users/{user['user_id']}", json={"password": "brand-new-password"}
    )

    assert response.status_code == 200
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_update_user_not_found_returns_404(client):
    response = client.put("/users/999999", json={"full_name": "Ghost"})

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_success(client, make_user):
    user = make_user()

    delete_response = client.delete(f"/users/{user['user_id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/users/{user['user_id']}")
    assert get_response.status_code == 404


def test_delete_user_not_found_returns_404(client):
    response = client.delete("/users/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
