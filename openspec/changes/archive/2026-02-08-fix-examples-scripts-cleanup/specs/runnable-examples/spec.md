## MODIFIED Requirements

### Requirement: Runnable example exists
The project SHALL provide at least one runnable example or script. The examples README SHALL only list examples that have corresponding implementation files. Examples that do not yet exist SHALL NOT appear in the README.

#### Scenario: Example execution
- **WHEN** the example is executed
- **THEN** it completes successfully and demonstrates the minimal loop

#### Scenario: README accuracy
- **WHEN** the examples README is reviewed
- **THEN** every listed example has a corresponding runnable file in examples/

## ADDED Requirements

### Requirement: Examples use shared path resolution
Examples SHALL resolve src/ onto sys.path via a shared _pathfix.py module rather than inline path manipulation.

#### Scenario: Path resolution consistency
- **WHEN** an example file needs to import from src/
- **THEN** it imports _pathfix instead of computing and inserting the path inline
