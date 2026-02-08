# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from blender_mcp.adapters.mock import MockAdapter
from blender_mcp.catalog.catalog import (
    CapabilityCatalog,
    capability_scope_map,
    minimal_capability_set,
)
from blender_mcp.core.lifecycle import ServiceLifecycle
from blender_mcp.core.server import MCPServer
from blender_mcp.security.allowlist import Allowlist
from blender_mcp.security.audit import MemoryAuditLogger
from blender_mcp.security.permissions import PermissionPolicy
from blender_mcp.security.rate_limit import RateLimiter


@dataclass
class IntegrationHarness:
    server: MCPServer
    audit: MemoryAuditLogger
    rate_limiter: RateLimiter
    adapter: MockAdapter


def build_integration_harness(
    *,
    rate_limits: Mapping[str, int] | None = None,
    window_seconds: float = 60.0,
    allowed_capabilities: Iterable[str] | None = None,
) -> IntegrationHarness:
    capabilities = minimal_capability_set()
    catalog = CapabilityCatalog()
    for capability in capabilities:
        catalog.register(capability)

    allowlist_capabilities = (
        {cap.name for cap in capabilities} | {"capabilities.list"}
        if allowed_capabilities is None
        else set(allowed_capabilities)
    )

    audit = MemoryAuditLogger()

    rate_limiter = RateLimiter(
        dict({"blender.get_object_data": 2} if rate_limits is None else rate_limits),
        window_seconds=window_seconds,
    )

    adapter = MockAdapter()

    server = MCPServer(
        catalog=catalog,
        lifecycle=ServiceLifecycle(),
        allowlist=Allowlist(allowlist_capabilities),
        permissions=PermissionPolicy(capability_scope_map(capabilities)),
        rate_limiter=rate_limiter,
        audit_logger=audit,
        adapter=adapter,
    )

    return IntegrationHarness(server=server, audit=audit, rate_limiter=rate_limiter, adapter=adapter)
