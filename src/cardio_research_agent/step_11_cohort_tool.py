"""Step 11: run typed synthetic cohort analytics."""

import json

from cardio_research_agent.tools import (
    analyze_synthetic_cohort,
)


def main() -> None:
    print("\n1. LANGCHAIN TOOL NAME")
    print(analyze_synthetic_cohort.name)

    print("\n2. TYPED INPUT SCHEMA")
    schema = (
        analyze_synthetic_cohort
        .args_schema
        .model_json_schema()
    )

    print(
        json.dumps(
            schema,
            indent=2,
        )
    )

    print("\n3. SELECTING THE SYNTHETIC COHORT")

    result = analyze_synthetic_cohort.invoke(
        {
            "heart_failure_type": "HFrEF",
            "maximum_lvef_percent": 40,
        }
    )

    print(result)


if __name__ == "__main__":
    main()