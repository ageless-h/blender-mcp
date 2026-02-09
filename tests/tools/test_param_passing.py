# -*- coding: utf-8 -*-
"""Tests verifying parameter passing from _dispatch_new_capability to dispatcher functions.

These tests mock data_create/data_write/data_delete/data_read at the import site
in base.py and verify that the payloads are correctly structured with params
nested under the "params" key (not spread at top level).
"""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch, MagicMock

# Must set before importing addon modules
os.environ.setdefault("MCP_ADAPTER", "mock")

from blender_mcp_addon.capabilities.base import _dispatch_new_capability

_STARTED = 0.0
_MOCK_OK = {"ok": True, "result": {"mocked": True}}


def _make_mock(**kwargs):
    m = MagicMock(return_value=_MOCK_OK)
    return m


class TestCreateObjectParamPassing(unittest.TestCase):
    """Verify blender.create_object nests all params under 'params' key."""

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_mesh_cube_params_nested(self, mock_create):
        _dispatch_new_capability("blender.create_object", {
            "name": "Cube", "object_type": "MESH", "primitive": "cube", "size": 2.0,
        }, _STARTED)

        mock_create.assert_called_once()
        payload = mock_create.call_args[0][0]

        self.assertEqual(payload["type"], "object")
        self.assertEqual(payload["name"], "Cube")
        self.assertIn("params", payload)
        params = payload["params"]
        self.assertEqual(params["object_type"], "MESH")
        self.assertEqual(params["primitive"], "cube")
        self.assertEqual(params["size"], 2.0)

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_light_params_nested(self, mock_create):
        _dispatch_new_capability("blender.create_object", {
            "name": "Sun", "object_type": "LIGHT", "light_type": "SUN",
            "energy": 5.0, "color": [1, 0.9, 0.8],
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        params = payload["params"]
        self.assertEqual(params["object_type"], "LIGHT")
        self.assertEqual(params["light_type"], "SUN")
        self.assertEqual(params["energy"], 5.0)
        self.assertEqual(params["color"], [1, 0.9, 0.8])

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_camera_params_nested(self, mock_create):
        _dispatch_new_capability("blender.create_object", {
            "name": "Cam", "object_type": "CAMERA", "lens": 35,
            "clip_start": 0.1, "clip_end": 500,
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        params = payload["params"]
        self.assertEqual(params["lens"], 35)
        self.assertEqual(params["clip_start"], 0.1)
        self.assertEqual(params["clip_end"], 500)

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_transform_params_nested(self, mock_create):
        _dispatch_new_capability("blender.create_object", {
            "name": "Obj", "location": [1, 2, 3],
            "rotation": [0, 0, 1.57], "scale": [2, 2, 2],
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        params = payload["params"]
        self.assertEqual(params["location"], [1, 2, 3])
        self.assertEqual(params["rotation"], [0, 0, 1.57])
        self.assertEqual(params["scale"], [2, 2, 2])

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_collection_param_nested(self, mock_create):
        _dispatch_new_capability("blender.create_object", {
            "name": "P", "primitive": "plane", "collection": "MyCol",
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        params = payload["params"]
        self.assertEqual(params["primitive"], "plane")
        self.assertEqual(params["collection"], "MyCol")

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_name_not_in_params(self, mock_create):
        """name should be at top level, not duplicated inside params."""
        _dispatch_new_capability("blender.create_object", {
            "name": "Test", "primitive": "cube",
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        self.assertEqual(payload["name"], "Test")
        # name is extracted to top level and excluded from params
        self.assertNotIn("name", payload["params"])

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_payload_not_mutated(self, mock_create):
        """Original payload dict must not be mutated by dispatch."""
        original = {
            "name": "Cube", "object_type": "MESH", "primitive": "cube", "size": 2.0,
        }
        original_copy = dict(original)
        _dispatch_new_capability("blender.create_object", original, _STARTED)

        # The original payload should still have 'name' — no in-place pop
        self.assertEqual(original, original_copy)


class TestManageModifierParamPassing(unittest.TestCase):
    """Verify blender.manage_modifier nests params correctly."""

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_add_params_nested(self, mock_create):
        _dispatch_new_capability("blender.manage_modifier", {
            "action": "add", "object_name": "Cube",
            "modifier_name": "Sub", "modifier_type": "SUBSURF",
            "settings": {"levels": 2},
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        self.assertEqual(payload["type"], "modifier")
        self.assertEqual(payload["name"], "Sub")
        self.assertIn("params", payload)
        params = payload["params"]
        self.assertEqual(params["object"], "Cube")
        self.assertEqual(params["type"], "SUBSURF")
        self.assertEqual(params["settings"], {"levels": 2})

    @patch("blender_mcp_addon.capabilities.base.data_delete", return_value=_MOCK_OK)
    def test_remove_params_nested(self, mock_delete):
        _dispatch_new_capability("blender.manage_modifier", {
            "action": "remove", "object_name": "Cube", "modifier_name": "Sub",
        }, _STARTED)

        payload = mock_delete.call_args[0][0]
        self.assertEqual(payload["type"], "modifier")
        self.assertEqual(payload["name"], "Sub")
        self.assertIn("params", payload)
        self.assertEqual(payload["params"]["object"], "Cube")

    @patch("blender_mcp_addon.capabilities.base.data_write", return_value=_MOCK_OK)
    def test_configure_properties_and_params(self, mock_write):
        _dispatch_new_capability("blender.manage_modifier", {
            "action": "configure", "object_name": "Cube",
            "modifier_name": "Sub", "settings": {"levels": 3},
        }, _STARTED)

        payload = mock_write.call_args[0][0]
        self.assertEqual(payload["type"], "modifier")
        self.assertEqual(payload["name"], "Sub")
        self.assertIn("properties", payload)
        self.assertEqual(payload["properties"], {"levels": 3})
        self.assertIn("params", payload)
        self.assertEqual(payload["params"]["object"], "Cube")


class TestManageCollectionParamPassing(unittest.TestCase):
    """Verify blender.manage_collection nests params correctly."""

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_create_params_nested(self, mock_create):
        _dispatch_new_capability("blender.manage_collection", {
            "action": "create", "collection_name": "Props",
            "parent": "Scene Collection", "color_tag": "COLOR_01",
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        self.assertEqual(payload["type"], "collection")
        self.assertEqual(payload["name"], "Props")
        self.assertIn("params", payload)
        params = payload["params"]
        self.assertEqual(params["parent"], "Scene Collection")
        self.assertEqual(params["color_tag"], "COLOR_01")

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_create_no_optional_params(self, mock_create):
        _dispatch_new_capability("blender.manage_collection", {
            "action": "create", "collection_name": "Empty",
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        self.assertIn("params", payload)
        self.assertEqual(payload["params"], {})

    @patch("blender_mcp_addon.capabilities.base.data_write", return_value=_MOCK_OK)
    def test_set_visibility_properties_nested(self, mock_write):
        _dispatch_new_capability("blender.manage_collection", {
            "action": "set_visibility", "collection_name": "Props",
            "hide_viewport": True, "hide_render": False,
        }, _STARTED)

        payload = mock_write.call_args[0][0]
        self.assertEqual(payload["type"], "collection")
        self.assertEqual(payload["name"], "Props")
        self.assertIn("properties", payload)
        self.assertEqual(payload["properties"]["hide_viewport"], True)
        self.assertEqual(payload["properties"]["hide_render"], False)


class TestManageCollectionLinkParamPassing(unittest.TestCase):
    """Verify blender.manage_collection link/unlink/set_parent use correct data_link structure."""

    @patch("blender_mcp_addon.capabilities.base.data_link", return_value=_MOCK_OK)
    def test_link_object_source_target_dicts(self, mock_link):
        _dispatch_new_capability("blender.manage_collection", {
            "action": "link_object", "collection_name": "Props",
            "object_name": "Cube",
        }, _STARTED)

        mock_link.assert_called_once()
        payload = mock_link.call_args[0][0]
        # source must be a dict with type and name
        self.assertIn("source", payload)
        self.assertIsInstance(payload["source"], dict)
        self.assertEqual(payload["source"]["type"], "object")
        self.assertEqual(payload["source"]["name"], "Cube")
        # target must be a dict with type and name
        self.assertIn("target", payload)
        self.assertIsInstance(payload["target"], dict)
        self.assertEqual(payload["target"]["type"], "collection")
        self.assertEqual(payload["target"]["name"], "Props")
        # unlink should be False for link_object
        self.assertFalse(payload.get("unlink", False))

    @patch("blender_mcp_addon.capabilities.base.data_link", return_value=_MOCK_OK)
    def test_unlink_object_source_target_dicts(self, mock_link):
        _dispatch_new_capability("blender.manage_collection", {
            "action": "unlink_object", "collection_name": "Props",
            "object_name": "Cube",
        }, _STARTED)

        payload = mock_link.call_args[0][0]
        self.assertEqual(payload["source"]["type"], "object")
        self.assertEqual(payload["source"]["name"], "Cube")
        self.assertEqual(payload["target"]["type"], "collection")
        self.assertEqual(payload["target"]["name"], "Props")
        # unlink should be True for unlink_object
        self.assertTrue(payload["unlink"])

    @patch("blender_mcp_addon.capabilities.base.data_link", return_value=_MOCK_OK)
    def test_set_parent_source_target_dicts(self, mock_link):
        _dispatch_new_capability("blender.manage_collection", {
            "action": "set_parent", "collection_name": "Props",
            "parent": "Scene Collection",
        }, _STARTED)

        payload = mock_link.call_args[0][0]
        self.assertIn("source", payload)
        self.assertIsInstance(payload["source"], dict)
        self.assertEqual(payload["source"]["type"], "collection")
        self.assertEqual(payload["source"]["name"], "Props")
        self.assertIn("target", payload)
        self.assertIsInstance(payload["target"], dict)
        self.assertEqual(payload["target"]["type"], "collection")
        self.assertEqual(payload["target"]["name"], "Scene Collection")


class TestManageMaterialParamPassing(unittest.TestCase):
    """Verify blender.manage_material (already correct) stays correct."""

    @patch("blender_mcp_addon.capabilities.base.data_create", return_value=_MOCK_OK)
    def test_create_params_nested(self, mock_create):
        _dispatch_new_capability("blender.manage_material", {
            "action": "create", "name": "Metal",
            "base_color": [0.8, 0.1, 0.1, 1], "metallic": 1.0, "roughness": 0.3,
        }, _STARTED)

        payload = mock_create.call_args[0][0]
        self.assertEqual(payload["type"], "material")
        self.assertEqual(payload["name"], "Metal")
        self.assertIn("params", payload)
        params = payload["params"]
        self.assertEqual(params["base_color"], [0.8, 0.1, 0.1, 1])
        self.assertEqual(params["metallic"], 1.0)
        self.assertEqual(params["roughness"], 0.3)

    @patch("blender_mcp_addon.capabilities.base.data_link", return_value=_MOCK_OK)
    def test_assign_source_target_dicts(self, mock_link):
        """Verify assign uses correct data_link structure (already was correct)."""
        _dispatch_new_capability("blender.manage_material", {
            "action": "assign", "name": "Metal", "object_name": "Cube", "slot": 0,
        }, _STARTED)

        payload = mock_link.call_args[0][0]
        self.assertIn("source", payload)
        self.assertEqual(payload["source"], {"type": "material", "name": "Metal"})
        self.assertIn("target", payload)
        self.assertEqual(payload["target"], {"type": "object", "name": "Cube"})
        self.assertFalse(payload.get("unlink", False))

    @patch("blender_mcp_addon.capabilities.base.data_link", return_value=_MOCK_OK)
    def test_unassign_source_target_dicts(self, mock_link):
        """Verify unassign sets unlink=True."""
        _dispatch_new_capability("blender.manage_material", {
            "action": "unassign", "name": "Metal", "object_name": "Cube",
        }, _STARTED)

        payload = mock_link.call_args[0][0]
        self.assertTrue(payload["unlink"])


if __name__ == "__main__":
    unittest.main()
