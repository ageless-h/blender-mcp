## Context

The repository currently contains a root-level package (`blender_mcp/`) and documentation that expects a `src/` layout. This ambiguity causes inconsistent import paths and packaging behavior. The change defines a single code root and updates packaging configuration to ensure consistent installs and imports.

## Goals / Non-Goals

**Goals:**
- Decide on a single code root layout and make it authoritative.
- Define a packaging configuration that installs the package predictably.
- Provide a clear migration path for existing code and imports.

**Non-Goals:**
- Implement new MCP capabilities (transport, audit, allowlist) in this change.
- Change runtime behavior beyond packaging/import resolution.
- Introduce new build tools beyond what is required for standard packaging.

## Decisions

- **Adopt `src/` layout as the single code root.**
  - Rationale: aligns with the documented structure plan and avoids accidental imports from the repo root.
  - Alternatives: keep root-level package (rejected due to import ambiguity and packaging confusion).

- **Use PEP 621 metadata and a standard build backend (hatchling).**
  - Rationale: common, minimal configuration and well supported by tooling.
  - Alternatives: setuptools (rejected due to heavier configuration for this project).

- **Package discovery is limited to `src/`.**
  - Rationale: prevents dual-package resolution and accidental namespace shadowing.

## Risks / Trade-offs

- **Migration touches many files** -> Mitigation: move code in one sweep and update imports.
- **Tooling expectations may differ** -> Mitigation: add a brief migration note and verify install locally.

## Migration Plan

- Create `src/blender_mcp/` and move the package there.
- Update `pyproject.toml` to use `src/` layout and proper package discovery.
- Adjust imports and tests to match the new layout.
- Add a short migration note in `README.md` if needed.

## Open Questions

- Should we pin a specific build backend version, or leave it unpinned?
- Do we need a temporary shim for legacy imports during migration?
