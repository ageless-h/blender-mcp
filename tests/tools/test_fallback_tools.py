# -*- coding: utf-8 -*-
"""Tests for the 3 fallback layer tools."""
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

    def _ok(self, result):
        self.assertIn("content", result)
        self.assertNotIn("isError", result)
        self.assertEqual(result["content"][0]["type"], "text")
        return json.loads(result["content"][0]["text"])

    def _err(self, result):
        self.assertTrue(result.get("isError", False))


class TestBlenderExecuteOperator(_ToolTestBase):
    """blender_execute_operator — execute any bpy.ops operator."""

    def test_basic_operator(self):
        self._ok(self._call("blender_execute_operator", {
            "operator": "mesh.primitive_cube_add",
        }))

    def test_operator_with_params(self):
        self._ok(self._call("blender_execute_operator", {
            "operator": "mesh.primitive_cube_add",
            "params": {"size": 2.0, "location": [0, 0, 0]},
        }))

    def test_operator_with_context(self):
        self._ok(self._call("blender_execute_operator", {
            "operator": "uv.smart_project",
            "params": {"angle_limit": 66.0},
            "context": {"active_object": "Cube", "mode": "EDIT"},
        }))

    def test_operator_only_required(self):
        self._ok(self._call("blender_execute_operator", {
            "operator": "object.select_all",
        }))


class TestBlenderExecuteScript(_ToolTestBase):
    """blender_execute_script — execute arbitrary Python code."""

    def test_simple_script(self):
        self._ok(self._call("blender_execute_script", {
            "code": "import bpy; print(bpy.data.objects.keys())",
        }))

    def test_multiline_script(self):
        self._ok(self._call("blender_execute_script", {
            "code": "import bpy\nfor obj in bpy.data.objects:\n    print(obj.name)",
        }))

    def test_empty_script(self):
        self._ok(self._call("blender_execute_script", {
            "code": "",
        }))


class TestBlenderImportExport(_ToolTestBase):
    """blender_import_export — import/export asset files."""

    def test_import_fbx(self):
        self._ok(self._call("blender_import_export", {
            "action": "import",
            "format": "FBX",
            "filepath": "/tmp/model.fbx",
        }))

    def test_export_gltf(self):
        self._ok(self._call("blender_import_export", {
            "action": "export",
            "format": "GLTF",
            "filepath": "/tmp/export.gltf",
        }))

    def test_import_obj(self):
        self._ok(self._call("blender_import_export", {
            "action": "import",
            "format": "OBJ",
            "filepath": "/tmp/model.obj",
        }))

    def test_export_usd(self):
        self._ok(self._call("blender_import_export", {
            "action": "export",
            "format": "USD",
            "filepath": "/tmp/scene.usd",
        }))

    def test_import_with_settings(self):
        self._ok(self._call("blender_import_export", {
            "action": "import",
            "format": "FBX",
            "filepath": "/tmp/model.fbx",
            "settings": {"use_custom_normals": True, "global_scale": 1.0},
        }))

    def test_export_stl(self):
        self._ok(self._call("blender_import_export", {
            "action": "export",
            "format": "STL",
            "filepath": "/tmp/print.stl",
        }))


if __name__ == "__main__":
    unittest.main()
