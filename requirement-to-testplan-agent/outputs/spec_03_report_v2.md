# Test plan: spec_03_report.txt
Route: **human_review**

- Review reason: 2 requirement gap(s) flagged

## Gaps
- REQ-002: Vague wording: easy, appropriate
- REQ-004: Vague wording: secure

## Test cases
| ID | Req | Type | Steps | Expected |
|---|---|---|---|---|
| TC-001 | REQ-001 | positive | Exercise: The system shall generate the monthly report as a PDF. | Requirement is met |
| TC-002 | REQ-002 | positive | Exercise: The report shall be easy to read and use appropriate formatting. | Requirement is met |
| TC-003 | REQ-003 | positive | Exercise: The system shall retain generated reports for 24 months. | Requirement is met |
| TC-004 | REQ-003 | boundary | Test at and just beyond the limit in: The system shall retain generated reports for 24 months. | Limit enforced exactly |
| TC-005 | REQ-004 | positive | Exercise: The system shall be secure. | Requirement is met |
