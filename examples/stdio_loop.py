# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass

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


def build_server() -> ServerBundle:
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
    )
    return ServerBundle(server=server, transport=StdioTransport())


def run_stdio_loop() -> int:
    bundle = build_server()
    bundle.server.handle_transport(bundle.transport)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_stdio_loop())
