## ADDED Requirements

### Requirement: Explicit capability allowlist
The system SHALL enforce an explicit allowlist of capabilities that can be invoked by agents.

#### Scenario: Disallowed capability request
- **WHEN** an agent requests a capability not in the allowlist
- **THEN** the system denies the request with a clear error and no side effects

### Requirement: Permission scopes per capability
Each capability SHALL define required permission scopes that are validated before execution.

#### Scenario: Missing permission scope
- **WHEN** a request lacks the required scope for a capability
- **THEN** execution is blocked and an authorization error is returned

### Requirement: Rate limiting and resource guards
The MCP service SHALL enforce rate limits and resource guards to preserve stability.

#### Scenario: Rate limit exceeded
- **WHEN** requests exceed configured rate limits
- **THEN** additional requests are rejected with a rate limit error

### Requirement: Audit logging for agent actions
All capability executions SHALL be recorded in an audit log with request metadata and outcomes.

#### Scenario: Successful capability invocation
- **WHEN** a capability executes successfully
- **THEN** an audit record is persisted with timestamps, requester, and result
