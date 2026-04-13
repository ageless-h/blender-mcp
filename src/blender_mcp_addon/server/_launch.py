# -*- coding: utf-8 -*-
"""Launch script for Blender's --python flag.

Starts the MCP socket server inside a running Blender process.
Used by integration tests and the BlenderProcessHarness.

Usage:
    blender --background --python _launch.py
    blender --background --python _launch.py -- --port 9877
"""

from __future__ import annotations

import os
import sys


def _parse_port() -> int:
    """Extract port from command-line args or environment."""
    argv = sys.argv
    try:
        dash_idx = argv.index("--")
        remaining = argv[dash_idx + 1 :]
        for i, arg in enumerate(remaining):
            if arg == "--port" and i + 1 < len(remaining):
                return int(remaining[i + 1])
    except (ValueError, IndexError):
        pass

    return int(os.environ.get("MCP_SOCKET_PORT", "9876"))


def main() -> None:
    """Register the addon modules and start the socket server."""
    # Ensure the addon's parent directory is on sys.path so that
    # `blender_mcp_addon` can be imported even without a full install.
    addon_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    src_root = os.path.dirname(addon_root)
    if src_root not in sys.path:
        sys.path.insert(0, src_root)

    from blender_mcp_addon.server.socket_server import (  # noqa: E402
        _main_thread_poll,
        is_server_running,
        start_socket_server,
        stop_socket_server,
    )

    if is_server_running():
        stop_socket_server()

    port = _parse_port()
    host = os.environ.get("MCP_SOCKET_HOST", "127.0.0.1")

    import time

    result = start_socket_server(host=host, port=port)
    if not result.get("ok"):
        print(f"MCP_SOCKET_FAILED {result}", flush=True)
        sys.exit(1)

    print(f"MCP_SOCKET_READY {host}:{port}", flush=True)

    while is_server_running():
        _main_thread_poll()
        time.sleep(0.05)


if __name__ == "__main__":
    main()
