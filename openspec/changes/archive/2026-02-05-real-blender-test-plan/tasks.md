## 1. Configuration Infrastructure

- [x] 1.1 Create `tests/blender-paths.example.json` template with Windows/Linux/macOS example paths
- [x] 1.2 Add `tests/blender-paths.json` to `.gitignore`
- [x] 1.3 Implement `tests/integration/real_blender/_config.py` with `load_blender_configs()` function
- [x] 1.4 Add environment variable support (`BLENDER_TEST_PATHS`, `BLENDER_EXECUTABLE`)
- [x] 1.5 Add path validation and version detection logic

## 2. Test Harness Implementation

- [x] 2.1 Create `tests/integration/real_blender/__init__.py`
- [x] 2.2 Implement `BlenderProcessHarness` class in `tests/integration/real_blender/_blender_harness.py`
- [x] 2.3 Add dynamic port allocation with `find_free_port()` function
- [x] 2.4 Implement `start()` method: subprocess launch with `--background --python` flags
- [x] 2.5 Implement `send_request()` method: JSON socket communication
- [x] 2.6 Implement `stop()` method: process termination and cleanup
- [x] 2.7 Add context manager support (`__enter__`, `__exit__`)
- [x] 2.8 Add stdout/stderr capture for debugging

## 3. Socket Server Adaptation

- [x] 3.1 Update `addon/start_socket_server.py` to read port from `MCP_SOCKET_PORT` environment variable
- [x] 3.2 Add ready signal output for harness detection

## 4. Real Blender Tests

- [x] 4.1 Create `tests/integration/real_blender/test_real_capabilities.py`
- [x] 4.2 Implement `test_scene_read` with real Blender
- [x] 4.3 Implement `test_scene_write` with real Blender
- [x] 4.4 Add pytest parametrization for multi-version testing
- [x] 4.5 Add skip decorator when no Blender configured

## 5. Multi-Version Execution Script

- [x] 5.1 Create `scripts/run_real_blender_tests.py`
- [x] 5.2 Implement version matrix iteration logic
- [x] 5.3 Implement results aggregation
- [x] 5.4 Add export to `docs/versioning/compatibility-results.json`

## 6. Documentation & Validation

- [x] 6.1 Create local `tests/blender-paths.json` with user's three Blender paths
- [x] 6.2 Run tests against Blender 4.2.17 LTS and verify pass
- [x] 6.3 Run tests against Blender 4.5.6 LTS and verify pass
- [x] 6.4 Run tests against Blender 5.0.1 and verify pass
- [x] 6.5 Update `compatibility-results.json` with real test data
