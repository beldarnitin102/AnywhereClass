
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import task_repository
from app.schemas.task import (
    CreateTaskRequest,
    DecisionRequest,
    TaskResponse,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return task_repository.list_tasks(db)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    request: CreateTaskRequest,
    db: Session = Depends(get_db),
):
    return task_service.create_task(db, request)


@router.patch(
    "/{task_id}/decision",
    response_model=TaskResponse,
)
def decide_task(
    task_id: str,
    request: DecisionRequest,
    db: Session = Depends(get_db),
):
    return task_service.decide_task(
        db, task_id, request.decision
    )
