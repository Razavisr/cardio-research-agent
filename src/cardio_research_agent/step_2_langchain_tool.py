"""Step 2: inspect and invoke a LangChain tool."""

import json

from cardio_research_agent.tools import lookup_synthetic_patient


def main() -> None:
    print("\nTOOL NAME")
    print(lookup_synthetic_patient.name)

    print("\nTOOL DESCRIPTION")
    print(lookup_synthetic_patient.description)

    print("\nTOOL INPUT SCHEMA")
    schema = lookup_synthetic_patient.args_schema.model_json_schema()
    print(json.dumps(schema, indent=2))

    print("\nTOOL RESULT")
    result = lookup_synthetic_patient.invoke({"patient_id": "p001"})
    print(result)


if __name__ == "__main__":
    main()