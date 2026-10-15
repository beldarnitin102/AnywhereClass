
from app.models.user import User


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teacher@example.com",
            "password": "SecurePassphrase123!",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "teacher@example.com"
    assert "password_hash" not in data
    assert "password" not in data


def test_password_is_hashed(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "teacher@example.com",
            "password": "SecurePassphrase123!",
        },
    )

    from app.db.session import get_db
    from app.main import app

    db_override = app.dependency_overrides[get_db]
    db = next(db_override())

    try:
        user = db.query(User).filter_by(
            email="teacher@example.com"
        ).first()

        assert user is not None
        assert user.password_hash != "SecurePassphrase123!"
        assert user.password_hash.startswith("$argon2")
    finally:
        db.close()


def test_duplicate_email_rejected(client):
    payload = {
        "email": "teacher@example.com",
        "password": "SecurePassphrase123!",
    }

    first = client.post("/api/v1/auth/register", json=payload)
    second = client.post("/api/v1/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_short_password_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "teacher@example.com",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_invalid_email_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "SecurePassphrase123!",
        },
    )

    assert response.status_code == 422
