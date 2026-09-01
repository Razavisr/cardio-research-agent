"""Step 3: call a local Hugging Face model through LangChain."""

from langchain.messages import HumanMessage, SystemMessage

from cardio_research_agent.config import get_chat_model


def main() -> None:
    print("Loading the local model. The first run downloads its files...")

    model = get_chat_model()

    messages = [
        SystemMessage(
            content=(
                "You support clinical research education. "
                "Do not diagnose patients or recommend treatment."
            )
        ),
        HumanMessage(
            content=(
                "In two short sentences, explain how left ventricular "
                "ejection fraction can be represented as a numeric "
                "research variable."
            )
        ),
    ]

    response = model.invoke(messages)

    print("\nMODEL RESPONSE")
    print(response.content)


if __name__ == "__main__":
    main()