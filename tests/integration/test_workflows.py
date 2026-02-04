# -*- coding: utf-8 -*-
import unittest

from blender_mcp.catalog.catalog import (
    CapabilityCatalog,
    capability_scope_map,
    minimal_capability_set,
)
from blender_mcp.core.lifecycle import ServiceLifecycle
from blender_mcp.core.server import MCPServer
from blender_mcp.core.types import Request
from blender_mcp.security.allowlist import Allowlist
from blender_mcp.security.audit import MemoryAuditLogger
from blender_mcp.security.permissions import PermissionPolicy
from blender_mcp.security.rate_limit import RateLimiter


class TestWorkflowScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.capabilities = minimal_capability_set()
        self.catalog = CapabilityCatalog()
        for capability in self.capabilities:
            self.catalog.register(capability)
        self.lifecycle = ServiceLifecycle()
        self.allowlist = Allowlist(
            {cap.name for cap in self.capabilities} | {"capabilities.list"}
        )
        self.permissions = PermissionPolicy(capability_scope_map(self.capabilities))
        self.rate_limiter = RateLimiter({"object.read": 2})
        self.audit = MemoryAuditLogger()
        self.server = MCPServer(
            catalog=self.catalog,
            lifecycle=self.lifecycle,
            allowlist=self.allowlist,
            permissions=self.permissions,
            rate_limiter=self.rate_limiter,
            audit_logger=self.audit,
        )

    def test_allowed_capability_executes(self) -> None:
        request = Request(
            capability="scene.read", payload={}, scopes=["scene:read"]
        )
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)

    def test_capability_discovery_returns_catalog(self) -> None:
        request = Request(capability="capabilities.list", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)
        names = {cap["name"] for cap in response.result["capabilities"]}
        expected = {cap.name for cap in self.capabilities}
        self.assertEqual(names, expected)

    def test_disallowed_capability_rejected(self) -> None:
        request = Request(capability="scene.delete", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "capability_not_allowed")

    def test_missing_scope_rejected(self) -> None:
        request = Request(capability="object.read", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "missing_scope")

    def test_rate_limit_rejected(self) -> None:
        request = Request(
            capability="object.read", payload={}, scopes=["object:read"]
        )
        self.assertTrue(self.server.handle_request(request).ok)
        self.assertTrue(self.server.handle_request(request).ok)
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "rate_limited")

    def test_rate_limit_window_reset(self) -> None:
        self.rate_limiter.window_seconds = 0.0
        request = Request(
            capability="object.read", payload={}, scopes=["object:read"]
        )
        self.assertTrue(self.server.handle_request(request).ok)
        self.assertTrue(self.server.handle_request(request).ok)


if __name__ == "__main__":
    unittest.main()
