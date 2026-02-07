# -*- coding: utf-8 -*-
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_mcp.mcp_protocol import MCPServer


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = MCPServer()

    def test_initialize(self):
        req = {"method": "initialize", "id": 1, "params": {}}
        resp = self.server.handle_request(req)
        self.assertEqual(resp["jsonrpc"], "2.0")
        self.assertEqual(resp["id"], 1)
        self.assertIn("capabilities", resp["result"])
        self.assertIn("serverInfo", resp["result"])

    def test_tools_list(self):
        req = {"method": "tools/list", "id": 2, "params": {}}
        resp = self.server.handle_request(req)
        self.assertIn("tools", resp["result"])
        self.assertGreater(len(resp["result"]["tools"]), 0)

    def test_tools_call_unknown(self):
        result = self.server.tools_call("nonexistent_tool", {})
        self.assertTrue(result["isError"])

    def test_tools_call_invalid_name(self):
        result = self.server.tools_call("", {})
        self.assertTrue(result["isError"])

    def test_tools_call_none_name(self):
        result = self.server.tools_call(None, {})
        self.assertTrue(result["isError"])

    def test_tools_call_non_dict_args(self):
        result = self.server.tools_call("nonexistent", "bad")
        self.assertTrue(result["isError"])

    def test_prompts_list(self):
        req = {"method": "prompts/list", "id": 3, "params": {}}
        resp = self.server.handle_request(req)
        self.assertIn("prompts", resp["result"])

    def test_prompts_get_not_found(self):
        result = self.server.prompts_get("nonexistent_prompt")
        self.assertIn("error", result)

    def test_prompts_get_invalid_name(self):
        result = self.server.prompts_get("")
        self.assertIn("error", result)

    def test_unknown_method(self):
        req = {"method": "unknown/method", "id": 4, "params": {}}
        resp = self.server.handle_request(req)
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32601)

    def test_notification_returns_none(self):
        req = {"method": "notifications/something", "params": {}}
        resp = self.server.handle_request(req)
        self.assertIsNone(resp)


if __name__ == "__main__":
    unittest.main()
