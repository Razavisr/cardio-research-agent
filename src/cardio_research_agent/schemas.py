"""Validated data contracts for the research workflow."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PatientSummary(BaseModel):
    """Allowed fields in a synthetic patient research summary."""

    model_config = ConfigDict(extra="forbid")

    patient_id: str
    synthetic: Literal[True]
    age: int = Field(ge=18, le=120)
    heart_failure_type: Literal["HFrEF", "HFpEF", "unknown"]
    lvef_percent: float = Field(ge=0, le=100)
    discharge_medications: list[str]
    follow_up_days: int = Field(ge=0, le=365)