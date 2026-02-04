## 1. Align OpenSpec requirements (specs)

- [x] 1.1 Update `openspec/specs/integration-tests-and-examples/spec.md` to incorporate the added requirements from this change (example + integration test per capability change, shared harness + fakes boundary)
- [x] 1.2 Update `openspec/specs/validation-gate-ci/spec.md` to incorporate the modified and added requirements from this change (scenario-based integration tests in CI, integration gates capability execution paths)

## 2. Establish an integration test harness baseline

- [x] 2.1 Create a shared integration test harness module (e.g. under `tests/integration/`) for building an `MCPServer` bundle with in-memory dependencies
- [x] 2.2 Refactor `tests/integration/test_workflows.py` to use the shared harness (reduce duplication, standardize setup)
- [x] 2.3 Define and apply an explicit mocks/fakes boundary in integration tests (only isolate external/system dependencies; keep capability execution path real)

## 3. Examples baseline for capability changes

- [x] 3.1 Update `examples/README.md` to state the project convention: each new capability or capability behavior change includes at least one runnable example
- [x] 3.2 Ensure the existing `python -m examples.stdio_loop` remains a stable reference example and remains runnable in CI

## 4. CI gate: execute integration suite

- [x] 4.1 Update `.github/workflows/ci.yml` integration job to run the integration test suite (replace the placeholder module invocation with an integration test discovery command)
- [x] 4.2 Keep CI running the integration example(s) and ensure failures fail the workflow

## 5. Verification

- [x] 5.1 Run unit and integration tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- [x] 5.2 Run the stdio example: `python -m examples.stdio_loop`
