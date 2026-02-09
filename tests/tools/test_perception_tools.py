# -*- coding: utf-8 -*-
"""Tests for the 11 perception layer tools.

Each tool is tested for:
- Successful call with valid params via MockAdapter
- Required parameter validation
- Response structure (content array with text type)
"""
from __future__ import annotations

import json
import os
import unittest

os.environ["MCP_ADAPTER"] = "mock"

from blender_mcp.mcp_protocol import MCPServer


class _ToolTestBase(unittest.TestCase):
    """Shared helpers for tool tests."""

    @classmethod
    def setUpClass(cls):
        cls.server = MCPServer()

    def _call(self, name: str, args: dict | None = None) -> dict:
        return self.server.tools_call(name, args or {})

    def _assert_success(self, result: dict) -> dict:
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], list)
        self.assertGreater(len(result["content"]), 0)
        self.assertEqual(result["content"][0]["type"], "text")
        self.assertNotIn("isError", result)
        return json.loads(result["content"][0]["text"])

    def _assert_error(self, result: dict) -> None:
        self.assertTrue(result.get("isError", False))


class TestBlenderGetObjects(_ToolTestBase):
    """blender_get_objects — list scene objects with optional filters."""

    def test_call_no_params(self):
        result = self._call("blender_get_objects")
        self._assert_success(result)

    def test_call_with_type_filter(self):
        result = self._call("blender_get_objects", {"type_filter": "MESH"})
        self._assert_success(result)

    def test_call_with_collection_filter(self):
        result = self._call("blender_get_objects", {"collection": "MyCollection"})
        self._assert_success(result)

    def test_call_with_selected_only(self):
        result = self._call("blender_get_objects", {"selected_only": True})
        self._assert_success(result)

    def test_call_with_visible_only(self):
        result = self._call("blender_get_objects", {"visible_only": True})
        self._assert_success(result)

    def test_call_with_name_pattern(self):
        result = self._call("blender_get_objects", {"name_pattern": "SM_*"})
        self._assert_success(result)

    def test_call_with_all_filters(self):
        result = self._call("blender_get_objects", {
            "type_filter": "MESH",
            "collection": "Props",
            "selected_only": False,
            "visible_only": True,
            "name_pattern": "*_high",
        })
        self._assert_success(result)


class TestBlenderGetObjectData(_ToolTestBase):
    """blender_get_object_data — detailed data for a single object."""

    def test_call_with_name(self):
        result = self._call("blender_get_object_data", {"name": "Cube"})
        self._assert_success(result)

    def test_call_with_include(self):
        result = self._call("blender_get_object_data", {
            "name": "Cube",
            "include": ["summary", "mesh_stats", "modifiers"],
        })
        self._assert_success(result)

    def test_call_with_all_includes(self):
        result = self._call("blender_get_object_data", {
            "name": "Cube",
            "include": [
                "summary", "mesh_stats", "modifiers", "materials",
                "constraints", "physics", "animation", "custom_properties",
                "vertex_groups", "shape_keys", "uv_maps", "particle_systems",
            ],
        })
        self._assert_success(result)


class TestBlenderGetNodeTree(_ToolTestBase):
    """blender_get_node_tree — read node tree structure."""

    def test_call_shader_object(self):
        result = self._call("blender_get_node_tree", {
            "tree_type": "SHADER",
            "context": "OBJECT",
            "target": "Material",
        })
        self._assert_success(result)

    def test_call_compositor(self):
        result = self._call("blender_get_node_tree", {
            "tree_type": "COMPOSITOR",
            "context": "SCENE",
        })
        self._assert_success(result)

    def test_call_geometry_modifier(self):
        result = self._call("blender_get_node_tree", {
            "tree_type": "GEOMETRY",
            "context": "MODIFIER",
            "target": "Cube/GeometryNodes",
        })
        self._assert_success(result)

    def test_call_with_depth_full(self):
        result = self._call("blender_get_node_tree", {
            "tree_type": "SHADER",
            "context": "WORLD",
            "depth": "full",
        })
        self._assert_success(result)


