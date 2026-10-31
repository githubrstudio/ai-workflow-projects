# data-quality-reconciliation-agent

Compares a **source** dataset to a **reporting** dataset, profiles both, flags mismatches, and writes files for human review. Reusable: point it at any two CSVs with a JSON config. Python standard library only.

## Quick start
    python3 scripts/generate_data.py                       # regenerate synthetic data (optional)
    python3 -m dq_agent --config configs/mismatch_scenario.json --out output/mismatch_run
    python3 -m dq_agent --config configs/match_scenario.json    --out output/match_run
    python3 tests/test_agent.py

Exit code: 0 = MATCH, 1 = REVIEW_REQUIRED.

## Outputs (in `--out`)
| File | When | Purpose |
|---|---|---|
| `summary_counts.json` / `.md` | always | Row counts and mismatch counts by type, severity and column |
| `profile_comparison.csv` | always | Statistical comparison (sum, mean, nulls, distinct...) with flags |
| `mismatches.csv` | only if mismatches | Review queue sorted by severity, with blank `review_decision` and `reviewer_notes` |

When the datasets match, you get the counts summary only and no review queue.

## Use your own data
Copy `configs/mismatch_scenario.json`, then set:
- `source_file`, `target_file` (paths relative to the config file)
- `keys`: business key columns in each file
- `columns`: for each compared field, its source name, target name, `type` (`string`, `numeric`, `date`) and, for numeric, an optional `tolerance`
- `profile_tolerance_pct`: allowed relative drift in profile metrics

## Demo results (synthetic accounts)
The mismatch scenario injects known defects: 3 missing, 2 extra, 1 duplicate key, 2 nulls, 11 value differences (rounding, sign flips, scale errors, branch changes) and 5 format-only differences. The agent reports exactly 24. The match scenario reformats currency and key case but holds the same values and reports MATCH.

## Layout
`dq_agent/` (extract, profile, reconcile, triage, report, pipeline) | `configs/` | `data/` (synthetic) | `scripts/generate_data.py` | `tests/` | `docs/design.md`, `docs/governance.md`

## Scheduling
    0 6 * * * cd /path/to/repo && python3 -m dq_agent --config configs/my_job.json --out output/$(date +\%F) || echo "review needed"

## Ideas to extend
SQL/Parquet loaders, an LLM step that drafts plain-English explanations for reviewers (rules still decide matches), email or Teams alert on exit code 1.
