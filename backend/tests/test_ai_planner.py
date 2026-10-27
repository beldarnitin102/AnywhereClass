
import httpx
import pytest
from unittest.mock import Mock, patch

from app.schemas.task import AIPlan
from app.services.ai_planner import PlannerError, generate_plan


def test_generate_plan_success():
    """A valid Ollama response should produce a validated AIPlan."""
    expected_plan = AIPlan(
        intent="Create a practice quiz",
        required_information=[],
        proposed_steps=[
            "Prepare quiz questions",
            "Validate the proposed quiz",
        ],
        requires_teacher_approval=True,
    )

    mock_response = Mock()
    mock_response.json.return_value = {
        "response": expected_plan.model_dump_json()
    }
    mock_response.raise_for_status.return_value = None

    with patch(
        "app.services.ai_planner.httpx.post",
        return_value=mock_response,
    ) as mock_post:
        result = generate_plan("Create a practice quiz")

    assert result.intent == "Create a practice quiz"
    assert result.proposed_steps == expected_plan.proposed_steps
    assert result.requires_teacher_approval is True
    mock_post.assert_called_once()


def test_generate_plan_when_ollama_is_unavailable():
    """A connection failure should become a controlled PlannerError."""
    with patch(
        "app.services.ai_planner.httpx.post",
        side_effect=httpx.ConnectError("Connection refused"),
    ):
        with pytest.raises(
            PlannerError,
            match="local AI planner is unavailable",
        ):
            generate_plan("Create a practice quiz")


def test_generate_plan_when_response_is_invalid():
    """Invalid model output should not be accepted as a plan."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": "This is not valid JSON"
    }
    mock_response.raise_for_status.return_value = None

    with patch(
        "app.services.ai_planner.httpx.post",
        return_value=mock_response,
    ):
        with pytest.raises(
            PlannerError,
            match="invalid plan",
        ):
            generate_plan("Create a practice quiz")


def test_generate_plan_when_response_is_empty():
    """An empty model response should produce a controlled error."""
    mock_response = Mock()
    mock_response.json.return_value = {"response": ""}
    mock_response.raise_for_status.return_value = None

    with patch(
        "app.services.ai_planner.httpx.post",
        return_value=mock_response,
    ):
        with pytest.raises(
            PlannerError,
            match="empty response",
        ):
            generate_plan("Create a practice quiz")


def test_generate_plan_when_ollama_times_out():
    """An Ollama timeout should produce a controlled PlannerError."""
    with patch(
        "app.services.ai_planner.httpx.post",
        side_effect=httpx.ReadTimeout("Request timed out"),
    ):
        with pytest.raises(
            PlannerError,
            match="local AI planner is unavailable",
        ):
            generate_plan("Create a practice quiz")
