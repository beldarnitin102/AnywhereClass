
from unittest.mock import patch

from app.schemas.task import AIPlan

from app.services.ai_planner import PlannerError
from unittest.mock import patch

from app.services.execution_service import ExecutionResult

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


def fake_plan(command: str):
    return AIPlan(
        intent="Create a practice quiz",
        required_information=[],
        proposed_steps=[
            "Prepare quiz questions",
            "Validate the proposed quiz",
        ],
        requires_teacher_approval=True,
    )


def test_create_task(client):
    headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a practice quiz"},
            headers=headers,
        )

    assert response.status_code == 201
    data = response.json()
    assert data["command"] == "Create a practice quiz"
    assert data["status"] == "awaiting_approval"
    assert data["plan"] == [
    "Prepare quiz questions",
    "Validate the proposed quiz",]

def test_list_tasks(client):
    headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        created = client.post(
            "/api/v1/tasks",
            json={"command": "Create a practice quiz"},
            headers=headers,
        )
        assert created.status_code == 201

    response = client.get("/api/v1/tasks", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_approve_task(client):
    headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        created_response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a practice quiz"},
            headers=headers,
        )

    assert created_response.status_code == 201
    created = created_response.json()

    response = client.patch(
        f"/api/v1/tasks/{created['id']}/decision",
        json={"decision": "approve"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved_simulation"


def test_reject_task(client):
    headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        created_response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a practice quiz"},
            headers=headers,
        )

    assert created_response.status_code == 201
    created = created_response.json()

    response = client.patch(
        f"/api/v1/tasks/{created['id']}/decision",
        json={"decision": "reject"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_invalid_decision(client):
    headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        created_response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a practice quiz"},
            headers=headers,
        )

    assert created_response.status_code == 201
    created = created_response.json()

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

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        created_response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a practice quiz"},
            headers=headers,
        )

    assert created_response.status_code == 201
    created = created_response.json()

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



def test_create_task_when_ai_planner_is_unavailable(client):
    headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=PlannerError(
            "The local AI planner is unavailable. Please try again."
        ),
    ):
        response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a practice quiz"},
            headers=headers,
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The local AI planner is unavailable. Please try again."
    )



def test_execute_approved_task_returns_simulation(client):
    headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        create_response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a Python practice quiz"},
            headers=headers,
        )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    approve_response = client.patch(
        f"/api/v1/tasks/{task_id}/decision",
        json={"decision": "approve"},
        headers=headers,
    )
    assert approve_response.status_code == 200

    with patch(
        "app.services.task_service.simulate_execution",
        return_value=ExecutionResult(
            action="prepare_quiz",
            status="simulated",
            message="Simulation only. No Moodle changes were made.",
            changes_made=False,
        ),
    ) as mock_execute:
        response = client.post(
            f"/api/v1/tasks/{task_id}/execute",
            headers=headers,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "simulated"
    assert response.json()["changes_made"] is False
    mock_execute.assert_called_once()


def test_execute_unapproved_task_is_rejected(client):
    headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        create_response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a Python practice quiz"},
            headers=headers,
        )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/tasks/{task_id}/execute",
        headers=headers,
    )

    assert response.status_code == 409


def test_execute_task_owned_by_another_user_is_hidden(client):
    owner_headers = authenticated_headers(client)

    with patch(
        "app.services.task_service.generate_plan",
        side_effect=fake_plan,
    ):
        create_response = client.post(
            "/api/v1/tasks",
            json={"command": "Create a Python practice quiz"},
            headers=owner_headers,
        )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    approve_response = client.patch(
        f"/api/v1/tasks/{task_id}/decision",
        json={"decision": "approve"},
        headers=owner_headers,
    )
    assert approve_response.status_code == 200

    other_user_headers = authenticated_headers(
    client,
    email="another-teacher@example.com",
)

    response = client.post(
        f"/api/v1/tasks/{task_id}/execute",
        headers=other_user_headers,
    )

    assert response.status_code == 404
