# -*- coding: utf-8 -*-
"""End-to-end integration tests for MCP request flow."""

from __future__ import annotations

import os
import unittest

os.environ["MCP_ADAPTER"] = "mock"

from blender_mcp.mcp_protocol import MCPServer


class TestE2EFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = MCPServer()

    def _rpc(self, method, params=None, req_id=1):
        req = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}
        return self.server.handle_request(req)

    def test_initialize_then_tools_list(self):
        r1 = self._rpc(
            "initialize",
            {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}},
            1,
        )
        self.assertIn("serverInfo", r1["result"])
        r2 = self._rpc("tools/list", {}, 2)
        self.assertEqual(len(r2["result"]["tools"]), 27)

    def test_tools_call_perception(self):
        resp = self._rpc("tools/call", {"name": "blender_get_scene", "arguments": {"include": ["stats"]}}, 3)
        self.assertIn("content", resp["result"])
        self.assertNotIn("isError", resp["result"])

    def test_tools_call_imperative(self):
        resp = self._rpc(
            "tools/call", {"name": "blender_create_object", "arguments": {"name": "Cube", "object_type": "MESH"}}, 4
        )
        self.assertIn("content", resp["result"])

    def test_tools_call_fallback(self):
        resp = self._rpc("tools/call", {"name": "blender_execute_script", "arguments": {"code": "print(1)"}}, 5)
        self.assertIn("content", resp["result"])

    def test_tools_call_unknown_returns_error(self):
        resp = self._rpc("tools/call", {"name": "nonexistent", "arguments": {}}, 6)
        self.assertTrue(resp["result"]["isError"])

    def test_prompts_list_then_get(self):
        r1 = self._rpc("prompts/list", {}, 7)
        self.assertIn("prompts", r1["result"])
        names = [p["name"] for p in r1["result"]["prompts"]]
        self.assertIn("blender-diagnose", names)
        r2 = self._rpc("prompts/get", {"name": "blender-diagnose"}, 8)
        self.assertIn("messages", r2["result"])

    def test_unknown_tool_returns_error(self):
        resp = self._rpc("tools/call", {"name": "data.read", "arguments": {}}, 9)
        self.assertTrue(resp["result"].get("isError"))

    def test_notification_no_response(self):
        resp = self._rpc("notifications/initialized", {}, None)
        self.assertIsNone(resp)

    def test_unknown_method_error(self):
        resp = self._rpc("unknown/method", {}, 10)
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32601)

    def test_response_id_matches_request(self):
        resp = self._rpc("tools/list", {}, 42)
        self.assertEqual(resp["id"], 42)

    def test_jsonrpc_version(self):
        resp = self._rpc("initialize", {}, 1)
        self.assertEqual(resp["jsonrpc"], "2.0")


if __name__ == "__main__":
    unittest.main()
