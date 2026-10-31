# Design: data-quality-reconciliation-agent

A fixed, deterministic workflow, not an open-ended agent. Reconciliation must be repeatable and auditable, so every decision is a rule in code. An LLM can later be added to *explain* findings; it should never decide what matches.

    config.json -> 1 Extract -> 2 Profile + compare stats -> 3 Row-level reconcile -> 4 Triage -> 5 Report -> human review

| Stage | What it does | Output |
|---|---|---|
| 1 Extract | Loads both CSVs, fails loudly if a configured column is missing | rows in memory |
| 2 Profile | Row counts, nulls, distinct counts, sum/mean/stdev/min/max per numeric column, top values for text; flags deltas beyond tolerance | profile_comparison.csv |
| 3 Reconcile | Joins on the business key (case-insensitive by default); finds missing, extra, duplicate keys; compares mapped columns with type-aware rules (numeric tolerance, date parsing, string format) | mismatch records |
| 4 Triage | Adds severity and a rule-based likely cause (rounding, sign flip, scale error, format only, dropped record) | review queue |
| 5 Report | Always writes summary_counts.json/.md. Writes mismatches.csv only when something needs review | files for humans |

## Reuse with other datasets
Nothing is hard-coded to accounts. A new comparison is one JSON file: file paths, key mapping, and a column mapping with type (`string`, `numeric`, `date`) and optional numeric `tolerance`. Source and target columns may have different names. Exit code is 0 for MATCH and 1 for REVIEW_REQUIRED, so a scheduler or CI job can alert on it.

## Mismatch types
MISSING_IN_TARGET, EXTRA_IN_TARGET, DUPLICATE_KEY_SOURCE/TARGET, NULL_MISMATCH, VALUE_MISMATCH, FORMAT_DIFFERENCE (same value, different presentation).

## Limits
Data is held in memory (fine to roughly a few million rows; use a database or Spark beyond that). CSV input only; add a loader in `extract.py` for SQL or Parquet. Triage causes are heuristics, not conclusions.
