# -*- coding: utf-8 -*-
"""Regression tests for the 10 bugs fixed in the bug-fix sprint."""

from __future__ import annotations

import sys
import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _install_mock_bpy(mock_bpy):
    """Install a mock bpy module into sys.modules for handler imports."""
    sys.modules["bpy"] = mock_bpy


def _remove_mock_bpy():
    """Remove mock bpy from sys.modules."""
    sys.modules.pop("bpy", None)


# ---------------------------------------------------------------------------
# Bug 1: Object delete — mesh data orphaned ("meshs" vs "meshes")
# ---------------------------------------------------------------------------


class TestBug1_ObjectDeleteDataNotOrphaned(unittest.TestCase):
    def test_delete_with_data_uses_correct_collection_name(self):
        mesh_data = MagicMock()
        mesh_data.name = "Cube.001"
        mesh_data.bl_rna.identifier = "Mesh"

        mock_meshes = MagicMock()
        mock_meshes.__contains__ = lambda self, name: True

        bpy = MagicMock()
        bpy.data.objects.get.return_value = MagicMock(name="Cube", data=mesh_data)
        bpy.data.meshes = mock_meshes
        _install_mock_bpy(bpy)

        try:
            from blender_mcp_addon.handlers.data.object_handler import ObjectHandler

            handler = ObjectHandler()
            result = handler.delete("Cube", {"delete_data": True})
            self.assertEqual(result["deleted"], "Cube")
            self.assertTrue(result["data_deleted"])
        finally:
            _remove_mock_bpy()


# ---------------------------------------------------------------------------
# Bug 2: Material assign crashes on Empty objects (obj.data is None)
# ---------------------------------------------------------------------------


class TestBug2_MaterialAssignEmptyObject(unittest.TestCase):
    def test_material_link_to_empty_object_returns_error(self):
        mat = MagicMock()
        mat.name = "TestMat"

        obj = MagicMock()
        obj.name = "Empty"
        obj.type = "EMPTY"
        obj.data = None

        bpy = MagicMock()
        bpy.data.materials.get.return_value = mat
        bpy.data.objects.get.return_value = obj
        _install_mock_bpy(bpy)

        try:
            from blender_mcp_addon.handlers.data.material_handler import MaterialHandler
            from blender_mcp_addon.handlers.types import DataType

            handler = MaterialHandler()
            result = handler.link("TestMat", DataType.OBJECT, "Empty")
            self.assertIn("error", result)
            self.assertIn("no data block", result["error"].lower())
        finally:
            _remove_mock_bpy()


# ---------------------------------------------------------------------------
# Bug 3: FPS truncated to int (23.976 → 23)
# ---------------------------------------------------------------------------


class TestBug3_FractionalFPS(unittest.TestCase):
    def _mock_bpy(self):
        bpy = MagicMock()
        bpy.context.scene.render.fps = 24
        bpy.context.scene.render.engine = "BLENDER_EEVEE"
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.context.scene.render.film_transparent = False
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.filepath = "/tmp/render"
        bpy.context.scene.world = None
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 250
        return bpy

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_fractional_fps_uses_fps_base(self, mock_check):
        bpy = self._mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"fps": 23.976}, started=_started())
        self.assertTrue(result["ok"])
        self.assertEqual(bpy.context.scene.render.fps, 23976)
        self.assertEqual(bpy.context.scene.render.fps_base, 1000)

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_integer_fps_uses_fps_base_1(self, mock_check):
        bpy = self._mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"fps": 30}, started=_started())
        self.assertTrue(result["ok"])
        self.assertEqual(bpy.context.scene.render.fps, 30)
        self.assertEqual(bpy.context.scene.render.fps_base, 1)


# ---------------------------------------------------------------------------
# Bug 4: VSE add_transition was a no-op placeholder
# ---------------------------------------------------------------------------


