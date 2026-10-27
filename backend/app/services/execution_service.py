
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExecutionRequest(BaseModel):
    """A validated request for a supported simulated action."""

    model_config = ConfigDict(extra="forbid")

    action: Literal["prepare_quiz"]
    title: str = Field(min_length=1, max_length=200)


class ExecutionResult(BaseModel):
    """Result of a simulation; no Moodle changes are made."""

    model_config = ConfigDict(extra="forbid")

    action: str
    status: Literal["simulated"]
    message: str
    changes_made: bool


def simulate_execution(
    request: ExecutionRequest,
) -> ExecutionResult:
    """
    Simulate an approved action without connecting to Moodle.

    This function must never perform real external operations.
    """
    return ExecutionResult(
        action=request.action,
        status="simulated",
        message=(
            f"Simulation only: prepared a draft workflow "
            f"for quiz '{request.title}'. No Moodle changes were made."
        ),
        changes_made=False,
    )
