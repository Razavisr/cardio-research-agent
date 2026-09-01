"""Step 4: unvalidated baseline combining a tool with a local model."""

from langchain.messages import HumanMessage, SystemMessage

from cardio_research_agent.config import get_chat_model
from cardio_research_agent.tools import lookup_synthetic_patient

PATIENT_ID = "P001"


def main() -> None:
    print("\n1. CALLING THE LANGCHAIN TOOL")

    tool_result = lookup_synthetic_patient.invoke(
        {"patient_id": PATIENT_ID}
    )

    print(tool_result)

    print("\n2. LOADING THE LOCAL LANGUAGE MODEL")

    model = get_chat_model()

    messages = [
        SystemMessage(
            content=(
                "You support a research-only cardiology workflow. "
                "Use only the supplied synthetic tool result. "
                "Do not diagnose, recommend treatment, or invent facts. "
                "Clearly state that the record is synthetic."
            )
        ),
        HumanMessage(
            content=(
                "Summarize the following tool result. Include only the "
                "patient ID, age, heart-failure type, LVEF, discharge "
                "medications, and follow-up interval.\n\n"
                f"TOOL RESULT:\n{tool_result}"
            )
        ),
    ]

    print("\n3. ASKING THE MODEL TO SUMMARIZE THE TOOL RESULT")

    response = model.invoke(messages)

    print("\nMODEL RESPONSE")
    print(response.content)


if __name__ == "__main__":
    main()