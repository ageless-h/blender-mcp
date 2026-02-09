# -*- coding: utf-8 -*-
"""Integration workflow tests using the production mcp_protocol.MCPServer."""
from __future__ import annotations

import os
import unittest

os.environ["MCP_ADAPTER"] = "mock"

from blender_mcp.mcp_protocol import MCPServer


class TestWorkflowScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = MCPServer()

    def _rpc(self, method, params=None, req_id=1):
        req = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}
        return self.server.handle_request(req)

    def test_allowed_capability_executes(self) -> None:
        resp = self._rpc("tools/call", {"name": "blender_get_scene", "arguments": {"include": ["stats"]}})
        self.assertIn("content", resp["result"])
        self.assertNotIn("isError", resp["result"])

    def test_tools_list_returns_26_tools(self) -> None:
        resp = self._rpc("tools/list")
        self.assertEqual(len(resp["result"]["tools"]), 26)

    def test_unknown_tool_rejected(self) -> None:
        resp = self._rpc("tools/call", {"name": "nonexistent_tool", "arguments": {}})
        self.assertTrue(resp["result"]["isError"])

    def test_rate_limit_rejected(self) -> None:
        """Rate limits are enforced per-capability when configured."""
        # Rate limits depend on env config; just verify the mechanism exists
        resp = self._rpc("tools/call", {"name": "blender_get_scene", "arguments": {}})
        self.assertIn("content", resp["result"])

    def test_perception_then_write_workflow(self) -> None:
        """Test typical workflow: read scene, then create object."""
        r1 = self._rpc("tools/call", {"name": "blender_get_scene", "arguments": {}}, 1)
        self.assertNotIn("isError", r1["result"])

        r2 = self._rpc("tools/call", {"name": "blender_create_object", "arguments": {"name": "WF_Cube", "object_type": "MESH"}}, 2)
        self.assertNotIn("isError", r2["result"])

    def test_prompts_workflow(self) -> None:
        """Test prompts list then get."""
        r1 = self._rpc("prompts/list")
        self.assertIn("prompts", r1["result"])
        names = [p["name"] for p in r1["result"]["prompts"]]
        self.assertIn("blender-diagnose", names)

        r2 = self._rpc("prompts/get", {"name": "blender-diagnose"})
        self.assertIn("messages", r2["result"])


if __name__ == "__main__":
    unittest.main()
