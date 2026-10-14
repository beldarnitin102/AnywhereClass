
def test_create_task(client):
    response = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
    )

    assert response.status_code == 201

    task = response.json()
    assert task["command"] == "Create a practice quiz"
    assert task["status"] == "awaiting_approval"
    assert task["mode"] == "simulation"
    assert task["id"]


def test_list_tasks(client):
    client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
    )

    response = client.get("/api/v1/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_approve_task(client):
    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
    ).json()

    response = client.patch(
        f"/api/v1/tasks/{created['id']}/decision",
        json={"decision": "approve"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved_simulation"


def test_reject_task(client):
    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
    ).json()

    response = client.patch(
        f"/api/v1/tasks/{created['id']}/decision",
        json={"decision": "reject"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_invalid_decision(client):
    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
    ).json()

    response = client.patch(
        f"/api/v1/tasks/{created['id']}/decision",
        json={"decision": "maybe"},
    )

    assert response.status_code == 422


def test_missing_task_returns_404(client):
    response = client.patch(
        "/api/v1/tasks/does-not-exist/decision",
        json={"decision": "approve"},
    )

    assert response.status_code == 404


def test_cannot_review_task_twice(client):
    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
    ).json()

    url = f"/api/v1/tasks/{created['id']}/decision"

    first_response = client.patch(
        url, json={"decision": "approve"}
    )
    second_response = client.patch(
        url, json={"decision": "reject"}
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409
