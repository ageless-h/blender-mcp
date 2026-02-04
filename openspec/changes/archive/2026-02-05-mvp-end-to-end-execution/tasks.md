## 1. Adapter Interface and Types

- [x] 1.1 Create `AdapterResult` dataclass in `src/blender_mcp/adapters/types.py` with fields: ok, result, error, timing_ms
- [x] 1.2 Define `BlenderAdapter` protocol in `src/blender_mcp/adapters/base.py` with `execute(capability, payload) -> AdapterResult` method
- [x] 1.3 Add adapter as optional parameter to `MCPServer.__init__()` (default None for backward compatibility)

## 2. Mock Adapter Implementation

- [x] 2.1 Create `MockAdapter` in `src/blender_mcp/adapters/mock.py` implementing BlenderAdapter protocol
- [x] 2.2 Add response configuration method to MockAdapter for test setup
- [x] 2.3 Implement default behavior: return AdapterResult(ok=True, result={}) for unregistered capabilities

## 3. Socket Adapter Implementation

- [x] 3.1 Create `SocketAdapter` in `src/blender_mcp/adapters/socket.py` with host/port configuration
- [x] 3.2 Implement TCP socket connection with configurable timeout (default 30s)
- [x] 3.3 Implement `execute()`: send JSON request, receive JSON response, parse to AdapterResult
- [x] 3.4 Handle connection failures: return AdapterResult(ok=False, error="adapter_unavailable")

## 4. Server Dispatch Integration

- [x] 4.1 Modify `MCPServer.handle_request()` to call adapter.execute() after security checks pass
- [x] 4.2 Map AdapterResult to Response (preserve ok, result, error)
- [x] 4.3 Maintain stub response when adapter is None (backward compatibility)
- [x] 4.4 Add audit logging for adapter failures (error code in AuditEvent)

## 5. Addon Socket Server

- [x] 5.1 Create `socket_server.py` in `addon/` with TCP server listening on configurable port
- [x] 5.2 Implement request handler: parse JSON, call `execute_capability()`, return JSON response
- [x] 5.3 Add `start_socket_server()` and `stop_socket_server()` entrypoints

## 6. Example and Integration Updates

- [x] 6.1 Update `examples/stdio_loop.py` to accept optional adapter configuration
- [x] 6.2 Add example usage with SocketAdapter connecting to Blender addon
- [x] 6.3 Update integration test harness to use MockAdapter by default

## 7. Testing

- [x] 7.1 Add unit tests for AdapterResult and BlenderAdapter protocol
- [x] 7.2 Add unit tests for MockAdapter (configured responses, default behavior)
- [x] 7.3 Add unit tests for SocketAdapter (mock socket, connection failure)
- [x] 7.4 Add integration tests for server dispatch with MockAdapter
- [x] 7.5 Add integration test for end-to-end scene.read with MockAdapter returning simulated data

## 8. Verification

- [x] 8.1 Run unit and integration tests: `uv run python -m unittest discover -s tests -p "test_*.py"`
- [x] 8.2 Run stdio example with MockAdapter: `python -m examples.stdio_loop`
- [x] 8.3 Manual test with Blender: start addon socket server, run stdio_loop with SocketAdapter, send scene.read request
