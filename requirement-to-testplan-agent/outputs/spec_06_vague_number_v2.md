# Test plan: spec_06_vague_number.txt
Route: **human_review**

- Review reason: 1 requirement gap(s) flagged

## Gaps
- REQ-001: Vague wording: reasonable

## Test cases
| ID | Req | Type | Steps | Expected |
|---|---|---|---|---|
| TC-001 | REQ-001 | positive | Exercise: The system shall process payments in a reasonable time of 3 seconds. | Requirement is met |
| TC-002 | REQ-001 | boundary | Test at and just beyond the limit in: The system shall process payments in a reasonable time of 3 seconds. | Limit enforced exactly |
| TC-003 | REQ-002 | positive | Exercise: The system shall reject payments with an expired card. | Requirement is met |
| TC-004 | REQ-002 | negative | Attempt a disallowed action for: The system shall reject payments with an expired card. | Action is refused |
