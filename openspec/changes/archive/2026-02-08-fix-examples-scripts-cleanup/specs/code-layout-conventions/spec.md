## ADDED Requirements

### Requirement: No ad-hoc sys.path manipulation in source files
Source files outside tests/ SHALL NOT contain inline sys.path manipulation. Path resolution SHALL be delegated to a per-directory _pathfix.py module.

#### Scenario: Script import review
- **WHEN** a Python file in examples/ or scripts/ is reviewed
- **THEN** it does not contain direct sys.path.insert calls; it imports _pathfix instead

### Requirement: Scripts README documents all scripts
The scripts/README.md SHALL document every script in the scripts/ directory with its purpose and usage.

#### Scenario: README completeness
- **WHEN** scripts/README.md is reviewed
- **THEN** each .py file in scripts/ has a corresponding entry with description and usage command
