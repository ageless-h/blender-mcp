## ADDED Requirements

### Requirement: Rate limiting uses a time window
Rate limiting SHALL enforce a configurable time window with a maximum count.

#### Scenario: Windowed limit exceeded
- **WHEN** requests exceed the allowed count within the time window
- **THEN** subsequent requests are rejected until the window resets
