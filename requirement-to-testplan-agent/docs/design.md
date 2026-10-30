# Design: Requirements-to-Test-Plan Agent

## Problem
Test planning from written requirements is slow and inconsistent, and vague requirements slip through. This workflow turns a spec into a draft test plan and a gap report, and sends anything doubtful to a person.

## Users
QA analysts and business analysts reviewing specs before build or validation.

## Pattern
Prompt chain with a programmatic check and a routing decision (a fixed workflow, not a free-roaming agent). Chosen because the steps are known in advance, which makes it easier to test and govern.

## Stages
| # | Stage | Input | Output | Done by |
|---|---|---|---|---|
| 1 | Extract requirements | spec text | requirement list (JSON) | model |
| 2 | Generate test cases | requirements | cases (JSON: positive, boundary, negative) | model |
| 3 | Coverage and schema check | requirements, cases | uncovered IDs, schema ok | code |
| 4 | Flag gaps | requirements | gaps (missing criteria, vague words) | model |
| 5 | Route | all of the above | auto_approve or human_review + reasons | code |

## Context management
Each stage receives only what it needs: stage 2 and 4 see the extracted requirements, not the raw spec. Intermediate outputs are JSON and logged.

## Human-in-the-loop
Any gap, uncovered requirement, schema failure, empty spec, or pipeline error routes to human review. Auto-approve is only for clean results, and a human still owns the final test plan.

## Failure modes handled
- Model returns invalid JSON: caught, logged, routed to review.
- Spec has no requirements: routed to review.
- Requirement without a test case: caught by stage 3.

## Evaluation
Six synthetic specs in data/eval_set.json with expected requirement counts, gaps and routes. Metrics: extraction accuracy, gap precision and recall, routing accuracy, schema validity. Prompts v1 and v2 are scored on the same set.

## Known limits
- Mock mode is a rule-based stand-in. It shows the harness works, not how a real model performs.
- The eval set is small and written by the author. Real use needs more cases from varied specs.
- Gap detection covers vague wording and missing measures, not correctness of the business rule.
