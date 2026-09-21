"""Step 12: evaluate automated abstraction and validation."""

import json
from uuid import uuid4

from cardio_research_agent.evaluation_data import (
    EVALUATION_CASES,
)
from cardio_research_agent.workflow import build_workflow


EXPECTED_FIELDS = (
    "patient_id",
    "synthetic",
    "age",
    "heart_failure_type",
    "lvef_percent",
    "discharge_medications",
    "follow_up_days",
)


def extract_json_object(
    response_text: str,
) -> dict:
    """Extract one JSON object from a model response."""

    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "No JSON object found in model response."
        )

    candidate = json.loads(
        response_text[start : end + 1]
    )

    if not isinstance(candidate, dict):
        raise ValueError(
            "The model output is not a JSON object."
        )

    return candidate


def percentage(
    numerator: int,
    denominator: int,
) -> float:
    """Calculate a rounded percentage."""

    if denominator == 0:
        return 0.0

    return round(
        100 * numerator / denominator,
        1,
    )


def main() -> None:
    print("\n1. BUILDING THE EVALUATION WORKFLOW")
    workflow = build_workflow()

    field_correct_counts = {
        field_name: 0
        for field_name in EXPECTED_FIELDS
    }

    parse_success_count = 0
    validation_pass_count = 0
    exact_match_count = 0
    unsupported_field_case_count = 0

    case_results = []

    for case in EVALUATION_CASES:
        patient_id = case["patient_id"]
        expected = case["expected"]
        run_id = f"evaluation-{uuid4()}"

        print(f"\n2. EVALUATING {patient_id}")

        config = {
            "configurable": {
                "thread_id": run_id,
            }
        }

        graph_result = workflow.invoke(
            {
                "patient_id": patient_id,
                "run_id": run_id,
            },
            config=config,
        )

        raw_response = graph_result[
            "raw_model_response"
        ]

        parse_succeeded = False
        candidate = {}
        parse_error = None

        try:
            candidate = extract_json_object(
                raw_response
            )
            parse_succeeded = True
            parse_success_count += 1
        except (
            ValueError,
            json.JSONDecodeError,
        ) as error:
            parse_error = str(error)

        candidate_fields = set(candidate)
        allowed_fields = set(EXPECTED_FIELDS)

        unsupported_fields = sorted(
            candidate_fields - allowed_fields
        )

        if unsupported_fields:
            unsupported_field_case_count += 1

        field_results = {}

        for field_name in EXPECTED_FIELDS:
            is_correct = (
                parse_succeeded
                and candidate.get(field_name)
                == expected[field_name]
            )

            field_results[field_name] = is_correct

            if is_correct:
                field_correct_counts[field_name] += 1

        all_fields_correct = all(
            field_results.values()
        )

        exact_match = (
            parse_succeeded
            and all_fields_correct
            and not unsupported_fields
        )

        if exact_match:
            exact_match_count += 1

        validation_passed = (
            graph_result.get("validation_status")
            == "validated"
        )

        if validation_passed:
            validation_pass_count += 1

        case_result = {
            "patient_id": patient_id,
            "parse_succeeded": parse_succeeded,
            "parse_error": parse_error,
            "field_results": field_results,
            "unsupported_fields": unsupported_fields,
            "exact_match": exact_match,
            "validation_passed": validation_passed,
            "validation_issues": graph_result.get(
                "issues",
                [],
            ),
            "raw_model_response": raw_response,
        }

        case_results.append(case_result)

        print(
            json.dumps(
                case_result,
                indent=2,
                sort_keys=True,
            )
        )

    case_count = len(EVALUATION_CASES)
    total_field_checks = (
        case_count * len(EXPECTED_FIELDS)
    )
    total_correct_fields = sum(
        field_correct_counts.values()
    )

    per_field_accuracy = {
        field_name: percentage(
            correct_count,
            case_count,
        )
        for field_name, correct_count
        in field_correct_counts.items()
    }

    metrics = {
        "case_count": case_count,
        "parse_success_rate_percent": percentage(
            parse_success_count,
            case_count,
        ),
        "validation_pass_rate_percent": percentage(
            validation_pass_count,
            case_count,
        ),
        "exact_match_rate_percent": percentage(
            exact_match_count,
            case_count,
        ),
        "overall_field_accuracy_percent": percentage(
            total_correct_fields,
            total_field_checks,
        ),
        "unsupported_field_case_rate_percent": (
            percentage(
                unsupported_field_case_count,
                case_count,
            )
        ),
        "per_field_accuracy_percent": (
            per_field_accuracy
        ),
    }

    print("\n3. FINAL EVALUATION METRICS")
    print(
        json.dumps(
            metrics,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()