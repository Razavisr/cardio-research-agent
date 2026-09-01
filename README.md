# CardioResearch Agent

A research-only prototype for governed cardiology cohort discovery and evidence-backed chart abstraction using LangChain and LangGraph.

## Goal

The workflow will:

1. Find synthetic adult heart-failure admissions using structured cohort criteria.
2. Retrieve an allow-listed chart bundle.
3. Extract heart-failure type, ejection fraction, discharge medications, and follow-up interval.
4. Attach exact evidence to every extracted field.
5. Detect missing or conflicting information.
6. Pause for human review before approving results.
7. Record metadata-only audit events.

## Planned architecture

```text
START
  -> discover cohort
  -> retrieve charts
  -> abstract fields
  -> validate evidence
  -> human review
  -> finalize
  -> END