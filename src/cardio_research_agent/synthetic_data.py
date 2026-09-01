"""Small synthetic dataset used for learning and development."""

SYNTHETIC_PATIENTS: dict[str, dict[str, object]] = {
    "P001": {
        "age": 74,
        "diagnosis_group": "heart_failure",
        "heart_failure_type": "HFrEF",
        "lvef_percent": 32,
        "discharge_medications": [
            "carvedilol",
            "lisinopril",
            "furosemide",
        ],
        "follow_up_days": 7,
    },
    "P002": {
        "age": 59,
        "diagnosis_group": "heart_failure",
        "heart_failure_type": "HFpEF",
        "lvef_percent": 58,
        "discharge_medications": [
            "metoprolol",
            "furosemide",
        ],
        "follow_up_days": 14,
    },
}


def lookup_synthetic_patient(patient_id: str) -> dict[str, object]:
    """Return one synthetic patient record using a normalized identifier."""
    normalized_id = patient_id.strip().upper()
    record = SYNTHETIC_PATIENTS.get(normalized_id)

    if record is None:
        return {
            "status": "not_found",
            "patient_id": normalized_id,
        }

    return {
        "status": "found",
        "synthetic": True,
        "patient_id": normalized_id,
        "record": record,
    }