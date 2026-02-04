# Compatibility Results Validation

## Purpose
TBD.

## Requirements

### Requirement: Compatibility results have required fields
Compatibility results SHALL include status and checked_at fields for each supported version.

#### Scenario: Compatibility results validation
- **WHEN** compatibility results are read
- **THEN** each entry includes status and checked_at
