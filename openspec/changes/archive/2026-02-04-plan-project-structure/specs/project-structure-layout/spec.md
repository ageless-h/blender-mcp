## ADDED Requirements

### Requirement: Top-level directory layout is defined
The repository SHALL define a top-level directory layout that separates source code, addon code, documentation, tests, examples, and scripts.

#### Scenario: Repository structure review
- **WHEN** a developer inspects the repository root
- **THEN** each top-level directory has a clear, documented responsibility

### Requirement: Source code uses src layout
Core service code SHALL reside under a single `src/` directory with a single package root.

#### Scenario: Code location check
- **WHEN** new core modules are added
- **THEN** they are placed under `src/` following the package root
