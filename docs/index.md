# Blender MCP Documentation

> Quick navigation to all documentation resources.

## Getting Started

- [Quick Start Guide](quick-start.md) - Install and start using Blender MCP in 5 minutes

## Tool Architecture

The 29 tools are organized into four layers:

| Layer | Doc | Description |
|-------|-----|-------------|
| **Perception** (11 tools) | [perception-layer.md](tools/perception-layer.md) | Read Blender state |
| **Declarative Write** (3 tools) | [declarative-write-layer.md](tools/declarative-write-layer.md) | Node/Animation/VSE editing |
| **Imperative Write** (9 tools) | [imperative-write-layer.md](tools/imperative-write-layer.md) | Object/Material/Modifier operations |
| **Fallback** (3 tools) | [operator-tool.md](tools/operator-tool.md), [script-tool.md](tools/script-tool.md) | Escape hatches |

For complete architecture details, see [tools/overview.md](tools/overview.md).

## MCP Client Configuration

| Client | Config |
|--------|--------|
| Antigravity | [antigravity.md](clients/antigravity.md) |
| Claude Code | [claude-code.md](clients/claude-code.md) |
| Cursor | [cursor.md](clients/cursor.md) |
| VS Code Copilot | [vs-code-copilot.md](clients/vs-code-copilot.md) |
| Windsurf | [windsurf.md](clients/windsurf.md) |

[→ All 18 clients](clients/)

## Reference

| Topic | Doc |
|-------|-----|
| Architecture | [architecture/](architecture/) |
| Versioning | [versioning/support-matrix.md](versioning/support-matrix.md) |
| Testing | [testing/](testing/) |
| Research | [research/](research/) |

## Development

- [Contributing](../CONTRIBUTING.md)
