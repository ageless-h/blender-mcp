# -*- coding: utf-8 -*-
"""Unit tests for animation editor — keyframes, NLA, drivers, shape keys, timeline."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _mock_keyframe(frame: float, value: float, interp: str = "BEZIER"):
    kp = MagicMock()
    kp.co = [frame, value]
    kp.interpolation = interp
    return kp


def _mock_fcurve(data_path: str, array_index: int, keyframe_points: list | None = None):
    fc = MagicMock()
    fc.data_path = data_path
    fc.array_index = array_index
    points = MagicMock()
    points.__iter__ = lambda self: iter(keyframe_points or [])
    points.__len__ = lambda self: len(keyframe_points or [])
    fc.keyframe_points = points
    return fc


def _mock_fcurves_collection(fcurves: list):
    """Create a mock fcurves collection with .find() method."""
    fcurves_mock = MagicMock()
    fcurves_mock.__iter__ = lambda self: iter(fcurves)
    fcurves_mock.__len__ = lambda self: len(fcurves)

    def find(data_path: str, index: int = -1):
        for fc in fcurves:
            if fc.data_path == data_path and (index == -1 or fc.array_index == index):
                return fc
        return None

    fcurves_mock.find = find
    return fcurves_mock


def _mock_action_legacy(fcurves: list):
    action = MagicMock()
    action.fcurves = _mock_fcurves_collection(fcurves)
    del action.layers
    return action


def _mock_action_layered(fcurves: list):
    cbag = MagicMock()
    cbag.fcurves = _mock_fcurves_collection(fcurves)
    strip = MagicMock()
    strip.channelbags = [cbag]
    layer = MagicMock()
    layer.strips = [strip]
    action = MagicMock()
    action.layers = [layer]
    del action.fcurves
    return action


def _mock_obj(
    name: str = "Cube",
    has_animation: bool = False,
    fcurves: list | None = None,
    layered: bool = False,
    has_shape_keys: bool = False,
    shape_key_blocks: dict | None = None,
):
    obj = MagicMock()
    obj.name = name
    if has_animation and fcurves is not None:
        if layered:
            action = _mock_action_layered(fcurves)
        else:
            action = _mock_action_legacy(fcurves)
        obj.animation_data.action = action
        obj.animation_data.nla_tracks = []
        obj.animation_data.drivers = []
    else:
        obj.animation_data = None if not has_animation else MagicMock()
        if obj.animation_data:
            obj.animation_data.action = None

    obj.data = MagicMock()
    if has_shape_keys and shape_key_blocks:
        obj.data.shape_keys.key_blocks = shape_key_blocks
    else:
        obj.data.shape_keys = None

    return obj


def _mock_bpy(objects: dict | None = None, frame_current: int = 1):
    bpy = MagicMock()
    bpy.context.scene.frame_current = frame_current
    bpy.data.objects.get = lambda name: objects.get(name) if objects else None
    bpy.data.actions = MagicMock()
    return bpy


class TestAnimationEditDispatch(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_missing_action(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_unknown_action(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit({"action": "nonexistent"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("Unknown action", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit({"action": "insert_keyframe"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")


class TestInsertKeyframe(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_basic_insert(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "insert_keyframe",
                "object_name": "Cube",
                "data_path": "location",
                "frame": 10,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "insert_keyframe")
        self.assertEqual(result["result"]["frame"], 10)
        obj.keyframe_insert.assert_called_once_with(data_path="location", index=-1, frame=10)

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_missing_object(self, mock_check):
        bpy = _mock_bpy({})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "insert_keyframe",
                "object_name": "Ghost",
                "data_path": "location",
            },
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_missing_object_name(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {"action": "insert_keyframe", "data_path": "location"},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")


class TestDeleteKeyframe(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_basic_delete(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "delete_keyframe",
                "object_name": "Cube",
                "data_path": "location",
                "frame": 10,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "delete_keyframe")
        obj.keyframe_delete.assert_called_once_with(data_path="location", index=-1, frame=10)


class TestModifyKeyframe(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_no_animation_data(self, mock_check):
        obj = _mock_obj(has_animation=False)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "modify_keyframe",
                "object_name": "Cube",
                "data_path": "location",
            },
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")
        self.assertIn("No animation data", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_modify_value_legacy(self, mock_check):
        kp1 = _mock_keyframe(1.0, 0.0)
        kp2 = _mock_keyframe(30.0, 3.0)
        fc = _mock_fcurve("location", 0, [kp1, kp2])
        new_kp = _mock_keyframe(1.0, 5.0)
        fc.keyframe_points.insert = MagicMock(return_value=new_kp)

        obj = _mock_obj(has_animation=True, fcurves=[fc], layered=False)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "modify_keyframe",
                "object_name": "Cube",
                "data_path": "location",
                "frame": 1,
                "value": 5.0,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["modified_count"], 1)
        fc.keyframe_points.insert.assert_called_once_with(1.0, 5.0)

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_modify_value_layered(self, mock_check):
        kp1 = _mock_keyframe(1.0, 0.0)
        fc = _mock_fcurve("location", 0, [kp1])
        new_kp = _mock_keyframe(1.0, 5.0)
        fc.keyframe_points.insert = MagicMock(return_value=new_kp)

        obj = _mock_obj(has_animation=True, fcurves=[fc], layered=True)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "modify_keyframe",
                "object_name": "Cube",
                "data_path": "location",
                "frame": 1,
                "value": 5.0,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["modified_count"], 1)

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_modify_interpolation_only(self, mock_check):
        kp1 = _mock_keyframe(1.0, 0.0)
        kp2 = _mock_keyframe(30.0, 3.0)
        fc = _mock_fcurve("location", 0, [kp1, kp2])

        obj = _mock_obj(has_animation=True, fcurves=[fc], layered=False)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "modify_keyframe",
                "object_name": "Cube",
                "data_path": "location",
                "interpolation": "LINEAR",
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["modified_count"], 2)

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_modify_no_matching_frame(self, mock_check):
        kp1 = _mock_keyframe(1.0, 0.0)
        fc = _mock_fcurve("location", 0, [kp1])

        obj = _mock_obj(has_animation=True, fcurves=[fc], layered=False)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "modify_keyframe",
                "object_name": "Cube",
                "data_path": "location",
                "frame": 999,
                "value": 5.0,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["modified_count"], 0)

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_modify_with_index_filter(self, mock_check):
        kp = _mock_keyframe(1.0, 0.0)
        fc_x = _mock_fcurve("location", 0, [kp])
        fc_y = _mock_fcurve("location", 1, [_mock_keyframe(1.0, 0.0)])
        new_kp = _mock_keyframe(1.0, 5.0)
        fc_x.keyframe_points.insert = MagicMock(return_value=new_kp)

        obj = _mock_obj(has_animation=True, fcurves=[fc_x, fc_y], layered=False)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "modify_keyframe",
                "object_name": "Cube",
                "data_path": "location",
                "index": 0,
                "frame": 1,
                "value": 5.0,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["modified_count"], 1)


class TestNLAStrips(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_add_nla_strip(self, mock_check):
        obj = _mock_obj()
        obj.animation_data = MagicMock()
        obj.animation_data.nla_tracks.new.return_value = MagicMock(name="NlaTrack")

        nla_action = MagicMock()
        nla_action.name = "WalkCycle"
        bpy = _mock_bpy({"Cube": obj})
        bpy.data.actions.get = lambda name: nla_action if name == "WalkCycle" else None
        mock_check.return_value = (True, bpy)

        track = obj.animation_data.nla_tracks.new.return_value
        track.strips.new.return_value = MagicMock(name="WalkCycleStrip")

        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "add_nla_strip",
                "object_name": "Cube",
                "nla_action": "WalkCycle",
                "nla_start_frame": 5,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "add_nla_strip")

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_add_nla_strip_missing_action(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        bpy.data.actions.get = lambda name: None
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {"action": "add_nla_strip", "object_name": "Cube", "nla_action": "Missing"},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_modify_nla_strip(self, mock_check):
        obj = _mock_obj()
        strip = MagicMock()
        strip.name = "WalkStrip"
        track = MagicMock()
        track.strips = [strip]
        obj.animation_data = MagicMock()
        obj.animation_data.nla_tracks = [track]

        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "modify_nla_strip",
                "object_name": "Cube",
                "nla_strip_name": "WalkStrip",
                "nla_start_frame": 10,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(strip.frame_start, 10)

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_remove_nla_strip(self, mock_check):
        obj = _mock_obj()
        strip = MagicMock()
        strip.name = "WalkStrip"
        track = MagicMock()
        track.strips = [strip]
        obj.animation_data = MagicMock()
        obj.animation_data.nla_tracks = [track]

        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "remove_nla_strip",
                "object_name": "Cube",
                "nla_strip_name": "WalkStrip",
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["removed"], "WalkStrip")

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_remove_nla_strip_not_found(self, mock_check):
        obj = _mock_obj()
        obj.animation_data = MagicMock()
        obj.animation_data.nla_tracks = []
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "remove_nla_strip",
                "object_name": "Cube",
                "nla_strip_name": "Ghost",
            },
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")


class TestDrivers(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_add_driver(self, mock_check):
        obj = _mock_obj()
        fc = MagicMock()
        fc.driver.expression = ""
        obj.driver_add.return_value = fc
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "add_driver",
                "object_name": "Cube",
                "data_path": "location.x",
                "driver_expression": "2*sin(frame)",
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["expression"], "2*sin(frame)")

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_remove_driver(self, mock_check):
        obj = _mock_obj()
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "remove_driver",
                "object_name": "Cube",
                "data_path": "location.x",
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "remove_driver")


class TestShapeKeys(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_set_shape_key(self, mock_check):
        kb = MagicMock()
        kb.value = 0.0
        obj = _mock_obj(has_shape_keys=True, shape_key_blocks={"Smile": kb})
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "set_shape_key",
                "object_name": "Cube",
                "shape_key_name": "Smile",
                "value": 0.8,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["value"], 0.8)
        self.assertEqual(kb.value, 0.8)

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_no_shape_keys(self, mock_check):
        obj = _mock_obj(has_shape_keys=False)
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "set_shape_key",
                "object_name": "Cube",
                "shape_key_name": "Smile",
            },
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_shape_key_not_found(self, mock_check):
        obj = _mock_obj(has_shape_keys=True, shape_key_blocks={})
        bpy = _mock_bpy({"Cube": obj})
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "set_shape_key",
                "object_name": "Cube",
                "shape_key_name": "Missing",
            },
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")


class TestTimeline(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_set_frame(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {"action": "set_frame", "frame": 25},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["frame"], 25)

    @patch("blender_mcp_addon.handlers.animation.editor.check_bpy_available")
    def test_set_frame_range(self, mock_check):
        bpy = _mock_bpy()
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 250
        bpy.context.scene.render.fps = 24
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.animation.editor import animation_edit

        result = animation_edit(
            {
                "action": "set_frame_range",
                "frame_start": 10,
                "frame_end": 100,
                "fps": 30,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["frame_start"], 10)
        self.assertEqual(result["result"]["frame_end"], 100)
        self.assertEqual(result["result"]["fps"], 30)


class TestIterFcurves(unittest.TestCase):
    def test_legacy_api(self):
        from blender_mcp_addon.handlers.animation import iter_fcurves

        fc1 = _mock_fcurve("location", 0, [])
        fc2 = _mock_fcurve("location", 1, [])
        action = _mock_action_legacy([fc1, fc2])
        result = list(iter_fcurves(action))
        self.assertEqual(len(result), 2)

    def test_layered_api(self):
        from blender_mcp_addon.handlers.animation import iter_fcurves

        fc = _mock_fcurve("location", 0, [])
        action = _mock_action_layered([fc])
        result = list(iter_fcurves(action))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].data_path, "location")

    def test_empty_action(self):
        from blender_mcp_addon.handlers.animation import iter_fcurves

        action = MagicMock(spec=[])
        action.fcurves = []
        if hasattr(action, "layers"):
            del action.layers
        result = list(iter_fcurves(action))
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
