"""Deterministic cohort selection and KPI calculation."""

from cardio_research_agent.synthetic_data import (
    SYNTHETIC_PATIENTS,
)


BETA_BLOCKERS = {
    "bisoprolol",
    "carvedilol",
    "metoprolol",
}


def analyze_synthetic_cohort(
    heart_failure_type: str = "all",
    maximum_lvef_percent: float | None = None,
) -> dict[str, object]:
    """Select a synthetic cohort and calculate KPIs."""

    matching_records: list[
        tuple[str, dict[str, object]]
    ] = []

    for patient_id, record in SYNTHETIC_PATIENTS.items():
        record_type = str(
            record["heart_failure_type"]
        )

        record_lvef = float(
            record["lvef_percent"]
        )

        if (
            heart_failure_type != "all"
            and record_type != heart_failure_type
        ):
            continue

        if (
            maximum_lvef_percent is not None
            and record_lvef
            > maximum_lvef_percent
        ):
            continue

        matching_records.append(
            (patient_id, record)
        )

    filters = {
        "heart_failure_type": heart_failure_type,
        "maximum_lvef_percent": (
            maximum_lvef_percent
        ),
    }

    if not matching_records:
        return {
            "status": "empty_cohort",
            "synthetic": True,
            "filters": filters,
            "patient_ids": [],
            "kpis": {
                "cohort_size": 0,
            },
        }

    cohort_size = len(matching_records)

    ages = [
        int(record["age"])
        for _, record in matching_records
    ]

    lvef_values = [
        float(record["lvef_percent"])
        for _, record in matching_records
    ]

    beta_blocker_count = 0
    timely_follow_up_count = 0

    for _, record in matching_records:
        medications = {
            str(medication).lower()
            for medication in record[
                "discharge_medications"
            ]
        }

        if medications.intersection(BETA_BLOCKERS):
            beta_blocker_count += 1

        if int(record["follow_up_days"]) <= 14:
            timely_follow_up_count += 1

    return {
        "status": "completed",
        "synthetic": True,
        "filters": filters,
        "patient_ids": [
            patient_id
            for patient_id, _ in matching_records
        ],
        "kpis": {
            "cohort_size": cohort_size,
            "mean_age": round(
                sum(ages) / cohort_size,
                2,
            ),
            "mean_lvef_percent": round(
                sum(lvef_values) / cohort_size,
                2,
            ),
            "beta_blocker_coverage_percent": round(
                100
                * beta_blocker_count
                / cohort_size,
                1,
            ),
            "follow_up_within_14_days_percent": round(
                100
                * timely_follow_up_count
                / cohort_size,
                1,
            ),
        },
    }