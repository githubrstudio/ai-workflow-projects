# Test plan: spec_02_transfer.txt
Route: **auto_approve**

- No issues flagged

## Gaps
- None

## Test cases
| ID | Req | Type | Steps | Expected |
|---|---|---|---|---|
| TC-001 | REQ-001 | positive | Exercise: The system shall reject transfers above 10000 USD per day. | Requirement is met |
| TC-002 | REQ-001 | boundary | Test at and just beyond the limit in: The system shall reject transfers above 10000 USD per day. | Limit enforced exactly |
| TC-003 | REQ-001 | negative | Attempt a disallowed action for: The system shall reject transfers above 10000 USD per day. | Action is refused |
| TC-004 | REQ-002 | positive | Exercise: The system shall send a confirmation email within 60 seconds of a completed transfer. | Requirement is met |
| TC-005 | REQ-002 | boundary | Test at and just beyond the limit in: The system shall send a confirmation email within 60 seconds of a completed transfer. | Limit enforced exactly |
| TC-006 | REQ-003 | positive | Exercise: The system shall only allow account owners to initiate transfers. | Requirement is met |
| TC-007 | REQ-003 | negative | Attempt a disallowed action for: The system shall only allow account owners to initiate transfers. | Action is refused |
