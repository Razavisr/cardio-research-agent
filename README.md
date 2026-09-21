# CardioResearch Agent

CardioResearch Agent is a small, research-only prototype I built to explore how an LLM-based clinical abstraction workflow can be made traceable and reviewable.

The project uses synthetic heart-failure records. It retrieves a patient record, asks a local language model to produce a structured summary, and checks every output field against the source. Summaries that pass validation are released automatically in this synthetic demonstration. Failed summaries pause for human review and cannot be released unless automated validation succeeds.

It also includes a separate cohort-analysis tool for selecting synthetic patients and calculating simple research KPIs.

This is a learning and demonstration project. It is not intended for diagnosis, treatment, clinical decision-making, or use with real patient data.

For intended use, evaluation scope, and limitations, see [MODEL_CARD.md](MODEL_CARD.md).

## Why I built it

A language model can turn a patient record into a readable summary, but a convincing answer is not necessarily a correct one. During an early version of this project, the model added dates and follow-up details that were not present in the source record.

That failure shaped the rest of the design. I added a strict output schema, deterministic comparison with the source, conditional human review, explicit release rules, and a saved audit record.

The model generates a candidate. Regular Python code decides whether that candidate is valid and whether it is allowed to continue.

## Workflow

```text
START
  |
  v
retrieve_patient
  |
  v
generate_candidate
  |
  v
validate_candidate
  |
  +---- validated --------> release_summary --------+
  |                                                |
  +---- review_required --> human_review            |
                              |                     |
                              v                     |
                         stop_workflow -------------+
                                                   |
                                                   v
                                              record_audit
                                                   |
                                                   v
                                                  END
```

The workflow follows these steps:

1. A typed LangChain tool retrieves one synthetic patient record.
2. A local Hugging Face model produces a structured candidate summary.
3. Pydantic checks the allowed fields, types, and numeric ranges.
4. Deterministic validation compares every field with the source record.
5. A validated summary follows the automatic release path.
6. A failed summary pauses for human review. The reviewer can inspect and document the failure, but cannot release an output that failed validation.
7. The final evidence, validation result, route, and optional review decision are written to a local audit file.

## Main components

### LangChain

LangChain provides the tool interface, message objects, and the adapter around the local Hugging Face text-generation pipeline.

The project currently exposes two tools:

- `lookup_synthetic_patient` retrieves one synthetic patient.
- `analyze_synthetic_cohort` applies typed cohort filters and calculates KPIs.

### LangGraph

LangGraph controls the workflow state and execution order. It is responsible for:

- moving data between nodes;
- pausing for human review;
- saving the paused state in an in-memory checkpoint;
- resuming with the reviewer’s decision;
- routing approved and rejected results to different nodes.

### Pydantic and deterministic validation

The generated summary must follow a strict Pydantic schema. Additional fields are forbidden, and numeric values have defined ranges.

Passing the schema is not enough. The workflow also compares each generated value with the retrieved source record. A correctly formatted but incorrect value therefore fails validation.

### Local language model

The example configuration uses:

```text
HuggingFaceTB/SmolLM2-1.7B-Instruct
```

The model runs locally through `transformers` and `langchain-huggingface`. No paid LLM API is required.

## Setup

