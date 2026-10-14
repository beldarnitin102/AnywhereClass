
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import TaskRecord

app = FastAPI(
    title="AI Moodle Operator",
    version="0.3.0",
    description="An AI-powered platform for safely executing approved tasks.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)


# Initial development setup. We will introduce Alembic migrations
# before the schema becomes more complex or the application is deployed.
Base.metadata.create_all(bind=engine)


class CreateTaskRequest(BaseModel):
    command: str = Field(min_length=5, max_length=2000)


class DecisionRequest(BaseModel):
    decision: str


def serialize_task(task: TaskRecord) -> dict:
    return {
        "id": task.id,
        "command": task.command,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
        "plan": task.plan,
        "mode": task.mode,
    }


@app.get("/")
def root():
    return {"message": "AI Moodle Operator API is running"}


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AI Moodle Operator",
    }


@app.get("/api/tasks")
def list_tasks(db: Session = Depends(get_db)):
    statement = select(TaskRecord).order_by(
        TaskRecord.created_at.desc()
    )
    tasks = db.scalars(statement).all()

    return [serialize_task(task) for task in tasks]


@app.post("/api/tasks", status_code=201)
def create_task(
    request: CreateTaskRequest,
    db: Session = Depends(get_db),
):
    command = request.command.strip()

    if len(command) < 5:
        raise HTTPException(
            status_code=422,
            detail="Command must contain at least 5 non-space characters.",
        )

    task = TaskRecord(
        id=str(uuid4()),
        command=command,
        status="awaiting_approval",
        plan=[
            "Interpret the requested task",
            "Validate the intended operation",
            "Prepare a reviewable action plan",
        ],
        mode="simulation",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return serialize_task(task)


@app.patch("/api/tasks/{task_id}/decision")
def decide_task(
    task_id: str,
    request: DecisionRequest,
    db: Session = Depends(get_db),
):
    if request.decision not in {"approve", "reject"}:
        raise HTTPException(
            status_code=422,
            detail="Decision must be approve or reject.",
        )

    task = db.get(TaskRecord, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "awaiting_approval":
        raise HTTPException(
            status_code=409,
            detail="This task has already been reviewed.",
        )

    task.status = (
        "approved_simulation"
        if request.decision == "approve"
        else "rejected"
    )

    db.commit()
    db.refresh(task)

    return serialize_task(task)
