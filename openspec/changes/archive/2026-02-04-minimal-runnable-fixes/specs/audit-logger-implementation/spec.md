## MODIFIED Requirements

### Requirement: File or JSON export is supported
The system SHALL support exporting audit events to a file or JSON format, including optional metadata fields.

#### Scenario: Audit export
- **WHEN** an export is requested
- **THEN** audit events are written in JSON format with metadata if present
