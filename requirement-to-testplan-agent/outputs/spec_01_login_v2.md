# Test plan: spec_01_login.txt
Route: **human_review**

- Review reason: 1 requirement gap(s) flagged

## Gaps
- REQ-003: Vague wording: quickly

## Test cases
| ID | Req | Type | Steps | Expected |
|---|---|---|---|---|
| TC-001 | REQ-001 | positive | Exercise: The system shall lock an account after 5 failed login attempts. | Requirement is met |
| TC-002 | REQ-001 | boundary | Test at and just beyond the limit in: The system shall lock an account after 5 failed login attempts. | Limit enforced exactly |
| TC-003 | REQ-001 | negative | Attempt a disallowed action for: The system shall lock an account after 5 failed login attempts. | Action is refused |
| TC-004 | REQ-002 | positive | Exercise: The system shall display an error message when the password is incorrect. | Requirement is met |
| TC-005 | REQ-003 | positive | Exercise: The system shall respond to login requests quickly. | Requirement is met |
