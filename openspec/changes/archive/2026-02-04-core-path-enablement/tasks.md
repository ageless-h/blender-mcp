## 1. Code Root Decision

- [x] 1.1 Define the single authoritative code root as `src/blender_mcp/`
- [x] 1.2 Move the existing `blender_mcp/` package into `src/` and update imports
- [x] 1.3 Add a short migration note for contributors

## 2. Packaging Configuration

- [x] 2.1 Update `pyproject.toml` with PEP 621 metadata and build backend
- [x] 2.2 Configure package discovery to use `src/` only

## 3. Validation Gate CI

- [x] 3.1 Align integration tests with the documented test plan scenarios
- [x] 3.2 Add minimal CI workflow with lint, unit, and integration placeholder steps
