"""Step 6: validate model output against its source evidence."""

import json

from langchain.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from cardio_research_agent.config import get_chat_model
from cardio_research_agent.tools import lookup_synthetic_patient
from cardio_research_agent.validation import (
    compare_summary_to_source,
    parse_model_summary,
)

PATIENT_ID = "P001"


def main() -> None:
    print("\n1. RETRIEVING SOURCE DATA")

    tool_result = lookup_synthetic_patient.invoke(
        {"patient_id": PATIENT_ID}
    )
    tool_payload = json.loads(tool_result)

    print(tool_result)

    print("\n2. GENERATING A STRUCTURED CANDIDATE")

    model = get_chat_model()

    messages = [
        SystemMessage(
            content=(
                "You extract structured fields for a research-only workflow. "
                "Use only the supplied synthetic tool result. "
                "Copy values exactly. Return one JSON object only. "
                "Do not add markdown, explanations, or additional fields."
            )
        ),
        HumanMessage(
            content=(
                "Return exactly these fields:\n"
                "- patient_id\n"
                "- synthetic\n"
                "- age\n"
                "- heart_failure_type\n"
                "- lvef_percent\n"
                "- discharge_medications\n"
                "- follow_up_days\n\n"
                f"TOOL RESULT:\n{tool_result}"
            )
        ),
    ]

    response = model.invoke(messages)
    response_text = str(response.content)

    print("\nRAW MODEL RESPONSE")
    print(response_text)

    print("\n3. RUNNING DETERMINISTIC VALIDATION")

    try:
        summary = parse_model_summary(response_text)
    except (ValueError, json.JSONDecodeError, ValidationError) as error:
        print("REQUIRES HUMAN REVIEW")
        print(f"Schema or JSON validation failed: {error}")
        return

    issues = compare_summary_to_source(summary, tool_payload)

    if issues:
        print("REQUIRES HUMAN REVIEW")
        for issue in issues:
            print(f"- {issue}")
        return

    print("PASSED AUTOMATED VALIDATION")
    print(summary.model_dump_json(indent=2))


if __name__ == "__main__":
    main()