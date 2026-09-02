"""LangChain tools for the research workflow."""

import json

from langchain.tools import tool

from cardio_research_agent.cohort import (
    analyze_synthetic_cohort as analyze_cohort_records,
)
from cardio_research_agent.schemas import CohortQuery
from cardio_research_agent.synthetic_data import (
    lookup_synthetic_patient as lookup_patient_record,
)


@tool
def lookup_synthetic_patient(
    patient_id: str,
) -> str:
    """Look up one synthetic patient record."""

    result = lookup_patient_record(patient_id)

    return json.dumps(
        result,
        indent=2,
        sort_keys=True,
    )


@tool(args_schema=CohortQuery)
def analyze_synthetic_cohort(
    heart_failure_type: str = "all",
    maximum_lvef_percent: float | None = None,
) -> str:
    """Select a synthetic heart-failure cohort and calculate KPIs."""

    result = analyze_cohort_records(
        heart_failure_type=heart_failure_type,
        maximum_lvef_percent=maximum_lvef_percent,
    )

    return json.dumps(
        result,
        indent=2,
        sort_keys=True,
    )