
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import TaskRecord


def list_tasks(db: Session) -> list[TaskRecord]:
    statement = select(TaskRecord).order_by(
        TaskRecord.created_at.desc()
    )
    return list(db.scalars(statement).all())


def get_task(db: Session, task_id: str) -> TaskRecord | None:
    return db.get(TaskRecord, task_id)


def save_task(db: Session, task: TaskRecord) -> TaskRecord:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
