
def authenticated_headers(client, email="teacher@example.com"):
    password = "SecurePassphrase123!"

    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert registered.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_task(client):
    headers = authenticated_headers(client)
    response = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["command"] == "Create a practice quiz"
    assert data["status"] == "awaiting_approval"


def test_list_tasks(client):
    headers = authenticated_headers(client)

    client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
        headers=headers,
    )

    response = client.get("/api/v1/tasks", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_approve_task(client):
    headers = authenticated_headers(client)
    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/v1/tasks/{created['id']}/decision",
        json={"decision": "approve"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved_simulation"


def test_reject_task(client):
    headers = authenticated_headers(client)
    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/v1/tasks/{created['id']}/decision",
        json={"decision": "reject"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_invalid_decision(client):
    headers = authenticated_headers(client)
    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/v1/tasks/{created['id']}/decision",
        json={"decision": "maybe"},
        headers=headers,
    )

    assert response.status_code == 422


def test_missing_task_returns_404(client):
    headers = authenticated_headers(client)

    response = client.patch(
        "/api/v1/tasks/does-not-exist/decision",
        json={"decision": "approve"},
        headers=headers,
    )

    assert response.status_code == 404


def test_cannot_review_task_twice(client):
    headers = authenticated_headers(client)
    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
        headers=headers,
    ).json()

    url = f"/api/v1/tasks/{created['id']}/decision"

    first = client.patch(
        url,
        json={"decision": "approve"},
        headers=headers,
    )
    second = client.patch(
        url,
        json={"decision": "reject"},
        headers=headers,
    )

    assert first.status_code == 200
    assert second.status_code == 409
