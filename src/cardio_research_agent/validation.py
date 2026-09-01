"""Deterministic validation for model-generated summaries."""

import json

from cardio_research_agent.schemas import PatientSummary


def parse_model_summary(response_text: str) -> PatientSummary:
    """Extract and validate one JSON object from a model response."""
    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("The model response does not contain a JSON object.")

    json_text = response_text[start : end + 1]
    candidate = json.loads(json_text)

    return PatientSummary.model_validate(candidate)


def compare_summary_to_source(
    summary: PatientSummary,
    tool_payload: dict,
) -> list[str]:
    """Compare every generated value with the deterministic tool result."""
    if tool_payload.get("status") != "found":
        return ["The source patient record was not found."]

    record = tool_payload["record"]

    expected = {
        "patient_id": tool_payload["patient_id"],
        "synthetic": tool_payload["synthetic"],
        "age": record["age"],
        "heart_failure_type": record["heart_failure_type"],
        "lvef_percent": record["lvef_percent"],
        "discharge_medications": record["discharge_medications"],
        "follow_up_days": record["follow_up_days"],
    }

    actual = summary.model_dump()
    issues: list[str] = []

    for field_name, expected_value in expected.items():
        actual_value = actual[field_name]

        if actual_value != expected_value:
            issues.append(
                f"{field_name}: expected {expected_value!r}, "
                f"received {actual_value!r}"
            )

    return issues