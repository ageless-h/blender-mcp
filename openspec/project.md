# Project Context

## Purpose
MCP server for AI-assisted Blender automation. Two-process architecture: MCP server (PyPI) talks to Blender addon over TCP.

## Tech Stack
- Python >=3.11
- MCP protocol (stdio/SSE)
- Zero runtime dependencies

## Architecture
- `src/blender_mcp/` — MCP server (published to PyPI)
- `src/blender_mcp_addon/` — Blender addon (runs inside Blender)
- 26 tools, 10 prompts, 37 registered handlers

## Conventions
- Ruff: line-length 120, select E/F/W/I
- `from __future__ import annotations` in every file
- unittest runner (NOT pytest)
- See root `AGENTS.md` for full details

## Constraints
- Avoid private Blender APIs
- Never import `blender_mcp_addon` from `blender_mcp` (separate processes)
- All addon writes go through `_push_undo_step()`