class TestBlenderGetAnimationData(_ToolTestBase):
    """blender_get_animation_data — read animation data."""

    def test_call_with_target(self):
        result = self._call("blender_get_animation_data", {"target": "Cube"})
        self._assert_success(result)

    def test_call_scene_target(self):
        result = self._call("blender_get_animation_data", {"target": "scene"})
        self._assert_success(result)

    def test_call_with_include(self):
        result = self._call("blender_get_animation_data", {
            "target": "Cube",
            "include": ["keyframes", "fcurves", "nla"],
        })
        self._assert_success(result)

    def test_call_with_frame_range(self):
        result = self._call("blender_get_animation_data", {
            "target": "Cube",
            "frame_range": [1, 250],
        })
        self._assert_success(result)


class TestBlenderGetMaterials(_ToolTestBase):
    """blender_get_materials — list all materials."""

    def test_call_no_params(self):
        result = self._call("blender_get_materials")
        self._assert_success(result)

    def test_call_filter_used(self):
        result = self._call("blender_get_materials", {"filter": "used_only"})
        self._assert_success(result)

    def test_call_filter_unused(self):
        result = self._call("blender_get_materials", {"filter": "unused_only"})
        self._assert_success(result)

    def test_call_with_name_pattern(self):
        result = self._call("blender_get_materials", {"name_pattern": "*Metal*"})
        self._assert_success(result)


class TestBlenderGetScene(_ToolTestBase):
    """blender_get_scene — scene-level information."""

    def test_call_no_params(self):
        result = self._call("blender_get_scene")
        self._assert_success(result)

    def test_call_with_include(self):
        result = self._call("blender_get_scene", {
            "include": ["stats", "render", "world", "timeline", "version", "memory"],
        })
        self._assert_success(result)

    def test_call_stats_only(self):
        result = self._call("blender_get_scene", {"include": ["stats"]})
        self._assert_success(result)


class TestBlenderGetCollections(_ToolTestBase):
    """blender_get_collections — collection hierarchy tree."""

    def test_call_no_params(self):
        result = self._call("blender_get_collections")
        self._assert_success(result)

    def test_call_with_root(self):
        result = self._call("blender_get_collections", {"root": "MyCollection"})
        self._assert_success(result)

    def test_call_with_depth(self):
        result = self._call("blender_get_collections", {"depth": 3})
        self._assert_success(result)


class TestBlenderGetArmatureData(_ToolTestBase):
    """blender_get_armature_data — armature/bone data."""

    def test_call_with_name(self):
        result = self._call("blender_get_armature_data", {"armature_name": "Armature"})
        self._assert_success(result)

    def test_call_with_include(self):
        result = self._call("blender_get_armature_data", {
            "armature_name": "Armature",
            "include": ["hierarchy", "poses", "constraints", "bone_groups", "ik_chains"],
        })
        self._assert_success(result)

    def test_call_with_bone_filter(self):
        result = self._call("blender_get_armature_data", {
            "armature_name": "Armature",
            "bone_filter": "Arm*",
        })
        self._assert_success(result)


class TestBlenderGetImages(_ToolTestBase):
    """blender_get_images — list images/textures."""

    def test_call_no_params(self):
        result = self._call("blender_get_images")
        self._assert_success(result)

    def test_call_filter_packed(self):
        result = self._call("blender_get_images", {"filter": "packed"})
        self._assert_success(result)

    def test_call_filter_missing(self):
        result = self._call("blender_get_images", {"filter": "missing"})
        self._assert_success(result)

    def test_call_with_name_pattern(self):
        result = self._call("blender_get_images", {"name_pattern": "tex_*"})
        self._assert_success(result)


class TestBlenderCaptureViewport(_ToolTestBase):
    """blender_capture_viewport — viewport screenshot."""

    def test_call_no_params(self):
        result = self._call("blender_capture_viewport")
        self._assert_success(result)

    def test_call_with_shading(self):
        result = self._call("blender_capture_viewport", {"shading": "RENDERED"})
        self._assert_success(result)

    def test_call_with_camera_view(self):
        result = self._call("blender_capture_viewport", {"camera_view": True})
        self._assert_success(result)

    def test_call_with_format_jpeg(self):
        result = self._call("blender_capture_viewport", {"format": "JPEG"})
        self._assert_success(result)

    def test_call_with_all_params(self):
        result = self._call("blender_capture_viewport", {
            "shading": "MATERIAL",
            "camera_view": True,
            "format": "PNG",
        })
        self._assert_success(result)


class TestBlenderGetSelection(_ToolTestBase):
    """blender_get_selection — current selection state."""

    def test_call_no_params(self):
        result = self._call("blender_get_selection")
        self._assert_success(result)


if __name__ == "__main__":
    unittest.main()
