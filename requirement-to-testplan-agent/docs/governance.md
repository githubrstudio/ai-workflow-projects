# Governance Note

Mapped loosely to the NIST AI RMF functions (Govern, Map, Measure, Manage). Illustrative controls for a prototype.

## Govern
- Owner named for the workflow and the prompt library.
- Prompt changes follow: edit in a new version folder, re-run the eval set, compare, approve, then release.
- Data rule: public or synthetic specs only. No customer data, no confidential company documents.

## Map (risks)
| Risk | Example | Control |
|---|---|---|
| Made-up requirements | Model invents a requirement | Prompt says use only spec text; reviewer checks extraction |
| Missed requirements | Requirement gets no test case | Stage 3 coverage check in code |
| Invalid output | Broken JSON | Parse failure logged and routed to a human |
| Over-reliance | Plan accepted without review | Gaps or doubt always route to review; human owns the final plan |
| Vague specs treated as clear | "Quickly" passes through | v2 gap prompt flags vague words |

## Measure
Run evaluate.py before any prompt or model change. Track extraction accuracy, gap precision and recall, routing accuracy, schema validity. Spot-check outputs by hand.

## Manage
- logs/runs.jsonl records every stage with a run ID and timestamp.
- Re-run the eval set after prompt, model, or spec-format changes.
- Keep a change log of prompt versions and their scores.
- Retire or roll back a version if scores drop.
