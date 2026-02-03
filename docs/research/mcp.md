# MCP Overview and Applicability

## Summary
The Model Context Protocol (MCP) defines a structured way for agents to call tools and services through a stable server interface. For Blender MCP, the protocol expectations imply a clear request/response contract, tool discovery, and strict boundary between core server behavior and integration adapters.

## Applicability to Blender MCP
- Use MCP-style capability discovery to expose Blender features as named capabilities.
- Enforce explicit allowlists and permission scopes for any tool execution.
- Keep transport and protocol handling in a core layer separate from Blender adapters.
- Prefer deterministic error handling and observability for agent safety.

## Best Practices to Apply
- Strongly typed capability schemas and stable naming conventions.
- Clear lifecycle states for server readiness and shutdown.
- Audit logging for all actions triggered by agents.
- Rate limiting and resource guards to protect Blender sessions.
