"""Step 7: run the validated workflow as a LangGraph."""

from pprint import pprint

from cardio_research_agent.workflow import build_workflow


def main() -> None:
    print("\n1. BUILDING THE LANGGRAPH")

    workflow = build_workflow()

    print("\nGRAPH DEFINITION")
    print(workflow.get_graph().draw_mermaid())

    print("\n2. RUNNING THE LANGGRAPH")

    result = workflow.invoke(
        {
            "patient_id": "P001",
        }
    )

    print("\nFINAL STATUS")
    print(result["status"])

    print("\nVALIDATED SUMMARY")
    pprint(result.get("summary"))

    print("\nVALIDATION ISSUES")
    pprint(result.get("issues"))


if __name__ == "__main__":
    main()