# Documentation Organization

## Purpose
TBD.

## Requirements

### Requirement: Documentation has a single authoritative home
Project documentation SHALL live under `docs/` with domain-based subdirectories.

#### Scenario: Documentation discovery
- **WHEN** a contributor searches for architecture or security documentation
- **THEN** it is found under `docs/` in a domain-specific folder

### Requirement: OpenSpec artifacts remain under openspec/
OpenSpec artifacts SHALL remain under `openspec/` and not be mixed into `docs/`.

#### Scenario: Spec artifact review
- **WHEN** a reviewer inspects OpenSpec changes
- **THEN** change artifacts are found under `openspec/changes/`
