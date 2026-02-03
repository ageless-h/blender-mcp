# Blender MCP Example Workflows

## Example 1: Minimal Stdio Loop
Run:

```
python -m examples.stdio_loop
```

Send:

```
{ "capability": "scene.read", "payload": {}, "scopes": [] }
```

## Example 2: Safe Scene Update
Use a scoped capability to modify scene properties with allowlist enforcement.

## Example 3: Render Pipeline
Run a render workflow with explicit permissions and audit logging.