The project uses Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
cp .env.example .env
```

The example environment configuration is:

```dotenv
HF_MODEL_ID=HuggingFaceTB/SmolLM2-1.7B-Instruct
HF_DEVICE=cpu
```

The model is downloaded from Hugging Face the first time it is used. Later runs use the local cache.

## Run the governed abstraction workflow

```bash
python -m cardio_research_agent.step_10_audit_trace
```

If the candidate passes automated validation, the workflow completes without pausing and follows the release route. If validation fails, LangGraph pauses and presents the detected issues to a human reviewer.

A failed candidate cannot be released in the current prototype. A rejection or blocked approval follows the stop route, and both release and stop outcomes are recorded in the audit file.

The final audit record is saved under:

```text
artifacts/audit/
```

This directory is ignored by Git.

## Run the cohort tool

```bash
python -m cardio_research_agent.step_11_cohort_tool
```

The example query selects synthetic HFrEF records with an LVEF no greater than 40%.

The resulting cohort contains four patients:

```text
P001, P003, P004, P006
```

| KPI | Result |
|---|---:|
| Cohort size | 4 |
| Mean age | 73.0 |
| Mean LVEF | 33.25% |
| Beta-blocker coverage | 75.0% |
| Follow-up within 14 days | 75.0% |

These are illustrative research KPIs calculated from synthetic data. They are not validated clinical quality measures or treatment recommendations.

The calculations are performed by deterministic Python rather than the language model. This makes the cohort membership and reported values reproducible.

## Run the evaluation

```bash
python -m cardio_research_agent.step_12_evaluation
```

The evaluation runs the automated workflow on three locked synthetic cases and stops before human approval.

The current local run produced:

| Metric | Result |
|---|---:|
| Evaluation cases | 3 |
| Evaluated fields | 21 |
| JSON parse success | 100.0% |
| Overall field accuracy | 100.0% |
| Exact-match accuracy | 100.0% |
| Automated validation pass rate | 100.0% |
| Cases with unsupported fields | 0.0% |

All seven evaluated fields achieved 100% accuracy on these three cases:

- patient ID;
- synthetic-data flag;
- age;
- heart-failure type;
- LVEF;
- discharge medications;
- follow-up interval.

These results show that the workflow and evaluation harness behave correctly on a small, controlled extraction task. They do not establish clinical accuracy, performance on real notes, or generalization to other datasets.

## Audit record

The final audit file includes:

- a unique run ID and UTC timestamp;
- the retrieved synthetic source;
- the raw model response;
- the validated summary;
- validation issues;
- the reviewer’s decision and comment when review occurred;
- the selected release outcome.

A production system handling clinical data would need encrypted storage, access controls, retention rules, durable checkpointing, and policies governing what can be logged. The current local JSON record is suitable only for this synthetic demonstration.

## Project structure

```text
src/cardio_research_agent/
├── audit.py                 # Writes the final decision trace
├── cohort.py                # Selects cohorts and calculates KPIs
├── config.py                # Loads the local Hugging Face model
├── evaluation_data.py       # Locked synthetic evaluation labels
├── schemas.py               # Pydantic input and output contracts
├── synthetic_data.py        # Synthetic patient records
├── tools.py                 # LangChain tools
├── validation.py            # Schema parsing and source comparison
├── workflow.py              # LangGraph workflow
├── step_10_audit_trace.py   # Full governed workflow demonstration
├── step_11_cohort_tool.py   # Cohort analytics demonstration
└── step_12_evaluation.py    # Labeled evaluation runner
```

The earlier numbered files remain in the repository to show how the project developed from a regular Python function into a governed LangGraph workflow.

## Current limitations

- The dataset contains only six synthetic patients.
- The evaluation set contains only three straightforward cases.
- The input is already structured; the project does not yet process clinical notes or ECG signals.
- Cohort filters and KPIs are simplified for demonstration.
- The checkpoint is stored in memory and is lost when the process ends.
- Audit files are stored locally and are not encrypted.
- The project has not been clinically validated.
- It is not connected to MIMIC-IV, OMOP, an EHR, or a production research environment.

## Possible next steps

If I continue the project, the most useful extensions would be:

- a larger, independently labeled evaluation set;
- an adapter for approved MIMIC-IV data without committing patient data to Git;
- durable checkpoint and audit storage;
- field-level provenance from clinical text;
- access controls and privacy-aware logging;
- monitoring for extraction failures and changes in model behavior.

For now, the repository focuses on the core problem: using an LLM inside a workflow where its output is constrained, checked against evidence, reviewed by a person, and recorded.