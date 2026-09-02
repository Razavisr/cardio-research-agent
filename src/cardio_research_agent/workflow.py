"""LangGraph workflow for governed synthetic patient abstraction."""

import json
from typing import Literal, TypedDict

from langchain.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
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
    approval_decision: Literal["approve", "reject"]
    reviewer_comment: str
    released: bool


def build_workflow():
    """Build and compile the governed research workflow."""

    model = get_chat_model()

    def retrieve_patient(state: ResearchState) -> dict:
        """Retrieve the synthetic source record."""

        tool_result = lookup_synthetic_patient.invoke(
            {"patient_id": state["patient_id"]}
        )

        return {
            "tool_payload": json.loads(tool_result),
        }

    def generate_candidate(state: ResearchState) -> dict:
        """Ask the local model to produce a structured candidate."""

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
        """Validate the model output against the schema and source."""

        try:
            summary = parse_model_summary(
                state["raw_model_response"]
            )
        except (
            ValueError,
            json.JSONDecodeError,
            ValidationError,
        ) as error:
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

    def human_review(state: ResearchState) -> dict:
        """Pause the graph and request a human decision."""

        review_request = {
            "question": (
                "Do you approve this candidate summary "
                "for research use?"
            ),
            "patient_id": state["patient_id"],
            "automated_status": state["status"],
            "summary": state.get("summary"),
            "issues": state.get("issues", []),
            "allowed_decisions": ["approve", "reject"],
        }

        review_response = interrupt(review_request)

        if not isinstance(review_response, dict):
            return {
                "status": "invalid_review_decision",
                "issues": state.get("issues", [])
                + ["The human-review response must be a dictionary."],
            }

        decision = str(
            review_response.get("decision", "")
        ).strip().lower()

        comment = str(
            review_response.get("comment", "")
        ).strip()

        if decision not in {"approve", "reject"}:
            return {
                "status": "invalid_review_decision",
                "reviewer_comment": comment,
                "issues": state.get("issues", [])
                + ["The decision must be approve or reject."],
            }

        if (
            decision == "approve"
            and state["status"] != "validated"
        ):
            return {
                "approval_decision": "approve",
                "reviewer_comment": comment,
                "status": "approval_blocked",
                "issues": state.get("issues", [])
                + [
                    "Human approval was blocked because "
                    "automated validation did not pass."
                ],
            }

        final_status = (
            "approved"
            if decision == "approve"
            else "rejected"
        )

        return {
            "approval_decision": decision,
            "reviewer_comment": comment,
            "status": final_status,
        }

    def route_after_review(
        state: ResearchState,
    ) -> Literal["release_summary", "stop_workflow"]:
        """Choose the next node from the review outcome."""

        if state.get("status") == "approved":
            return "release_summary"

        return "stop_workflow"

    def release_summary(state: ResearchState) -> dict:
        """Mark an approved summary as released."""

        return {
            "released": True,
            "status": "released",
        }

    def stop_workflow(state: ResearchState) -> dict:
        """Prevent an unapproved summary from being released."""

        return {
            "released": False,
            "status": "stopped",
        }

    builder = StateGraph(ResearchState)

    builder.add_node(
        "retrieve_patient",
        retrieve_patient,
    )
    builder.add_node(
        "generate_candidate",
        generate_candidate,
    )
    builder.add_node(
        "validate_candidate",
        validate_candidate,
    )
    builder.add_node(
        "human_review",
        human_review,
    )
    builder.add_node(
        "release_summary",
        release_summary,
    )
    builder.add_node(
        "stop_workflow",
        stop_workflow,
    )

    builder.add_edge(START, "retrieve_patient")
    builder.add_edge(
        "retrieve_patient",
        "generate_candidate",
    )
    builder.add_edge(
        "generate_candidate",
        "validate_candidate",
    )
    builder.add_edge(
        "validate_candidate",
        "human_review",
    )
    builder.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "release_summary": "release_summary",
            "stop_workflow": "stop_workflow",
        },
    )

    builder.add_edge("release_summary", END)
    builder.add_edge("stop_workflow", END)

    checkpointer = InMemorySaver()

    return builder.compile(
        checkpointer=checkpointer,
    )