# -*- coding: utf-8 -*-
"""Unit tests for UV handler — seams, unwrap, UV layer management."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _mock_obj(name="Cube", obj_type="MESH"):
    obj = MagicMock()
    obj.name = name
    obj.type = obj_type
    obj.mode = "OBJECT"
    obj.data = MagicMock()
    obj.data.uv_layers = MagicMock()
    return obj


def _mock_bpy(objects=None):
    bpy = MagicMock()
    bpy.data.objects.get = lambda n: objects.get(n) if objects else None
    bpy.context.scene = MagicMock()
    bpy.context.view_layer.objects.active = None
    bpy.context.temp_override = MagicMock()
    bpy.context.temp_override.return_value.__enter__ = MagicMock(return_value=None)
    bpy.context.temp_override.return_value.__exit__ = MagicMock(return_value=None)
    return bpy


class TestUVDispatch(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_missing_action(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage({"object_name": "Cube"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_missing_object_name(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage({"action": "unwrap"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_object_not_found(self, mock_check):
        bpy = _mock_bpy({})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage({"action": "unwrap", "object_name": "Ghost"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_non_mesh_object(self, mock_check):
        obj = _mock_obj("Light", "LIGHT")
        bpy = _mock_bpy({"Light": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage({"action": "unwrap", "object_name": "Light"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("not a mesh", result["error"]["message"])


class TestUVLayerManagement(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_add_uv_map(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage(
            {"action": "add_uv_map", "object_name": "Cube", "uv_map_name": "UVMap2"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "add_uv_map")
        obj.data.uv_layers.new.assert_called_once_with(name="UVMap2")

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_remove_uv_map(self, mock_check):
        uv_layer = MagicMock()
        obj = _mock_obj()
        obj.data.uv_layers.get.return_value = uv_layer
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage(
            {"action": "remove_uv_map", "object_name": "Cube", "uv_map_name": "UVMap"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["removed"], "UVMap")

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_remove_uv_map_not_found(self, mock_check):
        obj = _mock_obj()
        obj.data.uv_layers.get.return_value = None
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage(
            {"action": "remove_uv_map", "object_name": "Cube", "uv_map_name": "Ghost"},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_set_active_uv(self, mock_check):
        uv_layer = MagicMock()
        obj = _mock_obj()
        obj.data.uv_layers.get.return_value = uv_layer
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage(
            {"action": "set_active_uv", "object_name": "Cube", "uv_map_name": "UVMap2"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["active"], "UVMap2")

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_set_active_uv_not_found(self, mock_check):
        obj = _mock_obj()
        obj.data.uv_layers.get.return_value = None
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage(
            {"action": "set_active_uv", "object_name": "Cube", "uv_map_name": "Ghost"},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")


if __name__ == "__main__":
    unittest.main()
