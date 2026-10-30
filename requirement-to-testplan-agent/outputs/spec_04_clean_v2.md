# Test plan: spec_04_clean.txt
Route: **auto_approve**

- No issues flagged

## Gaps
- None

## Test cases
| ID | Req | Type | Steps | Expected |
|---|---|---|---|---|
| TC-001 | REQ-001 | positive | Exercise: The system shall email a reset link that expires after 30 minutes. | Requirement is met |
| TC-002 | REQ-001 | boundary | Test at and just beyond the limit in: The system shall email a reset link that expires after 30 minutes. | Limit enforced exactly |
| TC-003 | REQ-002 | positive | Exercise: The system shall limit reset requests to 3 per hour per account. | Requirement is met |
| TC-004 | REQ-002 | boundary | Test at and just beyond the limit in: The system shall limit reset requests to 3 per hour per account. | Limit enforced exactly |
| TC-005 | REQ-002 | negative | Attempt a disallowed action for: The system shall limit reset requests to 3 per hour per account. | Action is refused |
