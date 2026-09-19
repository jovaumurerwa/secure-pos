import pytest

from core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_return_plain_text():
    hashed = hash_password("my-secret-password")

    assert hashed != "my-secret-password"
    assert len(hashed) > 0


def test_verify_password_success_for_correct_password():
    hashed = hash_password("my-secret-password")

    assert verify_password("my-secret-password", hashed) is True


def test_verify_password_fails_for_incorrect_password():
    hashed = hash_password("my-secret-password")

    assert verify_password("wrong-password", hashed) is False


def test_hashing_same_password_twice_gives_different_hashes():
    first = hash_password("my-secret-password")
    second = hash_password("my-secret-password")

    assert first != second
    assert verify_password("my-secret-password", first) is True
    assert verify_password("my-secret-password", second) is True


def test_create_and_decode_access_token_round_trip():
    token = create_access_token(user_id=42)
    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert "exp" in payload


def test_decode_access_token_rejects_garbage_token():
    with pytest.raises(Exception):
        decode_access_token("this-is-not-a-valid-jwt")
