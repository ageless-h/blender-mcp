# Blender MCP

## Minimal Runnable Loop

1. Install the package:
   - `pip install .`
2. Run the stdio example:
   - `python -m examples.stdio_loop`
3. Send a JSON line on stdin:
   - `{ "capability": "scene.read", "payload": {}, "scopes": [] }`
4. Observe a JSON response on stdout.
