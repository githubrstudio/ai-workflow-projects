# Requirements-to-Test-Plan Agent (portfolio project)

A small AI workflow that turns a requirements spec into a draft test plan and gap report, with human review routing, an evaluation harness, and governance notes. All data is synthetic.

## Run (no API key needed)
    python3 evaluate.py mock                 # compare prompt v1 vs v2
    python3 pipeline.py data/specs/spec_01_login.txt --version v2

## Run with a real model (optional)
    pip install anthropic
    export ANTHROPIC_API_KEY=...
    python3 evaluate.py api
Mock mode is a deterministic rule-based stand-in driven by prompt markers; its scores show the harness works, not model quality. Run API mode for real model results.

## Files
- pipeline.py: the 5-stage workflow and routing
- llm.py: mock and API backends
- evaluate.py: scoring and version comparison
- prompts/v1, prompts/v2: prompt library by version
- data/: synthetic specs and eval set
- docs/design.md, docs/governance.md: design and controls
- logs/runs.jsonl: run log
- results/: saved eval scores
