# Blender Plugin Boundary

> 更新日期: 2026-02-08

## 双包架构

| 包 | 路径 | 运行环境 | 职责 |
|----|------|----------|------|
| blender_mcp | src/blender_mcp/ | 任意 Python | MCP 协议, Schema, 适配器 |
| blender_mcp_addon | src/blender_mcp_addon/ | Blender | bpy, 能力执行, Socket |

## Minimal Validation
Use `scripts/validate_plugin_boundary.py` to validate the entrypoint contract.

## Ownership Rules
- The core owns protocol handling, security, and capability dispatch.
- The plugin owns Blender-specific execution and access to bpy.

## Compatibility
Contract versions must be forward compatible within a major version. Breaking changes require a major version bump.
