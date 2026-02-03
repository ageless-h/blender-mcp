## 1. Research and alignment

- [x] 1.1 Survey MCP definitions, protocol expectations, and best practices; summarize applicability to Blender MCP
- [x] 1.2 Review Blender official API docs and identify stable, versioned integration surfaces
- [x] 1.3 Analyze reference projects (ahujasid/blender-mcp, chrome-devtools-mcp) for reusable patterns and gaps

## 2. Core architecture foundation

- [x] 2.1 Define MCP core service lifecycle states and health reporting
- [x] 2.2 Design transport-agnostic adapter interface and select primary transport for MVP
- [x] 2.3 Define plugin boundary contract surface and versioning rules

## 3. Security and stability model

- [x] 3.1 Specify capability allowlist format and enforcement flow
- [x] 3.2 Define permission scopes per capability and authorization checks
- [x] 3.3 Design rate limiting and resource guard configuration
- [x] 3.4 Specify audit log schema and retention policy

## 4. Capability catalog and version policy

- [x] 4.1 Draft canonical capability catalog with descriptions and grouping
- [x] 4.2 Define capability metadata for version constraints and limitations
- [x] 4.3 Establish support matrix policy (LTS + latest) and deprecation/rollback rules

## 5. Evaluation gates and validation

- [x] 5.1 Define stability and security evaluation criteria with measurable thresholds
- [x] 5.2 Specify gate workflow and release artifact storage

## 6. Testing and examples

- [x] 6.1 Design multi-version integration test harness and CI matrix
- [x] 6.2 Implement critical workflow scenarios as integration tests
- [x] 6.3 Create runnable example workflows demonstrating safe capability usage
