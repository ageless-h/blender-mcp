# -*- coding: utf-8 -*-
import unittest

from blender_mcp.catalog.catalog import CapabilityCatalog, CapabilityMeta
from blender_mcp.core.lifecycle import ServiceLifecycle
from blender_mcp.core.server import MCPServer
from blender_mcp.core.types import Request
from blender_mcp.security.allowlist import Allowlist
from blender_mcp.security.audit import MemoryAuditLogger
from blender_mcp.security.permissions import PermissionPolicy
from blender_mcp.security.rate_limit import RateLimiter


class TestWorkflowScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.lifecycle = ServiceLifecycle()
        self.allowlist = Allowlist({"scene.read", "scene.write"})
        self.permissions = PermissionPolicy({"scene.write": {"scene:write"}})
        self.rate_limiter = RateLimiter({"scene.write": 2})
        self.audit = MemoryAuditLogger()
        self.server = MCPServer(
            lifecycle=self.lifecycle,
            allowlist=self.allowlist,
            permissions=self.permissions,
            rate_limiter=self.rate_limiter,
            audit_logger=self.audit,
        )

    def test_allowed_capability_executes(self) -> None:
        request = Request(capability="scene.read", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertTrue(response.ok)

    def test_capability_discovery_returns_catalog(self) -> None:
        catalog = CapabilityCatalog()
        catalog.register(CapabilityMeta(name="scene.read", description="Read scene"))
        capabilities = list(catalog.list())
        self.assertEqual(len(capabilities), 1)
        self.assertEqual(capabilities[0].name, "scene.read")

    def test_disallowed_capability_rejected(self) -> None:
        request = Request(capability="scene.delete", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "capability_not_allowed")

    def test_missing_scope_rejected(self) -> None:
        request = Request(capability="scene.write", payload={}, scopes=[])
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "missing_scope")

    def test_rate_limit_rejected(self) -> None:
        request = Request(capability="scene.write", payload={}, scopes=["scene:write"])
        self.assertTrue(self.server.handle_request(request).ok)
        self.assertTrue(self.server.handle_request(request).ok)
        response = self.server.handle_request(request)
        self.assertFalse(response.ok)
        self.assertEqual(response.error, "rate_limited")


if __name__ == "__main__":
    unittest.main()
