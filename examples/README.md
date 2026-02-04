# Blender MCP Example Workflows

Each new capability, and each capability change that adds new behavior, MUST include at least one runnable example under `examples/`.

## Example 1: Minimal Stdio Loop
Run:

```python
python -m examples.stdio_loop
```

Send:

```json
{ "jsonrpc": "2.0", "id": 1, "method": "scene.read", "params": {"payload": {}, "scopes": ["scene:read"]} }
```

## Example 2: Safe Scene Update
Use a scoped capability to modify scene properties with allowlist enforcement.

## Example 3: Render Pipeline
Run a render workflow with explicit permissions and audit logging.
