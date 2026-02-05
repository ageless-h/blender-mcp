## ADDED Requirements

### Requirement: script.execute tool
The system SHALL provide a `script.execute` tool that executes arbitrary Python code in the Blender environment.

#### Scenario: Execute simple script
- **WHEN** `script.execute` is called with `code="import bpy; result = len(bpy.data.objects)"`
- **THEN** system executes the code and returns `{"success": true, "return_value": <count>}`

#### Scenario: Execute script with output
- **WHEN** `script.execute` is called with code that uses print statements
- **THEN** system captures stdout and returns in `output` field

#### Scenario: Execute script with error
- **WHEN** `script.execute` is called with code that raises an exception
- **THEN** system returns `{"success": false, "error": "<error message>"}`

### Requirement: Default disabled state
The system SHALL have `script.execute` disabled by default and require explicit configuration to enable.

#### Scenario: Call when disabled
- **WHEN** `script.execute` is called but not enabled in configuration
- **THEN** system returns error indicating the tool is disabled

#### Scenario: Enable via configuration
- **WHEN** `script_execute.enabled` is set to `true` in security configuration
- **THEN** system allows `script.execute` calls

### Requirement: Execution timeout
The system SHALL enforce a timeout on script execution to prevent infinite loops.

#### Scenario: Script within timeout
- **WHEN** `script.execute` is called with `timeout=30` and script completes in 5 seconds
- **THEN** system returns success with `execution_time_ms` field

#### Scenario: Script exceeds timeout
- **WHEN** `script.execute` is called and script runs longer than timeout
- **THEN** system terminates execution and returns `{"success": false, "error": "Execution timeout after <N> seconds"}`

#### Scenario: Default timeout
- **WHEN** `script.execute` is called without timeout parameter
- **THEN** system uses default timeout of 30 seconds

### Requirement: Return value capture
The system SHALL capture and return the value of the last expression in the script.

#### Scenario: Script with return value
- **WHEN** script ends with an expression (not a statement)
- **THEN** `return_value` field contains the evaluated expression value

#### Scenario: Script without return value
- **WHEN** script ends with a statement (e.g., assignment, function call)
- **THEN** `return_value` field is `null`

### Requirement: Security integration
The system SHALL integrate with existing security layers (allowlist, audit logging).

#### Scenario: Audit logging
- **WHEN** `script.execute` is called
- **THEN** system logs the executed code and result to audit log

#### Scenario: Rate limiting
- **WHEN** `script.execute` is called
- **THEN** call is subject to configured rate limits

### Requirement: User consent workflow
The system SHALL support user consent requirement before execution when configured.

#### Scenario: Consent required
- **WHEN** `require_consent` is enabled and script.execute is called
- **THEN** system returns consent_required status with warning message

#### Scenario: Consent granted
- **WHEN** user grants consent for script execution
- **THEN** system proceeds with execution

