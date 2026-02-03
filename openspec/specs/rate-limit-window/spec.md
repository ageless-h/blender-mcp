# Rate Limit Window

## Purpose
TBD.

## Requirements

### Requirement: Rate limiting uses a time window
Rate limiting SHALL be documented as time-windowed, and docs SHALL not claim unimplemented global guardrails.

#### Scenario: Windowed limit exceeded
- **WHEN** requests exceed the allowed count within the time window
- **THEN** subsequent requests are rejected until the window resets

#### Scenario: Window reset
- **WHEN** the time window passes
- **THEN** new requests are accepted again up to the limit

#### Scenario: Documentation alignment
- **WHEN** rate-limits documentation is reviewed
- **THEN** it reflects only implemented windowed behavior