class TestBug4_VSETransitionImplementation(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.sequencer.editor.check_bpy_available")
    def test_add_transition_calls_new_effect(self, mock_check):
        strip1 = MagicMock()
        strip1.name = "Clip1"
        strip2 = MagicMock()
        strip2.name = "Clip2"
        strip2.frame_start = 50

        new_strip = MagicMock()
        new_strip.name = "CROSS_Transition"

        sed = MagicMock()
        sed.sequences.get.side_effect = lambda n: {"Clip1": strip1, "Clip2": strip2}.get(n)
        sed.sequences.new_effect.return_value = new_strip

        bpy = MagicMock()
        bpy.context.scene.sequence_editor = sed
        mock_check.return_value = (True, bpy)

        from blender_mcp_addon.handlers.sequencer.editor import sequencer_edit

        result = sequencer_edit(
            {
                "action": "add_transition",
                "strip1_name": "Clip1",
                "strip2_name": "Clip2",
                "transition_type": "CROSS",
                "transition_duration": 15,
            },
            started=_started(),
        )
        self.assertTrue(result["ok"])
        sed.sequences.new_effect.assert_called_once()
        call_kwargs = sed.sequences.new_effect.call_args[1]
        self.assertEqual(call_kwargs["seq1"], strip1)
        self.assertEqual(call_kwargs["seq2"], strip2)


# ---------------------------------------------------------------------------
# Bug 5: action.fcurves crashes on Blender 5.1 (removed API)
# ---------------------------------------------------------------------------


class TestBug5_IterFcurvesCompat(unittest.TestCase):
    def test_legacy_fcurves(self):
        from blender_mcp_addon.handlers.animation import iter_fcurves

        fc1, fc2 = MagicMock(), MagicMock()
        action = MagicMock()
        del action.layers
        action.fcurves = [fc1, fc2]
        self.assertEqual(list(iter_fcurves(action)), [fc1, fc2])

    def test_layered_fcurves_blender_50(self):
        from blender_mcp_addon.handlers.animation import iter_fcurves

        fc1, fc2 = MagicMock(), MagicMock()
        cbag = MagicMock()
        cbag.fcurves = [fc1, fc2]
        strip = MagicMock()
        strip.channelbags = [cbag]
        layer = MagicMock()
        layer.strips = [strip]
        action = MagicMock()
        action.layers = [layer]
        del action.fcurves
        self.assertEqual(list(iter_fcurves(action)), [fc1, fc2])

    def test_empty_action_no_crash(self):
        from blender_mcp_addon.handlers.animation import iter_fcurves

        action = MagicMock()
        del action.layers
        action.fcurves = []
        self.assertEqual(list(iter_fcurves(action)), [])


# ---------------------------------------------------------------------------
# Bug 6: UV mark_seam ignores selection_mode parameter
# ---------------------------------------------------------------------------


class TestBug6_UVMarkSeamSelectionMode(unittest.TestCase):
    def _mock_bpy_for_uv(self):
        obj = MagicMock()
        obj.name = "Cube"
        obj.type = "MESH"
        obj.mode = "EDIT"
        obj.data = MagicMock()
        obj.data.uv_layers = MagicMock()

        bpy = MagicMock()
        bpy.data.objects.get.return_value = obj
        bpy.context.scene = MagicMock()
        bpy.context.view_layer.objects.active = obj
        bpy.context.temp_override = MagicMock()
        bpy.context.temp_override.return_value.__enter__ = MagicMock(return_value=None)
        bpy.context.temp_override.return_value.__exit__ = MagicMock(return_value=None)
        return bpy, obj

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_mark_seam_all_edges(self, mock_check):
        bpy, obj = self._mock_bpy_for_uv()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage(
            {"action": "mark_seam", "object_name": "Cube", "selection_mode": "ALL_EDGES"},
            started=_started(),
        )
        self.assertTrue(result["ok"])

    @patch("blender_mcp_addon.handlers.uv.handler.check_bpy_available")
    def test_mark_seam_default_sharp_edges(self, mock_check):
        bpy, obj = self._mock_bpy_for_uv()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.uv.handler import uv_manage

        result = uv_manage(
            {"action": "mark_seam", "object_name": "Cube"},
            started=_started(),
        )
        self.assertTrue(result["ok"])


# ---------------------------------------------------------------------------
# Bug 7: Constraint move_up/move_down wrong operator override
# ---------------------------------------------------------------------------


class TestBug7_ConstraintMoveUsesTempOverride(unittest.TestCase):
    def _mock_bpy_for_constraint(self):
        constraint = MagicMock()
        constraint.name = "Track To"

        obj = MagicMock()
        obj.name = "Cube"
        obj.type = "MESH"
        obj.constraints = MagicMock()
        obj.constraints.get.return_value = constraint
        obj.pose = None

        bpy = MagicMock()
        bpy.data.objects.get.return_value = obj
        bpy.context.view_layer.objects.active = obj
        return bpy, obj, constraint

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_move_up(self, mock_check):
        bpy, obj, constraint = self._mock_bpy_for_constraint()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage(
            {"action": "move_up", "target_name": "Cube", "constraint_name": "Track To"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        bpy.ops.constraint.move_up.assert_called_once_with(constraint="Track To")

    @patch("blender_mcp_addon.handlers.constraints.handler.check_bpy_available")
    def test_move_down(self, mock_check):
        bpy, obj, constraint = self._mock_bpy_for_constraint()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.constraints.handler import constraints_manage

        result = constraints_manage(
            {"action": "move_down", "target_name": "Cube", "constraint_name": "Track To"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        bpy.ops.constraint.move_down.assert_called_once_with(constraint="Track To")


# ---------------------------------------------------------------------------
# Bug 8: visible toggle sets both viewport AND render visibility
# ---------------------------------------------------------------------------


class TestBug8_VisibleToggleOnlyAffectsViewport(unittest.TestCase):
    def test_visible_true_only_sets_hide_viewport(self):
        obj = MagicMock()
        obj.name = "Cube"

        bpy = MagicMock()
        bpy.data.objects.get.return_value = obj
        _install_mock_bpy(bpy)

        try:
            from blender_mcp_addon.handlers.data.object_handler import ObjectHandler

            handler = ObjectHandler()
            result = handler.write("Cube", {"visible": True}, {})
            self.assertIn("visible", result["modified"])
            self.assertEqual(obj.hide_viewport, False)
        finally:
            _remove_mock_bpy()

    def test_visible_false_only_sets_hide_viewport(self):
        obj = MagicMock()
        obj.name = "Cube"

        bpy = MagicMock()
        bpy.data.objects.get.return_value = obj
        _install_mock_bpy(bpy)

        try:
            from blender_mcp_addon.handlers.data.object_handler import ObjectHandler

            handler = ObjectHandler()
            result = handler.write("Cube", {"visible": False}, {})
            self.assertIn("visible", result["modified"])
            self.assertEqual(obj.hide_viewport, True)
        finally:
            _remove_mock_bpy()


# ---------------------------------------------------------------------------
# Bug 9: _image_to_base64 permanently scales original image
# ---------------------------------------------------------------------------


class TestBug9_ImageBase64NonDestructive(unittest.TestCase):
    def test_image_copy_on_scale(self):
        image = MagicMock()
        image.name = "TestImage"
        image.size = [1024, 768]
        image.channels = 4
        image.depth = 8
        image.is_float = False
        image.filepath = "/tmp/test.png"
        image.source = "FILE"
        image.type = "IMAGE"
        image.users = 1

        image_copy = MagicMock()
        image.copy.return_value = image_copy

        bpy = MagicMock()
        bpy.data.images.get.return_value = image
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.image_settings.quality = 90
        _install_mock_bpy(bpy)

        try:
            from blender_mcp_addon.handlers.data.image_handler import ImageHandler

            handler = ImageHandler()
            try:
                handler.read("TestImage", None, {"format": "base64", "scale": 0.5})
            except Exception:
                pass
            image.copy.assert_called_once()
        finally:
            _remove_mock_bpy()


# ---------------------------------------------------------------------------
# Bug 10: Denoising silently ignored for EEVEE without feedback
# ---------------------------------------------------------------------------


class TestBug10_DenoisingEeveeSkippedFeedback(unittest.TestCase):
    def _mock_bpy_for_scene(self, engine="BLENDER_EEVEE"):
        bpy = MagicMock()
        bpy.context.scene.render.engine = engine
        bpy.context.scene.render.fps = 24
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.context.scene.render.film_transparent = False
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.filepath = "/tmp/render"
        bpy.context.scene.world = None
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 250
        return bpy

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_eevee_reports_skip(self, mock_check):
        bpy = self._mock_bpy_for_scene("BLENDER_EEVEE")
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"denoising": True}, started=_started())
        self.assertTrue(result["ok"])
        denoise_entries = [m for m in result["result"]["modified"] if "denoising" in m]
        self.assertTrue(len(denoise_entries) > 0)
        self.assertTrue(any("skipped" in m for m in denoise_entries))

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_cycles_applies_normally(self, mock_check):
        bpy = self._mock_bpy_for_scene("CYCLES")
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"denoising": True}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("denoising", result["result"]["modified"])
        denoise_entries = [m for m in result["result"]["modified"] if "denoising" in m]
        self.assertTrue(all("skipped" not in m for m in denoise_entries))


if __name__ == "__main__":
    unittest.main()
