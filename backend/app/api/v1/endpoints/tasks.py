
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories import task_repository
from app.schemas.task import (
    CreateTaskRequest,
    DecisionRequest,
    TaskResponse,
)
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    return task_repository.list_tasks(db, current_user.id)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    request: CreateTaskRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    return task_service.create_task(db, request, current_user.id)


@router.patch("/{task_id}/decision", response_model=TaskResponse)
def decide_task(
    task_id: str,
    request: DecisionRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    return task_service.decide_task(
        db,
        task_id,
        request.decision,
        current_user.id,
    )
