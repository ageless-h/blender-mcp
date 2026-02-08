# -*- coding: utf-8 -*-
"""Tests for the 3 declarative write layer tools."""
import json
import os
import unittest

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ["MCP_ADAPTER"] = "mock"

from blender_mcp.mcp_protocol import MCPServer


class _ToolTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = MCPServer()

    def _call(self, name, args=None):
        return self.server.tools_call(name, args or {})

    def _assert_success(self, result):
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], list)
        self.assertGreater(len(result["content"]), 0)
        self.assertEqual(result["content"][0]["type"], "text")
        self.assertNotIn("isError", result)
        return json.loads(result["content"][0]["text"])

    def _assert_error(self, result):
        self.assertTrue(result.get("isError", False))


class TestBlenderEditNodes(_ToolTestBase):
    """blender_edit_nodes — edit node trees."""

    def test_call_add_node(self):
        result = self._call("blender_edit_nodes", {
            "tree_type": "SHADER",
            "context": "OBJECT",
            "operations": [
                {"action": "add_node", "type": "ShaderNodeBsdfPrincipled", "name": "BSDF"},
            ],
        })
        self._assert_success(result)

    def test_call_remove_node(self):
        result = self._call("blender_edit_nodes", {
            "tree_type": "SHADER",
            "context": "OBJECT",
            "operations": [{"action": "remove_node", "name": "OldNode"}],
        })
        self._assert_success(result)

    def test_call_connect_nodes(self):
        result = self._call("blender_edit_nodes", {
            "tree_type": "SHADER",
            "context": "OBJECT",
            "operations": [{
                "action": "connect",
                "from_node": "Image Texture", "from_socket": "Color",
                "to_node": "Principled BSDF", "to_socket": "Base Color",
            }],
        })
        self._assert_success(result)

    def test_call_set_value(self):
        result = self._call("blender_edit_nodes", {
            "tree_type": "SHADER",
            "context": "OBJECT",
            "operations": [
                {"action": "set_value", "node": "Principled BSDF", "input": "Metallic", "value": 1.0},
            ],
        })
        self._assert_success(result)

    def test_call_compositor(self):
        result = self._call("blender_edit_nodes", {
            "tree_type": "COMPOSITOR",
            "context": "SCENE",
            "operations": [{"action": "add_node", "type": "CompositorNodeBlur", "name": "Blur"}],
        })
        self._assert_success(result)

    def test_call_geometry_nodes(self):
        result = self._call("blender_edit_nodes", {
            "tree_type": "GEOMETRY",
            "context": "MODIFIER",
            "target": "Cube/GeometryNodes",
            "operations": [{"action": "add_node", "type": "GeometryNodeMeshCube", "name": "Cube"}],
        })
        self._assert_success(result)

    def test_call_multiple_operations(self):
        result = self._call("blender_edit_nodes", {
            "tree_type": "SHADER",
            "context": "OBJECT",
            "target": "Material",
            "operations": [
                {"action": "add_node", "type": "ShaderNodeTexImage", "name": "Image", "location": [-300, 0]},
                {"action": "add_node", "type": "ShaderNodeBsdfPrincipled", "name": "BSDF", "location": [0, 0]},
                {"action": "connect", "from_node": "Image", "from_socket": "Color", "to_node": "BSDF", "to_socket": "Base Color"},
                {"action": "set_value", "node": "BSDF", "input": "Metallic", "value": 0.8},
            ],
        })
        self._assert_success(result)


class TestBlenderEditAnimation(_ToolTestBase):
    """blender_edit_animation — edit animation data."""

    def test_call_insert_keyframe(self):
        result = self._call("blender_edit_animation", {
            "action": "insert_keyframe",
            "object_name": "Cube",
            "data_path": "location",
            "frame": 1,
            "value": [0, 0, 0],
        })
        self._assert_success(result)

    def test_call_delete_keyframe(self):
        result = self._call("blender_edit_animation", {
            "action": "delete_keyframe",
            "object_name": "Cube",
            "data_path": "location",
            "frame": 1,
        })
        self._assert_success(result)

    def test_call_set_frame_range(self):
        result = self._call("blender_edit_animation", {
            "action": "set_frame_range",
            "frame_start": 1,
            "frame_end": 250,
            "fps": 24,
        })
        self._assert_success(result)

    def test_call_add_nla_strip(self):
        result = self._call("blender_edit_animation", {
            "action": "add_nla_strip",
            "object_name": "Cube",
            "nla_action": "CubeAction",
            "nla_start_frame": 1,
        })
        self._assert_success(result)

    def test_call_set_shape_key(self):
        result = self._call("blender_edit_animation", {
            "action": "set_shape_key",
            "object_name": "Cube",
            "shape_key_name": "Key 1",
            "value": 0.5,
        })
        self._assert_success(result)

    def test_call_add_driver(self):
        result = self._call("blender_edit_animation", {
            "action": "add_driver",
            "object_name": "Cube",
            "data_path": "location",
            "index": 0,
            "driver_expression": "frame / 250",
        })
        self._assert_success(result)


class TestBlenderEditSequencer(_ToolTestBase):
    """blender_edit_sequencer — edit video sequencer."""

    def test_call_add_color_strip(self):
        result = self._call("blender_edit_sequencer", {
            "action": "add_strip",
            "strip_type": "COLOR",
            "channel": 1,
            "frame_start": 1,
            "frame_end": 100,
            "color": [1.0, 0.0, 0.0],
        })
        self._assert_success(result)

    def test_call_add_text_strip(self):
        result = self._call("blender_edit_sequencer", {
            "action": "add_strip",
            "strip_type": "TEXT",
            "channel": 2,
            "frame_start": 1,
            "frame_end": 50,
            "text": "Hello World",
            "font_size": 48,
        })
        self._assert_success(result)

    def test_call_modify_strip(self):
        result = self._call("blender_edit_sequencer", {
            "action": "modify_strip",
            "strip_name": "Color Strip",
            "settings": {"blend_type": "ALPHA_OVER"},
        })
        self._assert_success(result)

    def test_call_delete_strip(self):
        result = self._call("blender_edit_sequencer", {
            "action": "delete_strip",
            "strip_name": "Color Strip",
        })
        self._assert_success(result)

    def test_call_add_effect(self):
        result = self._call("blender_edit_sequencer", {
            "action": "add_effect",
            "effect_type": "GAUSSIAN_BLUR",
            "channel": 3,
            "frame_start": 1,
            "frame_end": 100,
        })
        self._assert_success(result)

    def test_call_add_transition(self):
        result = self._call("blender_edit_sequencer", {
            "action": "add_transition",
            "transition_type": "CROSS",
            "transition_duration": 30,
        })
        self._assert_success(result)

    def test_call_move_strip(self):
        result = self._call("blender_edit_sequencer", {
            "action": "move_strip",
            "strip_name": "Color Strip",
            "channel": 2,
            "frame_start": 50,
        })
        self._assert_success(result)


if __name__ == "__main__":
    unittest.main()
