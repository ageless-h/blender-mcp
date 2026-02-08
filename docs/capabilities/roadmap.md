# Roadmap

> Last Updated: 2026-02-08

This document outlines planned features and enhancements for Blender MCP.

---

## 🔵 P3: Future Enhancements

### Performance & Efficiency

#### batch_execute - Batch Tool Execution

**Priority**: High  
**Expected Impact**: 10-100x performance improvement for bulk operations

**Description**:
Implement batch execution mechanism to process multiple tool requests in a single round-trip, reducing network overhead for common workflows like creating multiple objects or applying materials to many meshes.

**Reference**: Unity MCP's batch_execute implementation

**Implementation Plan**:
- [ ] Design batch request/response schema
- [ ] Implement request batching logic in MCP server
- [ ] Update addon to handle batched operations
- [ ] Add batch-specific error handling
- [ ] Document batch execution patterns

---

### MCP Protocol Features

#### MCP Resources - Asset Directory Exposure

**Priority**: Medium

**Description**:
Expose Blender's internal asset library (Materials, Node Groups, Scenes, etc.) through MCP Resources API, allowing LLMs to browse and reference existing assets.

**Use Cases**:
- LLM can discover available materials before applying
- Reference existing node groups without recreating
- Browse saved scenes for context

**Implementation Plan**:
- [ ] Define resource categories (materials, node_groups, scenes, etc.)
- [ ] Implement `list_resources` handler
- [ ] Implement `read_resource` handler
- [ ] Add filtering and search capabilities
- [ ] Document resource URIs structure

#### MCP Progress - Long-Running Operation Feedback

**Priority**: Medium

**Description**:
Add progress reporting for long-running operations (rendering, baking, complex geometry processing) using MCP Progress protocol.

**Use Cases**:
- Rendering operations can report % complete
- Physics simulation baking progress
- Large mesh processing feedback

**Implementation Plan**:
- [ ] Identify long-running operations
- [ ] Integrate progress callbacks
- [ ] Map Blender progress to MCP progress schema
- [ ] Test with rendering workflow

---

### Transport Layer

#### WebSocket Transport

**Priority**: Medium

**Description**:
Add WebSocket transport layer to support alternative connection methods beyond stdio, enabling:
- Real-time bi-directional communication
- Web-based clients
- Better integration with browser-based LLM interfaces

**Implementation Plan**:
- [ ] Design WebSocket protocol specification
- [ ] Implement `src/blender_mcp/transport/websocket.py`
- [ ] Update addon to support WebSocket connections
- [ ] Add connection management (reconnect, keepalive)
- [ ] Document WebSocket deployment options

---

### External Integrations

#### PolyHaven Integration

**Priority**: Low

**Description**:
Add integration to search and download free assets from PolyHaven (HDRI environments, textures, models) directly within Blender.

**Implementation Plan**:
- [ ] Create `src/blender_mcp_addon/integrations/polyhaven.py`
- [ ] Implement PolyHaven API client
- [ ] Add search by category, resolution, tags
- [ ] Implement download and import workflow
- [ ] Add cache management for downloaded assets

**Reference**: [PolyHaven API](https://api.polyhaven.com/)

#### Sketchfab Integration

**Priority**: Low

**Description**:
Add integration to search and import models from Sketchfab's free model library.

**Implementation Plan**:
- [ ] Create `src/blender_mcp_addon/integrations/sketchfab.py`
- [ ] Implement Sketchfab API client
- [ ] Add search by category, style, tags
- [ ] Implement import workflow (GLB/GLTF)
- [ ] Handle licensing attribution

**Reference**: [Sketchfab API](https://docs.sketchfab.com/)

---

## Contribution Guidelines

Want to help implement these features?

1. Check the [Contributing Guide](../CONTRIBUTING.md) (if available)
2. Review the [Architecture Documentation](../architecture/) for implementation context
3. Open an issue or PR to discuss your approach
4. Reference this roadmap in your PR description

---

## Version Planning

| Version | Planned Features | Target Date |
|---------|------------------|-------------|
| v0.2.0 | batch_execute, MCP Resources | Q1 2026 |
| v0.3.0 | WebSocket transport, MCP Progress | Q2 2026 |
| v0.4.0 | PolyHaven integration | Q3 2026 |
| v0.5.0 | Sketchfab integration | Q4 2026 |

*Note: Dates are estimates and subject to change based on community feedback and priorities.*
