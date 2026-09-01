"""LangChain tools available to the research workflow."""

import json

from langchain.tools import tool

from cardio_research_agent.synthetic_data import (
    lookup_synthetic_patient as lookup_patient_record,
)


@tool
def lookup_synthetic_patient(patient_id: str) -> str:
    """Look up one synthetic patient record for a cardiology research task."""
    result = lookup_patient_record(patient_id)
    return json.dumps(result, indent=2, sort_keys=True)