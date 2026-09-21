"""Step 10: save an auditable workflow decision trace."""

from pathlib import Path
from pprint import pprint
from uuid import uuid4

from langgraph.types import Command

from cardio_research_agent.workflow import build_workflow


def main() -> None:
    run_id = str(uuid4())

    print("\n1. WORKFLOW RUN ID")
    print(run_id)

    print("\n2. BUILDING THE AUDITED LANGGRAPH")
    workflow = build_workflow()

    config = {
        "configurable": {
            "thread_id": run_id,
        }
    }

    print("\n3. RUNNING UNTIL HUMAN REVIEW")

    paused_result = workflow.invoke(
        {
            "patient_id": "P001",
            "run_id": run_id,
        },
        config=config,
    )

    interrupts = paused_result.get("__interrupt__", ())

    if not interrupts:
        print("\n4. HUMAN REVIEW NOT REQUIRED")
        print(
            "The candidate passed automated validation "
            "and was released."
        )
        pprint(paused_result)
        return

    print("\n4. HUMAN REVIEW REQUEST")
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

    print("\n5. RESUMING THE WORKFLOW")

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

    print("\nRELEASED")
    print(final_result["released"])

    print("\nAUDIT PATH")
    print(final_result["audit_path"])

    audit_path = Path(final_result["audit_path"])

    print("\n6. SAVED AUDIT RECORD")
    print(audit_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()