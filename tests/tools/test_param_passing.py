# -*- coding: utf-8 -*-
"""Tests verifying parameter passing from _dispatch_new_capability to handler methods.

These tests mock HandlerRegistry.get to return mock handlers and verify that
the handler methods (create, write, delete, link) are called with correctly
structured arguments after the legacy data_* dispatcher layer was removed.
"""

from __future__ import annotations

import os
import unittest
from unittest.mock import MagicMock, patch

# Must set before importing addon modules
os.environ.setdefault("MCP_ADAPTER", "mock")

from blender_mcp_addon.capabilities.base import _dispatch_new_capability
from blender_mcp_addon.handlers.types import DataType

_STARTED = 0.0


def _make_handler():
    """Create a fresh mock handler for each test."""
    m = MagicMock()
    m.create.return_value = {"mocked": True}
    m.write.return_value = {"mocked": True}
    m.delete.return_value = {"mocked": True}
    m.link.return_value = {"mocked": True}
    m.list_items.return_value = {"mocked": True}
    m.read.return_value = {"mocked": True}
    return m


class TestCreateObjectParamPassing(unittest.TestCase):
    """Verify blender.create_object passes params correctly to handler.create."""

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_mesh_cube_params_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.create_object",
            {
                "name": "Cube",
                "object_type": "MESH",
                "primitive": "cube",
                "size": 2.0,
            },
            _STARTED,
        )

        mock_get.assert_called_with(DataType.OBJECT)
        handler.create.assert_called_once()
        args = handler.create.call_args[0]
        self.assertEqual(args[0], "Cube")
        params = args[1]
        self.assertEqual(params["object_type"], "MESH")
        self.assertEqual(params["primitive"], "cube")
        self.assertEqual(params["size"], 2.0)

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_light_params_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.create_object",
            {
                "name": "Sun",
                "object_type": "LIGHT",
                "light_type": "SUN",
                "energy": 5.0,
                "color": [1, 0.9, 0.8],
            },
            _STARTED,
        )

        params = handler.create.call_args[0][1]
        self.assertEqual(params["object_type"], "LIGHT")
        self.assertEqual(params["light_type"], "SUN")
        self.assertEqual(params["energy"], 5.0)
        self.assertEqual(params["color"], [1, 0.9, 0.8])

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_camera_params_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.create_object",
            {
                "name": "Cam",
                "object_type": "CAMERA",
                "lens": 35,
                "clip_start": 0.1,
                "clip_end": 500,
            },
            _STARTED,
        )

        params = handler.create.call_args[0][1]
        self.assertEqual(params["lens"], 35)
        self.assertEqual(params["clip_start"], 0.1)
        self.assertEqual(params["clip_end"], 500)

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_transform_params_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.create_object",
            {
                "name": "Obj",
                "location": [1, 2, 3],
                "rotation": [0, 0, 1.57],
                "scale": [2, 2, 2],
            },
            _STARTED,
        )

        params = handler.create.call_args[0][1]
        self.assertEqual(params["location"], [1, 2, 3])
        self.assertEqual(params["rotation"], [0, 0, 1.57])
        self.assertEqual(params["scale"], [2, 2, 2])

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_collection_param_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.create_object",
            {
                "name": "P",
                "primitive": "plane",
                "collection": "MyCol",
            },
            _STARTED,
        )

        params = handler.create.call_args[0][1]
        self.assertEqual(params["primitive"], "plane")
        self.assertEqual(params["collection"], "MyCol")

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_name_not_in_params(self, mock_get):
        """name should be the first arg to handler.create, not duplicated inside params."""
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.create_object",
            {
                "name": "Test",
                "primitive": "cube",
            },
            _STARTED,
        )

        args = handler.create.call_args[0]
        self.assertEqual(args[0], "Test")
        self.assertNotIn("name", args[1])

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_payload_not_mutated(self, mock_get):
        """Original payload dict must not be mutated by dispatch."""
        handler = _make_handler()
        mock_get.return_value = handler

        original = {
            "name": "Cube",
            "object_type": "MESH",
            "primitive": "cube",
            "size": 2.0,
        }
        original_copy = dict(original)
        _dispatch_new_capability("blender.create_object", original, _STARTED)

        self.assertEqual(original, original_copy)


