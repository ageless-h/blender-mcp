# Security Configuration

This document describes all security-related environment variables and configuration options for Blender MCP.

## Environment Variables

### Core Security Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_ADAPTER` | string | `socket` | Adapter mode: `socket` (production) or `mock` (testing) |
| `MCP_LOG_LEVEL` | string | `WARNING` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `MCP_ENABLE_SCRIPT_EXECUTE` | string | `false` | Enable `blender_execute_script` capability (dangerous) |

### Connection Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_SOCKET_HOST` | string | `127.0.0.1` | Host address for Blender addon connection |
| `MCP_SOCKET_PORT` | int | `9876` | Port for Blender addon connection |
| `MCP_MAX_RETRIES` | int | `3` | Connection retry attempts |

### Rate Limiting

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_RATE_LIMITS` | string | `""` | Comma-separated `capability:limit` pairs (e.g., `blender.get_objects:100,blender.execute_script:10`) |
| `MCP_RATE_WINDOW_SECONDS` | float | `60.0` | Rate limit window in seconds |

### Payload Protection

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_MAX_PAYLOAD_BYTES` | int | `65536` | Maximum payload size in bytes |
| `MCP_MAX_PAYLOAD_KEYS` | int | `128` | Maximum number of keys in payload |
| `MCP_BLOCKED_CAPABILITIES` | string | `""` | Comma-separated list of blocked capabilities |

### Audit Logging

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_AUDIT_LOG` | string | `""` | Path to audit log file (empty = no file logging) |

### Telemetry

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_TELEMETRY` | string | `false` | Enable anonymous usage telemetry |
| `DISABLE_TELEMETRY` | string | `false` | Explicitly disable all telemetry |

## Configuration Profiles

### Development Mode

Recommended for local development and testing:

```bash
export MCP_ADAPTER=mock
export MCP_LOG_LEVEL=DEBUG
export MCP_ENABLE_SCRIPT_EXECUTE=true
export MCP_MAX_PAYLOAD_BYTES=1048576  # 1MB for testing
export MCP_AUDIT_LOG=/tmp/blender_mcp_audit.jsonl
```

### Production Mode

Recommended for production deployments:

```bash
export MCP_ADAPTER=socket
export MCP_LOG_LEVEL=WARNING
export MCP_ENABLE_SCRIPT_EXECUTE=false
export MCP_MAX_PAYLOAD_BYTES=65536
export MCP_MAX_PAYLOAD_KEYS=128
export MCP_RATE_WINDOW_SECONDS=60
export MCP_AUDIT_LOG=/var/log/blender_mcp/audit.jsonl
```

### High-Security Mode

Recommended for sensitive environments:

```bash
export MCP_ADAPTER=socket
export MCP_LOG_LEVEL=INFO
export MCP_ENABLE_SCRIPT_EXECUTE=false
export MCP_MAX_PAYLOAD_BYTES=16384  # 16KB
export MCP_MAX_PAYLOAD_KEYS=64
export MCP_RATE_LIMITS="blender.execute_operator:30,blender.execute_script:0,blender.import_export:10"
export MCP_RATE_WINDOW_SECONDS=60
export MCP_BLOCKED_CAPABILITIES="blender.execute_script"
export MCP_AUDIT_LOG=/var/log/blender_mcp/audit.jsonl
export DISABLE_TELEMETRY=true
```

## Security Features

### Allowlist

The `Allowlist` class enforces capability access control. Configure via `MCP_BLOCKED_CAPABILITIES` to block specific tools.

### Guardrails

The `Guardrails` class provides input validation:
- Payload size limits
- Key count limits
- Blocked capability enforcement

### Rate Limiting

The `RateLimiter` class prevents abuse:
- Per-capability rate limits
- Configurable time window
- Automatic cleanup of expired entries

### Audit Logging

The `JsonFileAuditLogger` and `MemoryAuditLogger` classes track all capability invocations:
- Timestamp, capability name, success/failure
- Error details on failure
- Log rotation at 10MB with 5 backup files

## Important Notes

1. **Script Execution**: `MCP_ENABLE_SCRIPT_EXECUTE` is disabled by default. Enable only in trusted environments. This capability allows arbitrary Python code execution.

2. **Rate Limits**: Without `MCP_RATE_LIMITS` configured, the default limit is 120 requests per minute per capability.

3. **Audit Logs**: File-based audit logs rotate automatically. Ensure the log directory exists and is writable.

4. **Telemetry**: Telemetry is opt-in. No data is sent unless `MCP_TELEMETRY=true`.

## Error Codes

| Code | Description |
|------|-------------|
| `adapter_timeout` | Connection to Blender addon timed out |
| `adapter_unavailable` | Cannot connect to Blender addon |
| `adapter_empty_response` | No response from Blender addon |
| `adapter_invalid_response` | Invalid JSON in response |
| `rate_limited` | Too many requests in time window |
| `capability_blocked` | Capability is in blocked list |
| `payload_too_large` | Payload exceeds MCP_MAX_PAYLOAD_BYTES |
| `too_many_keys` | Payload has more than MCP_MAX_PAYLOAD_KEYS keys |
