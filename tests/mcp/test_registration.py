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
        """Test that tools/list includes all 26 new tools with blender_ prefix."""
        response = self._tools_list()
        result = response["result"]
        tools = result["tools"]
        
        tool_names = {tool["name"] for tool in tools}
        
        # All 26 tools in the new architecture
        expected_tools = [
            # Perception (11)
            "blender_get_objects", "blender_get_object_data", "blender_get_node_tree",
            "blender_get_animation_data", "blender_get_materials", "blender_get_scene",
            "blender_get_collections", "blender_get_armature_data", "blender_get_images",
            "blender_capture_viewport", "blender_get_selection",
            # Declarative (3)
            "blender_edit_nodes", "blender_edit_animation", "blender_edit_sequencer",
            # Imperative (9)
            "blender_create_object", "blender_modify_object", "blender_manage_material",
            "blender_manage_modifier", "blender_manage_collection", "blender_manage_uv",
            "blender_manage_constraints", "blender_manage_physics", "blender_setup_scene",
            # Fallback (3)
            "blender_execute_operator", "blender_execute_script", "blender_import_export",
        ]
        
        for tool in expected_tools:
            self.assertIn(
                tool, tool_names, f"Tool '{tool}' should be present"
            )
        
        self.assertEqual(len(tools), 26, "Should have exactly 26 tools")

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
        # Test new tool name
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "blender_get_object_data", "arguments": {"name": "Cube"}},
        }

        response = self._send_request(request)

        self.assertIn("result", response, "Response should have result field")
        result = response["result"]
        self.assertIn("content", result, "tools/call result should include content")
        self.assertIsInstance(result["content"], list)
        self.assertFalse(response.get("error"), "tools/call should not return error")

    def test_tools_call_legacy_name_compatibility(self):
        """Test that legacy tool names (data.read) are resolved to new names."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "data.read", "arguments": {"payload": {}}},
        }

        response = self._send_request(request)

        self.assertIn("result", response, "Response should have result field")
        result = response["result"]
        self.assertIn("content", result, "Legacy tools/call should still work")

    def test_tools_have_annotations(self):
        """Test that all tools have MCP annotations."""
        response = self._tools_list()
        tools = response["result"]["tools"]

        for tool in tools:
            self.assertIn("annotations", tool, f"Tool '{tool['name']}' should have annotations")
            ann = tool["annotations"]
            self.assertIn("readOnlyHint", ann, f"Tool '{tool['name']}' should have readOnlyHint")
            self.assertIn("destructiveHint", ann)
            self.assertIn("idempotentHint", ann)
            self.assertIn("openWorldHint", ann)

    def test_tools_have_flat_schemas(self):
        """Test that tool schemas use flat params (no payload wrapper)."""
        response = self._tools_list()
        tools = response["result"]["tools"]

        for tool in tools:
            schema = tool["inputSchema"]
            self.assertEqual(schema["type"], "object", f"Tool '{tool['name']}' schema should be object")
            props = schema.get("properties", {})
            self.assertNotIn("payload", props,
                f"Tool '{tool['name']}' should NOT have payload wrapper")
            self.assertFalse(
                schema.get("additionalProperties", True),
                f"Tool '{tool['name']}' should have additionalProperties=false"
            )

    def test_perception_tools_are_readonly(self):
        """Test that all perception layer tools are marked readOnly."""
        response = self._tools_list()
        tools = response["result"]["tools"]

        perception_tools = [
            "blender_get_objects", "blender_get_object_data", "blender_get_node_tree",
            "blender_get_animation_data", "blender_get_materials", "blender_get_scene",
            "blender_get_collections", "blender_get_armature_data", "blender_get_images",
            "blender_capture_viewport", "blender_get_selection",
        ]

        tool_map = {t["name"]: t for t in tools}
        for name in perception_tools:
            tool = tool_map[name]
            self.assertTrue(
                tool["annotations"]["readOnlyHint"],
                f"Perception tool '{name}' should have readOnlyHint=true"
            )
            self.assertTrue(
                tool["annotations"]["idempotentHint"],
                f"Perception tool '{name}' should have idempotentHint=true"
            )

    def test_initialize_includes_prompts_capability(self):
        """Test that initialize advertises prompts capability."""
        response = self._initialize()
        result = response["result"]
        capabilities = result["capabilities"]
        self.assertIn("prompts", capabilities, "Should advertise prompts capability")

    def test_prompts_list(self):
        """Test that prompts/list returns 7 workflow prompts."""
        request = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "prompts/list",
            "params": {},
        }
        response = self._send_request(request)
        self.assertIn("result", response)
        prompts = response["result"]["prompts"]
        self.assertEqual(len(prompts), 7, "Should have 7 workflow prompts")

        prompt_names = {p["name"] for p in prompts}
        expected = {
            "blender-scene-setup", "blender-material-create", "blender-model-asset",
            "blender-animate", "blender-composite", "blender-render-output",
            "blender-diagnose",
        }
        self.assertEqual(prompt_names, expected)

    def test_prompts_get(self):
        """Test that prompts/get returns structured messages."""
        request = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "prompts/get",
            "params": {
                "name": "blender-diagnose",
            },
        }
        response = self._send_request(request)
        self.assertIn("result", response)
        result = response["result"]
        self.assertIn("messages", result)
        self.assertGreater(len(result["messages"]), 0)
        self.assertEqual(result["messages"][0]["role"], "user")

    def test_tool_descriptions_have_cross_references(self):
        """Test that tool descriptions include cross-reference guidance."""
        response = self._tools_list()
        tools = response["result"]["tools"]
        tool_map = {t["name"]: t for t in tools}

        # blender_execute_operator should reference specialized tools
        desc = tool_map["blender_execute_operator"]["description"]
        self.assertIn("blender_manage_uv", desc,
            "execute_operator should cross-reference blender_manage_uv")

        # blender_manage_material should reference blender_edit_nodes
        desc = tool_map["blender_manage_material"]["description"]
        self.assertIn("blender_edit_nodes", desc,
            "manage_material should cross-reference blender_edit_nodes")


if __name__ == "__main__":
    unittest.main()