class TestManageModifierParamPassing(unittest.TestCase):
    """Verify blender.manage_modifier calls handler methods correctly."""

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_add_params_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_modifier",
            {
                "action": "add",
                "object_name": "Cube",
                "modifier_name": "Sub",
                "modifier_type": "SUBSURF",
                "settings": {"levels": 2},
            },
            _STARTED,
        )

        mock_get.assert_called_with(DataType.MODIFIER)
        handler.create.assert_called_once_with(
            "Sub",
            {
                "object": "Cube",
                "type": "SUBSURF",
                "settings": {"levels": 2},
            },
        )

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_remove_params_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_modifier",
            {
                "action": "remove",
                "object_name": "Cube",
                "modifier_name": "Sub",
            },
            _STARTED,
        )

        handler.delete.assert_called_once_with("Sub", {"object": "Cube"})

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_configure_properties_and_params(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_modifier",
            {
                "action": "configure",
                "object_name": "Cube",
                "modifier_name": "Sub",
                "settings": {"levels": 3},
            },
            _STARTED,
        )

        handler.write.assert_called_once_with("Sub", {"levels": 3}, {"object": "Cube"})


class TestManageCollectionParamPassing(unittest.TestCase):
    """Verify blender.manage_collection calls handler methods correctly."""

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_create_params_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_collection",
            {
                "action": "create",
                "collection_name": "Props",
                "parent": "Scene Collection",
                "color_tag": "COLOR_01",
            },
            _STARTED,
        )

        mock_get.assert_called_with(DataType.COLLECTION)
        handler.create.assert_called_once_with(
            "Props",
            {
                "parent": "Scene Collection",
                "color_tag": "COLOR_01",
            },
        )

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_create_no_optional_params(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_collection",
            {
                "action": "create",
                "collection_name": "Empty",
            },
            _STARTED,
        )

        handler.create.assert_called_once_with("Empty", {})

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_set_visibility_properties_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_collection",
            {
                "action": "set_visibility",
                "collection_name": "Props",
                "hide_viewport": True,
                "hide_render": False,
            },
            _STARTED,
        )

        handler.write.assert_called_once_with(
            "Props",
            {
                "hide_viewport": True,
                "hide_render": False,
            },
            {},
        )


class TestManageCollectionLinkParamPassing(unittest.TestCase):
    """Verify blender.manage_collection link/unlink/set_parent use handler.link correctly."""

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_link_object_source_target(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_collection",
            {
                "action": "link_object",
                "collection_name": "Props",
                "object_name": "Cube",
            },
            _STARTED,
        )

        handler.link.assert_called_once_with(
            "Cube",
            DataType.COLLECTION,
            "Props",
            False,
            {},
        )

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_unlink_object_source_target(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_collection",
            {
                "action": "unlink_object",
                "collection_name": "Props",
                "object_name": "Cube",
            },
            _STARTED,
        )

        handler.link.assert_called_once_with(
            "Cube",
            DataType.COLLECTION,
            "Props",
            True,
            {},
        )

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_set_parent_source_target(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_collection",
            {
                "action": "set_parent",
                "collection_name": "Props",
                "parent": "Scene Collection",
            },
            _STARTED,
        )

        handler.link.assert_called_once_with(
            "Props",
            DataType.COLLECTION,
            "Scene Collection",
            False,
            {},
        )


class TestManageMaterialParamPassing(unittest.TestCase):
    """Verify blender.manage_material calls handler methods correctly."""

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_create_params_nested(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_material",
            {
                "action": "create",
                "name": "Metal",
                "base_color": [0.8, 0.1, 0.1, 1],
                "metallic": 1.0,
                "roughness": 0.3,
            },
            _STARTED,
        )

        mock_get.assert_called_with(DataType.MATERIAL)
        handler.create.assert_called_once_with(
            "Metal",
            {
                "base_color": [0.8, 0.1, 0.1, 1],
                "metallic": 1.0,
                "roughness": 0.3,
            },
        )

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_assign_source_target(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_material",
            {
                "action": "assign",
                "name": "Metal",
                "object_name": "Cube",
                "slot": 0,
            },
            _STARTED,
        )

        handler.link.assert_called_once_with(
            "Metal",
            DataType.OBJECT,
            "Cube",
            False,
            {"slot": 0},
        )

    @patch("blender_mcp_addon.capabilities.base.HandlerRegistry.get")
    def test_unassign_source_target(self, mock_get):
        handler = _make_handler()
        mock_get.return_value = handler

        _dispatch_new_capability(
            "blender.manage_material",
            {
                "action": "unassign",
                "name": "Metal",
                "object_name": "Cube",
            },
            _STARTED,
        )

        handler.link.assert_called_once_with(
            "Metal",
            DataType.OBJECT,
            "Cube",
            True,
            {"slot": None},
        )


if __name__ == "__main__":
    unittest.main()
