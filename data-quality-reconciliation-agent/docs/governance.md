# Governance (NIST AI RMF style)

- **Govern:** Rules live in code and config under version control; changing a tolerance or mapping is a reviewed commit. Owner: repo maintainer.
- **Map:** Users are data owners and analysts. Risks: a loose tolerance hides real errors; a wrong key mapping creates false mismatches; sensitive data in outputs.
- **Measure:** `tests/test_agent.py` asserts exact mismatch counts on a synthetic dataset with known injected defects, and that a clean pair reports MATCH.
- **Manage:** Humans decide. Every mismatch row has blank `review_decision` and `reviewer_notes` columns. The agent never edits either dataset. Failures (missing columns) stop the run instead of producing partial results.

Data handling: the repo contains only synthetic data. Do not commit real data; `output/` is git-ignored. Mask or limit identifiers in outputs if reports leave a controlled environment.
