"""Locked gold labels for the synthetic evaluation set."""


EVALUATION_CASES = [
    {
        "patient_id": "P001",
        "expected": {
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
        },
    },
    {
        "patient_id": "P002",
        "expected": {
            "patient_id": "P002",
            "synthetic": True,
            "age": 59,
            "heart_failure_type": "HFpEF",
            "lvef_percent": 58,
            "discharge_medications": [
                "metoprolol",
                "furosemide",
            ],
            "follow_up_days": 14,
        },
    },
    {
        "patient_id": "P003",
        "expected": {
            "patient_id": "P003",
            "synthetic": True,
            "age": 67,
            "heart_failure_type": "HFrEF",
            "lvef_percent": 28,
            "discharge_medications": [
                "metoprolol",
                "sacubitril-valsartan",
                "spironolactone",
            ],
            "follow_up_days": 10,
        },
    },
]