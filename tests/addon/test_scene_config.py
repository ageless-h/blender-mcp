# -*- coding: utf-8 -*-
"""Unit tests for scene/config handler — render, output, world, timeline settings."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _mock_bpy():
    bpy = MagicMock()
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250
    bpy.context.scene.render.fps = 24
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.filepath = "/tmp/render"
    bpy.context.scene.render.film_transparent = False
    bpy.context.scene.world = None
    bpy.data.worlds.new.return_value = MagicMock(use_nodes=False)
    return bpy


class TestSceneSetupDispatch(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_empty_payload(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({}, started=_started())
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["modified"], [])

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_set_engine(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"engine": "CYCLES"}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("engine", result["result"]["modified"])
        self.assertEqual(bpy.context.scene.render.engine, "CYCLES")

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_set_resolution(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"resolution_x": 3840, "resolution_y": 2160}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("resolution_x", result["result"]["modified"])
        self.assertIn("resolution_y", result["result"]["modified"])
        self.assertEqual(bpy.context.scene.render.resolution_x, 3840)
        self.assertEqual(bpy.context.scene.render.resolution_y, 2160)

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_set_fps(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"fps": 60}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("fps", result["result"]["modified"])
        self.assertEqual(bpy.context.scene.render.fps, 60)

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_set_frame_range(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"frame_start": 10, "frame_end": 200}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("frame_start", result["result"]["modified"])
        self.assertIn("frame_end", result["result"]["modified"])

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_set_frame_current(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"frame_current": 42}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("frame_current", result["result"]["modified"])
        bpy.context.scene.frame_set.assert_called_once_with(42)

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_set_output_format(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"output_format": "OPEN_EXR"}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("output_format", result["result"]["modified"])

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_set_film_transparent(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"film_transparent": True}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("film_transparent", result["result"]["modified"])
        self.assertTrue(bpy.context.scene.render.film_transparent)

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_multiple_settings(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup(
            {"engine": "CYCLES", "fps": 30, "resolution_x": 1280, "resolution_y": 720},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["result"]["modified"]), 4)

    @patch("blender_mcp_addon.handlers.scene.config.check_bpy_available")
    def test_result_includes_current_state(self, mock_check):
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.scene.config import scene_setup

        result = scene_setup({"fps": 48}, started=_started())
        self.assertTrue(result["ok"])
        self.assertIn("engine", result["result"])
        self.assertIn("resolution", result["result"])
        self.assertIn("fps", result["result"])
        self.assertIn("frame_range", result["result"])


if __name__ == "__main__":
    unittest.main()
