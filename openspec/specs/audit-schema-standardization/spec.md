# Audit Schema Standardization

## Purpose
TBD.

## Requirements

### Requirement: Audit schema is standardized
Audit events SHALL include capability, ok, timestamp, and optional metadata fields.

#### Scenario: Audit event creation
- **WHEN** an audit event is recorded
- **THEN** it contains the required fields and metadata if present
