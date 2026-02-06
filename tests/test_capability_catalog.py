# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_mcp.catalog.catalog import (
    CapabilityCatalog,
    CapabilityMeta,
    capability_availability,
    capability_scope_map,
    capability_to_dict,
    minimal_capability_set,
)
from blender_mcp.core.lifecycle import ServiceLifecycle
from blender_mcp.core.server import MCPServer
from blender_mcp.core.types import Request
from blender_mcp.security.allowlist import Allowlist
from blender_mcp.security.audit import MemoryAuditLogger
from blender_mcp.security.permissions import PermissionPolicy
from blender_mcp.security.rate_limit import RateLimiter


class TestCapabilityCatalog(unittest.TestCase):
    def test_minimal_capability_set_contains_expected(self) -> None:
        capabilities = minimal_capability_set()
        names = {cap.name for cap in capabilities}
        self.assertEqual(
            names,
            {
                # Data layer tools (CRUD for all Blender data types)
                "data.create",
                "data.read",
                "data.write",
                "data.delete",
                "data.list",
                "data.link",
                # Operator layer tool
                "operator.execute",
                # Info layer tool
                "info.query",
                # Optional dangerous tool (disabled by default)
                "script.execute",
                # Legacy capabilities (deprecated, for backward compatibility)
                "scene.read",
                "scene.write",
            },
        )
        for cap in capabilities:
            self.assertEqual(cap.min_version, "4.2")
            self.assertTrue(cap.scopes)


class TestCapabilityDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        self.capabilities = minimal_capability_set()
        self.catalog = CapabilityCatalog()
        for capability in self.capabilities:
            self.catalog.register(capability)
        self.server = MCPServer(
            catalog=self.catalog,
            lifecycle=ServiceLifecycle(),
            allowlist=Allowlist(
                {cap.name for cap in self.capabilities} | {"capabilities.list"}
            ),
            permissions=PermissionPolicy(capability_scope_map(self.capabilities)),
            rate_limiter=RateLimiter({}, window_seconds=60.0),
            audit_logger=MemoryAuditLogger(),
        )

    def test_capabilities_list_returns_catalog(self) -> None:
        request = Request(capability="capabilities.list", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)
        names = {cap["name"] for cap in response.result["capabilities"]}
        self.assertEqual(names, {cap.name for cap in self.capabilities})

    def test_capabilities_list_availability_by_version(self) -> None:
        request = Request(
            capability="capabilities.list",
            payload={"blender_version": "4.0"},
            scopes=[],
        )
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)
        entries = response.result["capabilities"]
        self.assertTrue(all(entry["available"] is False for entry in entries))
        self.assertTrue(
            all(entry["unavailable_reason"] == "version_below_min" for entry in entries)
        )

        request_ok = Request(
            capability="capabilities.list",
            payload={"blender_version": "4.2"},
            scopes=[],
        )
        response_ok = self.server.handle_request(request_ok)
        self.assertTrue(response_ok.ok)
        entries_ok = response_ok.result["capabilities"]
        self.assertTrue(all(entry["available"] is True for entry in entries_ok))


if __name__ == "__main__":
    unittest.main()
