## Context

The MCP server (`src/blender_mcp/core/server.py`) handles JSON-RPC 2.0 requests with full security (allowlist, permissions, rate limiting, audit). The Blender addon (`addon/entrypoint.py`) implements `execute_capability()` with `scene.read` and `scene.write` stubs that interact with bpy. These components run in separate processes and are currently disconnected.

Current flow: Client → StdioTransport → MCPServer → `{"status": "accepted"}` (stub)
Target flow: Client → StdioTransport → MCPServer → BlenderAdapter → Addon → bpy → real result

## Goals / Non-Goals

**Goals:**
- Connect MCPServer to Blender addon via a communication channel
- Execute `scene.read` and `scene.write` end-to-end returning real Blender data
- Maintain all existing security checks (allowlist, permissions, rate limiting)
- Support testability with mock adapters for CI (no Blender required)

**Non-Goals:**
- HTTP/WebSocket transports (future change)
- Full capability catalog execution (MVP: scene.read, scene.write only)
- Official MCP SDK integration (documented as future)
- Blender addon UI or operator registration

## Decisions

### D1: Socket-based IPC for adapter communication

**Choice**: Unix domain socket (or localhost TCP on Windows) between MCP server and Blender addon.

**Rationale**: 
- Blender addon runs inside Blender process; cannot share memory with external MCP server
- Stdio is already used for client transport; cannot reuse for internal IPC
- Sockets provide bidirectional, reliable communication with minimal dependencies

**Alternatives considered**:
- Shared file polling: Higher latency, complex synchronization
- Named pipes: Platform differences, less flexible than sockets
- Embedding server in Blender: Blocks Blender main thread, complicates architecture

### D2: Adapter interface as abstract protocol

**Choice**: Define `BlenderAdapter` protocol with `execute(capability, payload) -> result` method. Server injects adapter at construction.

**Rationale**:
- Decouples server from transport details
- Enables mock adapter for testing without Blender
- Matches existing dependency injection pattern (catalog, allowlist, etc.)

### D3: Addon runs socket server, MCP server is client

**Choice**: Blender addon listens on socket; MCP server connects as client.

**Rationale**:
- Addon lifecycle tied to Blender; it should own the socket lifecycle
- MCP server can retry connection if Blender not ready
- Simpler error handling: MCP server reports "adapter unavailable" if connection fails

### D4: JSON message format over socket

**Choice**: Single-line JSON messages (same as JSON-RPC format) for adapter protocol.

**Rationale**:
- Consistent with existing protocol patterns
- Easy to debug and log
- No additional serialization dependencies

### D5: Capability dispatch in MCPServer.handle_request()

**Choice**: Replace stub response with adapter call after security checks pass.

**Rationale**:
- Security checks remain in server (not duplicated in addon)
- Single point of dispatch modification
- Adapter only receives authorized requests

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Blender not running when MCP server starts | Server enters "waiting for adapter" state; retries connection with backoff |
| Socket connection drops mid-request | Return error response; client can retry; audit log records failure |
| Addon execution blocks Blender | Document that capabilities should be fast; future: async execution |
| Windows socket path differences | Use localhost TCP with configurable port; abstract in adapter factory |
| Testing requires Blender | MockAdapter implements same interface; integration tests use mock by default |

## Open Questions

- Q1: Should adapter connection be lazy (on first request) or eager (at server start)?
  - Tentative: Eager with retry, so health check reflects true readiness
- Q2: Timeout for addon execution?
  - Tentative: 30s default, configurable per capability
