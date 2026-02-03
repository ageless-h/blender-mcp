# Reference Projects Review

## ahujasid/blender-mcp
- Highlights a direct bridge between MCP requests and Blender operations.
- Demonstrates a minimal adapter approach, but lacks long-term version strategy.
- Useful for early capability mapping and example workflows.

## chrome-devtools-mcp
- Emphasizes a stable tool registry and strict request routing.
- Shows clear separation between protocol handling and platform-specific adapters.
- Provides a model for capability catalog organization and auditing.

## Applicability to Blender MCP
- Reuse adapter boundary patterns and tool registry structure.
- Extend with security guardrails and version compatibility policy.
- Add multi-version integration test harness and evaluation gate.
