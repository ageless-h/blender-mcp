# -*- coding: utf-8 -*-
"""Unit tests for constraints handler — add/configure/remove/enable/disable."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _mock_obj(name="Cube", constraints=None):
    obj = MagicMock()
    obj.name = name
    obj.type = "MESH"
    obj.constraints = constraints or MagicMock()
    obj.pose = None
    return obj


def _mock_bpy(objects=None):
    bpy = MagicMock()
    bpy.data.objects.get = lambda n: objects.get(n) if objects else None
    return bpy


class TestConstraintsDispatch(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_missing_action(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_unknown_action(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage({"action": "fly_away", "target_name": "Cube"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("Unknown action", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_missing_target_name(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage({"action": "add"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_object_not_found(self, mock_check):
        bpy = _mock_bpy({})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage({"action": "add", "target_name": "Ghost"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")


class TestConstraintsAdd(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_add_constraint(self, mock_check):
        new_c = MagicMock()
        new_c.name = "TrackTo"
        constraints = MagicMock()
        constraints.new.return_value = new_c
        obj = _mock_obj(constraints=constraints)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage(
            {
                "action": "add",
                "target_name": "Cube",
                "constraint_type": "TRACK_TO",
                "constraint_name": "MyTrack",
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "add")
        self.assertEqual(result["result"]["type"], "TRACK_TO")
        constraints.new.assert_called_once_with(type="TRACK_TO")

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_add_missing_type(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage({"action": "add", "target_name": "Cube"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("constraint_type", result["error"]["message"])


class TestConstraintsRemove(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_remove_constraint(self, mock_check):
        c = MagicMock()
        c.name = "TrackTo"
        constraints = MagicMock()
        constraints.get.return_value = c
        obj = _mock_obj(constraints=constraints)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage(
            {"action": "remove", "target_name": "Cube", "constraint_name": "TrackTo"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["removed"], "TrackTo")
        constraints.remove.assert_called_once_with(c)

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_remove_not_found(self, mock_check):
        constraints = MagicMock()
        constraints.get.return_value = None
        obj = _mock_obj(constraints=constraints)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage(
            {"action": "remove", "target_name": "Cube", "constraint_name": "Ghost"},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")


class TestConstraintsEnableDisable(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_disable_constraint(self, mock_check):
        c = MagicMock()
        c.name = "TrackTo"
        c.mute = False
        constraints = MagicMock()
        constraints.get.return_value = c
        obj = _mock_obj(constraints=constraints)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage(
            {"action": "disable", "target_name": "Cube", "constraint_name": "TrackTo"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertTrue(c.mute)

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_enable_constraint(self, mock_check):
        c = MagicMock()
        c.name = "TrackTo"
        c.mute = True
        constraints = MagicMock()
        constraints.get.return_value = c
        obj = _mock_obj(constraints=constraints)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage(
            {"action": "enable", "target_name": "Cube", "constraint_name": "TrackTo"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertFalse(c.mute)


class TestConstraintsConfigure(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_configure_constraint(self, mock_check):
        c = MagicMock()
        c.name = "TrackTo"
        constraints = MagicMock()
        constraints.get.return_value = c
        obj = _mock_obj(constraints=constraints)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage(
            {
                "action": "configure",
                "target_name": "Cube",
                "constraint_name": "TrackTo",
                "settings": {"influence": 0.5},
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "configure")


if __name__ == "__main__":
    unittest.main()
