"""LangGraph workflow for validated synthetic patient abstraction."""

import json
from typing import TypedDict

from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import ValidationError

from cardio_research_agent.config import get_chat_model
from cardio_research_agent.tools import lookup_synthetic_patient
from cardio_research_agent.validation import (
    compare_summary_to_source,
    parse_model_summary,
)


class ResearchState(TypedDict, total=False):
    """Data carried between LangGraph nodes."""

    patient_id: str
    tool_payload: dict
    raw_model_response: str
    summary: dict
    issues: list[str]
    status: str


def build_workflow():
    """Create and compile the patient-abstraction graph."""
    model = get_chat_model()

    def retrieve_patient(state: ResearchState) -> dict:
        """Retrieve a synthetic patient through the LangChain tool."""
        tool_result = lookup_synthetic_patient.invoke(
            {"patient_id": state["patient_id"]}
        )

        return {
            "tool_payload": json.loads(tool_result),
        }

    def generate_candidate(state: ResearchState) -> dict:
        """Ask the local model for a structured candidate."""
        tool_payload = json.dumps(
            state["tool_payload"],
            indent=2,
            sort_keys=True,
        )

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
                    f"TOOL RESULT:\n{tool_payload}"
                )
            ),
        ]

        response = model.invoke(messages)

        return {
            "raw_model_response": str(response.content),
        }

    def validate_candidate(state: ResearchState) -> dict:
        """Validate schema and compare values with source evidence."""
        try:
            summary = parse_model_summary(
                state["raw_model_response"]
            )
        except (ValueError, json.JSONDecodeError, ValidationError) as error:
            return {
                "status": "review_required",
                "issues": [
                    f"Schema or JSON validation failed: {error}"
                ],
            }

        issues = compare_summary_to_source(
            summary,
            state["tool_payload"],
        )

        if issues:
            return {
                "summary": summary.model_dump(),
                "status": "review_required",
                "issues": issues,
            }

        return {
            "summary": summary.model_dump(),
            "status": "validated",
            "issues": [],
        }

    builder = StateGraph(ResearchState)

    builder.add_node("retrieve_patient", retrieve_patient)
    builder.add_node("generate_candidate", generate_candidate)
    builder.add_node("validate_candidate", validate_candidate)

    builder.add_edge(START, "retrieve_patient")
    builder.add_edge("retrieve_patient", "generate_candidate")
    builder.add_edge("generate_candidate", "validate_candidate")
    builder.add_edge("validate_candidate", END)

    return builder.compile()