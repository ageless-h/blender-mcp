# -*- coding: utf-8 -*-
"""Unit tests for physics handler — add/configure/remove/bake/free_bake."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _mock_obj(name="Cube"):
    obj = MagicMock()
    obj.name = name
    obj.type = "MESH"
    obj.mode = "OBJECT"
    obj.modifiers = []
    obj.rigid_body = None
    obj.particle_systems = []
    obj.field = MagicMock()
    obj.field.type = "NONE"
    return obj


def _mock_bpy(objects=None):
    bpy = MagicMock()
    bpy.data.objects.get = lambda n: objects.get(n) if objects else None
    bpy.context.scene.rigidbody_world = MagicMock()
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250
    return bpy


class TestPhysicsDispatch(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_missing_action(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage({"object_name": "Cube"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_missing_object_name(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage({"action": "add"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_object_not_found(self, mock_check):
        bpy = _mock_bpy({})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage({"action": "add", "object_name": "Ghost"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")

    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_unknown_action(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage({"action": "explode", "object_name": "Cube"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("Unknown action", result["error"]["message"])


class TestPhysicsAdd(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_add_missing_physics_type(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage({"action": "add", "object_name": "Cube"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("physics_type", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_add_force_field(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage(
            {
                "action": "add",
                "object_name": "Cube",
                "physics_type": "FORCE_FIELD",
                "force_field_type": "WIND",
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["physics_type"], "FORCE_FIELD")

    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_add_unknown_physics_type(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage(
            {"action": "add", "object_name": "Cube", "physics_type": "QUANTUM"},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertIn("Unknown physics_type", result["error"]["message"])


class TestPhysicsConfigure(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_configure_missing_settings(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage({"action": "configure", "object_name": "Cube"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("settings", result["error"]["message"])


class TestPhysicsBake(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_bake(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage(
            {"action": "bake", "object_name": "Cube", "frame_start": 1, "frame_end": 100},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "bake")

    @patch("blender_mcp_addon.handlers.physics.handler.check_bpy_available")
    def test_free_bake(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.physics.handler import physics_manage

        result = physics_manage({"action": "free_bake", "object_name": "Cube"}, started=_started())
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "free_bake")


if __name__ == "__main__":
    unittest.main()
