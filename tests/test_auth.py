from datetime import datetime, timedelta, timezone

import jwt
import pytest

from conftest import TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME
from core.security import create_access_token, jwt_algorithm, jwt_secret


# ---------- Login ----------

def test_login_with_correct_password_returns_token(client, anon_client):
    # "client" fixture created the admin; anon_client logs in from scratch
    response = anon_client.post(
        "/auth/login", data={"username": TEST_ADMIN_USERNAME, "password": TEST_ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_returns_401(client, anon_client):
    response = anon_client.post(
        "/auth/login", data={"username": TEST_ADMIN_USERNAME, "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_login_with_unknown_user_gives_same_message_as_wrong_password(client, anon_client):
    wrong_pw = anon_client.post("/auth/login", data={"username": TEST_ADMIN_USERNAME, "password": "nope"})
    no_user = anon_client.post("/auth/login", data={"username": "ghost", "password": "nope"})
    # Same status + same message, so attackers can't tell which usernames exist
    assert wrong_pw.status_code == no_user.status_code == 401
    assert wrong_pw.json()["detail"] == no_user.json()["detail"]


def test_inactive_user_cannot_log_in(client, anon_client, make_user):
    make_user(username="sleepy", password="Sleepy-Pass-123!", is_active=False)
    response = anon_client.post("/auth/login", data={"username": "sleepy", "password": "Sleepy-Pass-123!"})
    assert response.status_code == 403


def test_me_returns_logged_in_user_without_password(client):
    response = client.get("/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == TEST_ADMIN_USERNAME
    assert "password_hash" not in body


# ---------- Protected routes ----------

PROTECTED_ROUTES = [
    "/categories/", "/suppliers/", "/products/", "/users/", "/customers/",
    "/sales/", "/sale-items/", "/payments/", "/receipts/",
]


@pytest.mark.parametrize("path", PROTECTED_ROUTES)
def test_protected_route_without_token_returns_401(anon_client, path):
    response = anon_client.get(path)
    assert response.status_code == 401, f"{path} is open to the public!"


def test_garbage_token_returns_401(anon_client):
    response = anon_client.get("/products/", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_expired_token_returns_401(client, anon_client):
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        jwt_secret, algorithm=jwt_algorithm,
    )
    response = anon_client.get("/products/", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401


def test_token_signed_with_wrong_secret_returns_401(client, anon_client):
    forged = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "attacker-guessed-secret", algorithm=jwt_algorithm,
    )
    response = anon_client.get("/products/", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401


def test_token_for_deleted_user_returns_401(anon_client):
    token = create_access_token(999999)  # valid signature, but no such user
    response = anon_client.get("/products/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_root_stays_public(anon_client):
    assert anon_client.get("/").status_code == 200