
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateTaskRequest(BaseModel):
    command: str = Field(min_length=5, max_length=2000)


class DecisionRequest(BaseModel):
    decision: str


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    command: str
    status: str
    created_at: datetime
    plan: list[str]
    mode: str
