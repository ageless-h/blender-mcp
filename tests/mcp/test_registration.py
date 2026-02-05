"""MCP registration tests using subprocess to simulate real client behavior."""

import json
import os
import subprocess
import sys
import unittest


class MCPRegistrationTest(unittest.TestCase):
    """Test MCP protocol registration functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up subprocess environment for MCP testing."""
        cls.env = os.environ.copy()
        cls.env["MCP_ADAPTER"] = "mock"
        # Ensure src is in PYTHONPATH
        src_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
        cls.env["PYTHONPATH"] = os.path.abspath(src_path)

    def _send_request(self, request: dict) -> dict:
        """Send a JSON-RPC request to the MCP server and return the response."""
        request_line = json.dumps(request) + "\n"
        
        proc = subprocess.Popen(
            [sys.executable, "-m", "blender_mcp.mcp_protocol"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
            text=True,
        )
        
        stdout, stderr = proc.communicate(input=request_line, timeout=10)
        
        # Parse the first line of output as JSON response
        lines = stdout.strip().split("\n")
        if not lines or not lines[0]:
            raise RuntimeError(f"No response received. stderr: {stderr}")
        
        return json.loads(lines[0])

    def _initialize(self) -> dict:
        """Send initialize request and return response."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }
        return self._send_request(request)

    def _tools_list(self) -> dict:
        """Send tools/list request and return response."""
        # For stateless testing, we send initialize + tools/list in sequence
        # Since each subprocess is fresh, we just send tools/list directly
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
        return self._send_request(request)

    def test_initialize_returns_server_info(self):
        """Test that initialize response contains serverInfo with name and version."""
        response = self._initialize()
        
        self.assertIn("result", response, "Response should have result field")
        result = response["result"]
        
        self.assertIn("serverInfo", result, "Result should contain serverInfo")
        server_info = result["serverInfo"]
        
        self.assertIn("name", server_info, "serverInfo should have name")
        self.assertIn("version", server_info, "serverInfo should have version")
        self.assertTrue(server_info["name"], "serverInfo.name should not be empty")
        self.assertTrue(server_info["version"], "serverInfo.version should not be empty")

    def test_initialize_returns_capabilities(self):
        """Test that initialize response contains capabilities object."""
        response = self._initialize()
        
        self.assertIn("result", response, "Response should have result field")
        result = response["result"]
        
        self.assertIn("capabilities", result, "Result should contain capabilities")
        self.assertIsInstance(result["capabilities"], dict, "capabilities should be an object")

    def test_tools_list_returns_non_empty_array(self):
        """Test that tools/list returns a non-empty tools array."""
        response = self._tools_list()
        
        self.assertIn("result", response, "Response should have result field")
        result = response["result"]
        
        self.assertIn("tools", result, "Result should contain tools")
        tools = result["tools"]
        
        self.assertIsInstance(tools, list, "tools should be an array")
        self.assertGreater(len(tools), 0, "tools array should not be empty")

    def test_tools_list_contains_core_tools(self):
        """Test that tools/list includes all core tools."""
        response = self._tools_list()
        result = response["result"]
        tools = result["tools"]
        
        tool_names = {tool["name"] for tool in tools}
        
        core_tools = [
            "data.create",
            "data.read",
            "data.write",
            "data.delete",
            "data.list",
            "data.link",
            "operator.execute",
            "info.query",
        ]
        
        for core_tool in core_tools:
            self.assertIn(
                core_tool, tool_names, f"Core tool '{core_tool}' should be present"
            )

    def test_jsonrpc_compliance(self):
        """Test that responses conform to JSON-RPC 2.0 specification."""
        # Test initialize response
        init_response = self._initialize()
        
        self.assertEqual(
            init_response.get("jsonrpc"), "2.0", "Response should have jsonrpc: 2.0"
        )
        self.assertEqual(
            init_response.get("id"), 1, "Response id should match request id"
        )
        
        # Response should have either result or error, not both
        has_result = "result" in init_response
        has_error = "error" in init_response
        self.assertTrue(
            has_result != has_error,
            "Response should have either result or error, not both",
        )
        
        # Test tools/list response
        tools_response = self._tools_list()
        
        self.assertEqual(
            tools_response.get("jsonrpc"), "2.0", "Response should have jsonrpc: 2.0"
        )
        self.assertEqual(
            tools_response.get("id"), 2, "Response id should match request id"
        )

    def test_tools_call_uses_mock_adapter(self):
        """Test that tools/call works with mock adapter (no Blender required)."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "data.read", "arguments": {"payload": {}}},
        }

        response = self._send_request(request)

        self.assertIn("result", response, "Response should have result field")
        result = response["result"]
        self.assertIn("content", result, "tools/call result should include content")
        self.assertIsInstance(result["content"], list)
        self.assertFalse(response.get("error"), "tools/call should not return error")


if __name__ == "__main__":
    unittest.main()
