
from tests.test_tasks import authenticated_headers


def test_user_cannot_access_another_users_task(client):
    teacher_a = authenticated_headers(
        client, "teacher-a@example.com"
    )
    teacher_b = authenticated_headers(
        client, "teacher-b@example.com"
    )

    created = client.post(
        "/api/v1/tasks",
        json={"command": "Create a practice quiz"},
        headers=teacher_a,
    )

    assert created.status_code == 201
    task_id = created.json()["id"]

    # Teacher B cannot see Teacher A's task.
    listing = client.get(
        "/api/v1/tasks",
        headers=teacher_b,
    )
    assert listing.status_code == 200
    assert all(task["id"] != task_id for task in listing.json())

    # Teacher B cannot approve Teacher A's task.
    decision = client.patch(
        f"/api/v1/tasks/{task_id}/decision",
        json={"decision": "approve"},
        headers=teacher_b,
    )
    assert decision.status_code == 404

    # Teacher A can still approve their own task.
    own_decision = client.patch(
        f"/api/v1/tasks/{task_id}/decision",
        json={"decision": "approve"},
        headers=teacher_a,
    )
    assert own_decision.status_code == 200
    assert own_decision.json()["status"] == "approved_simulation"
