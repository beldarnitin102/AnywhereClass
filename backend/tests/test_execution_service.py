
import pytest
from pydantic import ValidationError

from app.services.execution_service import (
    ExecutionRequest,
    simulate_execution,
)


def test_simulate_prepare_quiz():
    request = ExecutionRequest(
        action="prepare_quiz",
        title="Python Practice Quiz",
    )

    result = simulate_execution(request)

    assert result.action == "prepare_quiz"
    assert result.status == "simulated"
    assert result.changes_made is False
    assert "No Moodle changes were made" in result.message


def test_reject_unsupported_action():
    with pytest.raises(ValidationError):
        ExecutionRequest(
            action="delete_course",
            title="Test",
        )


def test_reject_empty_title():
    with pytest.raises(ValidationError):
        ExecutionRequest(
            action="prepare_quiz",
            title="",
        )


def test_reject_unexpected_fields():
    with pytest.raises(ValidationError):
        ExecutionRequest(
            action="prepare_quiz",
            title="Test",
            password="example",
        )
