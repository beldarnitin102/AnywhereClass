
import jwt

from app.core.security import decode_access_token


def test_login_returns_valid_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "SecurePassphrase123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "SecurePassphrase123!",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0

    claims = decode_access_token(data["access_token"])
    assert claims["sub"]
    assert "exp" in claims


def test_wrong_password_rejected(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "SecurePassphrase123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_unknown_email_rejected(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "SecurePassphrase123!",
        },
    )

    assert response.status_code == 401


def test_invalid_token_rejected():
    try:
        decode_access_token("not-a-valid-token")
        assert False, "Expected an invalid token to be rejected"
    except jwt.InvalidTokenError:
        pass
