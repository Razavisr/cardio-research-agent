"""Step 9: route an approved or rejected research summary."""

from pprint import pprint

from langgraph.types import Command

from cardio_research_agent.workflow import build_workflow


def main() -> None:
    print("\n1. BUILDING THE CONDITIONAL LANGGRAPH")
    workflow = build_workflow()

    print("\nGRAPH DEFINITION")
    print(workflow.get_graph().draw_mermaid())

    config = {
        "configurable": {
            "thread_id": "p001-routing-demo",
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

    print("\n3. HUMAN REVIEW REQUEST")
    pprint(interrupts[0].value)

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

    print("\n4. RESUMING AND SELECTING A ROUTE")

    final_result = workflow.invoke(
        Command(
            resume={
                "decision": decision,
                "comment": comment,
            }
        ),
        config=config,
    )

    print("\nSELECTED ROUTE")

    if final_result["released"]:
        print("release_summary")
    else:
        print("stop_workflow")

    print("\nFINAL STATUS")
    print(final_result["status"])

    print("\nRELEASED")
    print(final_result["released"])

    print("\nHUMAN DECISION")
    print(final_result.get("approval_decision"))

    print("\nREVIEWER COMMENT")
    print(final_result.get("reviewer_comment"))

    print("\nSUMMARY")
    pprint(final_result.get("summary"))

    print("\nVALIDATION ISSUES")
    pprint(final_result.get("issues"))


if __name__ == "__main__":
    main()