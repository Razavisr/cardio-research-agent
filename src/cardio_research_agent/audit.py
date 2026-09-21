"""Audit-trail utilities for synthetic workflow runs."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_DIRECTORY = PROJECT_ROOT / "artifacts" / "audit"


def write_audit_record(
    state: dict[str, Any],
) -> Path:
    """Write one complete decision trace for a workflow run."""

    audit_directory = DEFAULT_AUDIT_DIRECTORY
    audit_directory.mkdir(parents=True, exist_ok=True)

    run_id = str(state["run_id"])
    summary = state.get("summary") or {}

    audit_record = {
        "event_type": "patient_summary_workflow",
        "workflow_version": "0.1.0",
        "run_id": run_id,
        "recorded_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "patient_id": state.get("patient_id"),
        "synthetic": summary.get("synthetic"),
        "tool_payload": state.get("tool_payload"),
        "raw_model_response": state.get(
            "raw_model_response"
        ),
        "validated_summary": summary,
        "validation_status": state.get(
            "validation_status"
        ),
        "validation_issues": state.get("issues", []),
        "approval_decision": state.get(
            "approval_decision"
        ),
        "reviewer_comment": state.get(
            "reviewer_comment"
        ),
        "released": state.get("released", False),
        "final_status": state.get("status"),
    }

    audit_path = audit_directory / f"{run_id}.json"

    audit_path.write_text(
        json.dumps(
            audit_record,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return audit_path