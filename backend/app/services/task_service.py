
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.task import TaskRecord
from app.repositories import task_repository
from app.schemas.task import CreateTaskRequest
from app.services.ai_planner import PlannerError, generate_plan


def create_task(
    db: Session,
    request: CreateTaskRequest,
    owner_id: str,
) -> TaskRecord:
    command = request.command.strip()

    if len(command) < 5:
        raise HTTPException(
            status_code=422,
            detail="Command must contain at least 5 non-space characters.",
        )

    try:
        ai_plan = generate_plan(command)
    except PlannerError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    task = TaskRecord(
        id=str(uuid4()),
        owner_id=owner_id,
        command=command,
        status="awaiting_approval",
        plan=ai_plan.proposed_steps,
        mode="simulation",
    )

    return task_repository.save_task(db, task)


def decide_task(
    db: Session,
    task_id: str,
    decision: str,
    owner_id: str,
) -> TaskRecord:
    if decision not in {"approve", "reject"}:
        raise HTTPException(
            status_code=422,
            detail="Decision must be approve or reject.",
        )

    task = task_repository.get_task(db, task_id, owner_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    if task.status != "awaiting_approval":
        raise HTTPException(
            status_code=409,
            detail="This task has already been reviewed.",
        )

    task.status = (
        "approved_simulation" if decision == "approve" else "rejected"
    )

    return task_repository.save_task(db, task)
