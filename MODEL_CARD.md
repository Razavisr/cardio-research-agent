# Model Card: CardioResearch Agent

## Overview

CardioResearch Agent is a research-only prototype for structured abstraction and cohort analysis over synthetic heart-failure records.

The system combines a local language model with deterministic validation, human review, conditional release rules, and audit logging. It was built to demonstrate how an LLM can be used inside a controlled research workflow without allowing the model to make final release decisions.

This card describes the complete workflow, not just the underlying language model.

## Version

- Project version: 0.1.0
- Language model: `HuggingFaceTB/SmolLM2-1.7B-Instruct`
- Inference: local CPU
- Decoding: deterministic generation with sampling disabled
- Data: synthetic heart-failure records only

The model is used through `transformers`, `langchain-huggingface`, and LangChain. It has not been fine-tuned for this project.

## Intended use

The current system is intended for:

- learning LangChain and LangGraph;
- demonstrating structured research-data abstraction;
- testing validation and human-review patterns;
- calculating simple cohort-level KPIs from synthetic records;
- discussing governance requirements for clinical research AI.

It may also serve as a starting point for designing a more complete research system using approved datasets and institutional infrastructure.

## Out-of-scope uses

The system must not be used for:

- diagnosis or treatment;
- clinical decision support;
- patient prioritization;
- direct use with identifiable patient information;
- unsupervised release of research data;
- measuring clinical quality or guideline adherence;
- making claims about model performance on real clinical records.

The project has not been reviewed or approved as a medical device or clinical research application.

## Inputs

The abstraction workflow accepts a synthetic patient identifier. A LangChain tool retrieves the corresponding structured record.

The source record may contain:

- age;
- heart-failure type;
- LVEF;
- discharge medications;
- follow-up interval.

A separate cohort tool accepts typed filters for heart-failure type and maximum LVEF.

## Outputs

The abstraction workflow produces a structured candidate containing:

- patient ID;
- synthetic-data flag;
- age;
- heart-failure type;
- LVEF;
- discharge medications;
- follow-up interval.

The cohort tool returns matching synthetic patient IDs and descriptive KPIs.

## Workflow controls

The language model does not have authority to approve or release its output.

The workflow applies the following controls:

1. Pydantic rejects missing, additional, incorrectly typed, or out-of-range fields.
2. Deterministic Python compares every generated value with the retrieved source.
3. LangGraph pauses for an explicit human decision.
4. Conditional routing sends approved results to a release node and all other outcomes to a stop node.
5. Both outcomes pass through an audit node before the graph ends.

If automated validation fails, a human approval attempt is blocked rather than converted into a released result.

## Evaluation data

The evaluation set contains three locked synthetic cases:

- P001
- P002
- P003

Each case has seven labeled output fields, giving 21 field-level comparisons.

The evaluation runs the automated graph only until the human-review interrupt. Human corrections are not included in the reported accuracy.

## Evaluation results

| Metric | Result |
|---|---:|
| Cases | 3 |
| Field comparisons | 21 |
| JSON parse success | 100.0% |
| Overall field accuracy | 100.0% |
| Exact-match accuracy | 100.0% |
| Automated validation pass rate | 100.0% |
| Cases containing unsupported fields | 0.0% |

All seven fields achieved 100% accuracy on the three evaluation cases.

These results show that the model followed the extraction instructions in this small, controlled setting. The source input was already structured, and the task mainly required copying allowed values into a JSON object.

The results do not measure performance on clinical notes, ambiguous documentation, missing data, larger cohorts, or real-world hospital data.

## Observed failure behavior

An earlier unvalidated version generated plausible dates and follow-up details that were not present in the source.

This showed that prompt instructions alone were not a sufficient control. The current workflow addresses that failure by forbidding additional fields and comparing accepted values with the source record.

Other possible failures include:

- malformed JSON;
- missing fields;
- incorrect values copied from the source;
- changes in output after a model or dependency update;
- medication-name variations affecting cohort calculations;
- incomplete or conflicting source data;
- reviewer error.

The current synthetic evaluation does not cover all these cases.

## Human oversight

A reviewer sees the candidate summary, automated validation status, and any detected issues before choosing `approve` or `reject`.

Human review is an additional control, not a replacement for automated validation. A reviewer cannot release an output that failed the automated checks.

The current interface is a terminal prompt. It does not provide authentication, reviewer-role management, or electronic signatures.

## Auditability

Each completed workflow writes one local JSON audit record containing:

- run ID;
- UTC timestamp;
- synthetic source payload;
- raw model response;
- validated summary;
- validation issues;
- reviewer decision and comment;
- final release status.

The audit record is keyed by run ID, so repeating the same run overwrites the same record instead of silently adding a duplicate.

The audit directory is ignored by Git.

## Data and privacy

Only synthetic data is included in the repository.

The local audit record contains the complete synthetic source and model response. This logging approach must not be reused with real clinical data without appropriate encryption, access controls, retention policies, and privacy review.

Real MIMIC-IV, EHR, note, or ECG data must never be committed to this repository.

## Cohort metrics

The cohort tool calculates descriptive values such as mean LVEF, medication coverage, and follow-up within 14 days.

These KPIs are included to demonstrate reproducible cohort analytics. They have not been reviewed as clinical quality measures and must not be interpreted as treatment recommendations or guideline adherence.

## Reproducibility

The repository records its Python dependencies in `pyproject.toml`, and the example environment identifies the local Hugging Face model.

Sampling is disabled to reduce variation between runs. However, exact reproducibility may still be affected by dependency versions, hardware, model revisions, and updates to the source code.

The model revision is not currently pinned to a specific Hugging Face commit.

## Main limitations

- Six synthetic patient records
- Three evaluation cases
- Structured inputs rather than clinical notes
- No external or clinical validation
- No missing-data or conflicting-evidence evaluation
- In-memory LangGraph checkpointing
- Local, unencrypted audit storage
- No authentication or authorization
- No deployment, monitoring service, or user interface
- No connection to MIMIC-IV, OMOP, an EHR, or institutional infrastructure

## Work required before real research use

Before considering use in a real research environment, the system would require:

- institutional privacy and security review;
- a clearly defined research protocol;
- approved access to representative data;
- expert-created annotation guidelines;
- a larger independently labeled evaluation set;
- subgroup and error analysis;
- durable checkpoint and audit storage;
- authentication and role-based access;
- monitoring for failures and model changes;
- documented release and incident-response procedures.

The current project demonstrates the workflow design. It does not claim readiness for clinical or production use.