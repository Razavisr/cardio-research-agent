"""Step 8: pause and resume a LangGraph for human review."""

from pprint import pprint

from langgraph.types import Command

from cardio_research_agent.workflow import build_workflow


def main() -> None:
    print("\n1. BUILDING THE GOVERNED LANGGRAPH")
    workflow = build_workflow()

    config = {
        "configurable": {
            "thread_id": "p001-review-demo",
        }
    }

    print("\n2. RUNNING UNTIL HUMAN REVIEW")
    paused_result = workflow.invoke(
        {"patient_id": "P001"},
        config=config,
    )

    interrupts = paused_result.get("__interrupt__", ())

    if not interrupts:
        print("\nTHE WORKFLOW DID NOT PAUSE")
        pprint(paused_result)
        return

    review_request = interrupts[0].value

    print("\n3. HUMAN REVIEW REQUEST")
    pprint(review_request)

    while True:
        decision = input(
            "\nType approve or reject: "
        ).strip().lower()

        if decision in {"approve", "reject"}:
            break

        print("Please enter approve or reject.")

    comment = input(
        "Optional reviewer comment: "
    ).strip()

    print("\n4. RESUMING THE SAME LANGGRAPH RUN")

    final_result = workflow.invoke(
        Command(
            resume={
                "decision": decision,
                "comment": comment,
            }
        ),
        config=config,
    )

    print("\nFINAL STATUS")
    print(final_result["status"])

    print("\nHUMAN DECISION")
    print(final_result.get("approval_decision"))

    print("\nREVIEWER COMMENT")
    print(final_result.get("reviewer_comment"))

    print("\nFINAL SUMMARY")
    pprint(final_result.get("summary"))

    print("\nVALIDATION ISSUES")
    pprint(final_result.get("issues"))


if __name__ == "__main__":
    main()