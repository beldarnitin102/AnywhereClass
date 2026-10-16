
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import TaskRecord


def list_tasks(db: Session, owner_id: str) -> list[TaskRecord]:
    statement = (
        select(TaskRecord)
        .where(TaskRecord.owner_id == owner_id)
        .order_by(TaskRecord.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_task(
    db: Session,
    task_id: str,
    owner_id: str,
) -> TaskRecord | None:
    statement = select(TaskRecord).where(
        TaskRecord.id == task_id,
        TaskRecord.owner_id == owner_id,
    )
    return db.scalar(statement)


def save_task(db: Session, task: TaskRecord) -> TaskRecord:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
