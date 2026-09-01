"""Step 5: demonstrate deterministic Pydantic validation."""

from pydantic import ValidationError

from cardio_research_agent.schemas import PatientSummary

VALID_CANDIDATE = {
    "patient_id": "P001",
    "synthetic": True,
    "age": 74,
    "heart_failure_type": "HFrEF",
    "lvef_percent": 32,
    "discharge_medications": [
        "carvedilol",
        "lisinopril",
        "furosemide",
    ],
    "follow_up_days": 7,
}

INVALID_CANDIDATE = {
    **VALID_CANDIDATE,
    "discharge_date": "2022-01-01",
    "follow_up_date": "2022-01-08",
    "follow_up_type": "Routine",
}


def main() -> None:
    print("\n1. VALID CANDIDATE")

    valid_summary = PatientSummary.model_validate(VALID_CANDIDATE)
    print(valid_summary.model_dump_json(indent=2))

    print("\n2. INVALID CANDIDATE")

    try:
        PatientSummary.model_validate(INVALID_CANDIDATE)
    except ValidationError as error:
        print("REJECTED BY PYDANTIC")
        print(error)


if __name__ == "__main__":
    main()