# Audit Logging

## Events
Each capability execution produces an audit event containing capability name, outcome, timestamp, error when applicable, and optional metadata.

Required fields:
- capability
- ok
- timestamp

Optional fields:
- error
- data

## Metadata Examples
- allowlist.update: data includes added/removed entries

## Retention
Audit logs are retained per policy aligned to security requirements and compliance needs.

## Access
Audit logs are read-only for agents and accessible to operators for review.
