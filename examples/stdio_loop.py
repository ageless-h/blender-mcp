# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _REPO_ROOT / "src"
if _SRC_ROOT.exists():
    sys.path.insert(0, str(_SRC_ROOT))

from blender_mcp.adapters.base import BlenderAdapter
from blender_mcp.adapters.mock import MockAdapter
from blender_mcp.adapters.socket import SocketAdapter
from blender_mcp.core.lifecycle import ServiceLifecycle
from blender_mcp.core.server import MCPServer
from blender_mcp.catalog.catalog import (
    CapabilityCatalog,
    capability_scope_map,
    minimal_capability_set,
)
from blender_mcp.security.allowlist import Allowlist
from blender_mcp.security.audit import MemoryAuditLogger
from blender_mcp.security.permissions import PermissionPolicy
from blender_mcp.security.rate_limit import RateLimiter
from blender_mcp.transport.stdio import StdioTransport


@dataclass
class ServerBundle:
    server: MCPServer
    transport: StdioTransport


def build_adapter() -> BlenderAdapter | None:
    """Build adapter based on environment configuration.
    
    Environment variables:
        MCP_ADAPTER: 'mock', 'socket', or unset (no adapter)
        MCP_SOCKET_HOST: Socket host (default: 127.0.0.1)
        MCP_SOCKET_PORT: Socket port (default: 9876)
    """
    adapter_type = os.environ.get("MCP_ADAPTER", "").lower()
    
    if adapter_type == "mock":
        return MockAdapter()
    elif adapter_type == "socket":
        host = os.environ.get("MCP_SOCKET_HOST", "127.0.0.1")
        port = int(os.environ.get("MCP_SOCKET_PORT", "9876"))
        return SocketAdapter(host=host, port=port)
    
    return None


def build_server(adapter: BlenderAdapter | None = None) -> ServerBundle:
    audit_logger = MemoryAuditLogger()
    capabilities = minimal_capability_set()
    allowlist = Allowlist(
        {cap.name for cap in capabilities} | {"capabilities.list"},
        audit_logger=audit_logger,
    )
    catalog = CapabilityCatalog()
    for capability in capabilities:
        catalog.register(capability)
    server = MCPServer(
        catalog=catalog,
        lifecycle=ServiceLifecycle(),
        allowlist=allowlist,
        permissions=PermissionPolicy(capability_scope_map(capabilities)),
        rate_limiter=RateLimiter(
            {capability: 10 for capability in allowlist.allowed},
            window_seconds=60.0,
        ),
        audit_logger=audit_logger,
        adapter=adapter,
    )
    return ServerBundle(server=server, transport=StdioTransport())


def run_stdio_loop() -> int:
    adapter = build_adapter()
    bundle = build_server(adapter=adapter)
    bundle.server.handle_transport(bundle.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_stdio_loop())
