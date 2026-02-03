## MODIFIED Requirements

### Requirement: Allowlist updates are audited
Allowlist updates SHALL generate audit events with update details.

#### Scenario: Allowlist change
- **WHEN** the allowlist is updated
- **THEN** an audit event is recorded with added and removed entries
