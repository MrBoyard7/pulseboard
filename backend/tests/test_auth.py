"""Tests for the login flow and token-based identity resolution."""
from tests.conftest import auth_headers


def test_login_succeeds_with_valid_credentials(client, admin_user):
    response = client.post(
        "/api/auth/login", json={"email": admin_user.email, "password": "password123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_fails_with_wrong_password(client, admin_user):
    response = client.post(
        "/api/auth/login", json={"email": admin_user.email, "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_me_endpoint_returns_current_user(client, admin_user):
    headers = auth_headers(client, admin_user.email)
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == admin_user.email


def test_protected_endpoint_rejects_missing_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
