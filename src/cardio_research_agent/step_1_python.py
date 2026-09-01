"""Step 1: call the synthetic lookup using ordinary Python."""

from pprint import pprint

from cardio_research_agent.synthetic_data import lookup_synthetic_patient


def main() -> None:
    found_result = lookup_synthetic_patient("p001")
    missing_result = lookup_synthetic_patient("P999")

    print("\nFOUND PATIENT")
    pprint(found_result)

    print("\nMISSING PATIENT")
    pprint(missing_result)


if __name__ == "__main__":
    main()