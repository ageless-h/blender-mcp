# -*- coding: utf-8 -*-
"""Example: run the MCP server via stdio.

This is a thin wrapper around the production entry point.
Set MCP_ADAPTER=mock for testing without Blender, or
MCP_ADAPTER=socket (default) to connect to a running Blender addon.

Usage:
    python -m examples.stdio_loop
"""
from __future__ import annotations

from . import _pathfix  # noqa: F401 — ensure src/ is on sys.path

from blender_mcp.mcp_protocol import run_mcp_server


def run_stdio_loop() -> int:
    return run_mcp_server()


if __name__ == "__main__":
    raise SystemExit(run_stdio_loop())
