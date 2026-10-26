
import json
import os

import httpx

from app.schemas.task import AIPlan


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")


class PlannerError(Exception):
    """Raised when the AI planner cannot produce a valid plan."""


def generate_plan(command: str) -> AIPlan:
    """Generate and validate a task plan using local Ollama."""

    prompt = f"""
You are the planning component of a Moodle task-management system.

Create a proposed plan for this teacher request:
{json.dumps(command)}

Rules:
- Interpret the teacher's request without executing it.
- Identify missing information instead of inventing details.
- Propose clear, short workflow steps.
- Never claim that a Moodle action has been performed.
- Teacher approval is always required.
- Return only data matching the supplied JSON schema.
"""

    try:
        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": AIPlan.model_json_schema(),
                "think": False,
                "options": {"temperature": 0.2},
            },
            timeout=120.0,
        )
        response.raise_for_status()

        payload = response.json()
        raw_output = payload.get("response")

        if not isinstance(raw_output, str) or not raw_output.strip():
            raise PlannerError("The AI model returned an empty response.")

        plan = AIPlan.model_validate_json(raw_output)

        # Enforce our application policy independently of the model.
        plan.requires_teacher_approval = True

        return plan

    except PlannerError:
        raise
    except httpx.HTTPError as exc:
        raise PlannerError(
            "The local AI planner is unavailable. Please try again."
        ) from exc
    except (ValueError, TypeError) as exc:
        raise PlannerError(
            "The AI planner returned an invalid plan. Please try again."
        ) from exc
