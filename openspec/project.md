# Project Context

## Purpose
Provide a minimal, secure MCP server surface for Blender automation.

## Tech Stack
- Python 3.12
- MCP server core

## Project Conventions

### Code Style
- Prefer explicit, readable code with minimal dependencies.
- Use UTF-8 for file I/O.

### Architecture Patterns
- Transport adapters are isolated from core server logic.
- Security primitives live under `security/`.

### Testing Strategy
- Unittest-based unit and integration tests under `tests/`.
- Integration tests must align to the documented plan.

### CI Expectations
- Lint, unit, and integration placeholder run on pull requests.

### Git Workflow
- Small, focused commits with English messages.

## Domain Context
- Blender automation via MCP requires strict allowlist and auditability.

## Important Constraints
- Avoid private Blender APIs.

## External Dependencies
- None required beyond standard Python for the minimal loop.
