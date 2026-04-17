# -*- coding: utf-8 -*-
"""Unit tests for sequencer editor — add/modify/delete strips, effects, transitions."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _reset_strips_cache():
    """Reset the global _USE_STRIPS_ATTR cache to avoid MagicMock false positives."""
    from blender_mcp_addon.handlers.sequencer import editor

    editor._USE_STRIPS_ATTR = None


def _mock_sequence_editor():
    se = MagicMock()
    se.sequences = MagicMock()
    se.sequences.new.return_value = MagicMock(name="TestStrip", channel=1, frame_start=1, frame_final_end=25)
    return se


def _mock_bpy(has_sequencer=True):
    bpy = MagicMock()
    if has_sequencer:
        bpy.context.scene.sequence_editor = _mock_sequence_editor()
    else:
        bpy.context.scene.sequence_editor = None
    bpy.context.scene.frame_current = 1
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250
    return bpy


class TestSequencerDispatch(unittest.TestCase):
    def setUp(self):
        _reset_strips_cache()

    @patch("blender_mcp_addon.handlers.sequencer.editor.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.sequencer.editor import sequencer_edit

        result = sequencer_edit({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.sequencer.editor.check_bpy_available")
    def test_missing_action(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.sequencer.editor import sequencer_edit

        result = sequencer_edit({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("action", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.sequencer.editor.check_bpy_available")
    def test_unknown_action(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.sequencer.editor import sequencer_edit

        result = sequencer_edit({"action": "teleport"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("Unknown action", result["error"]["message"])


class TestSequencerNoEditor(unittest.TestCase):
    def setUp(self):
        _reset_strips_cache()

    @patch("blender_mcp_addon.handlers.sequencer.editor.check_bpy_available")
    def test_auto_creates_sequence_editor(self, mock_check):
        bpy = _mock_bpy(has_sequencer=False)
        bpy.context.scene.sequence_editor_create.return_value = None
        new_se = MagicMock()
        bpy.context.scene.sequence_editor = None

        def _create_se():
            bpy.context.scene.sequence_editor = new_se

        bpy.context.scene.sequence_editor_create.side_effect = _create_se
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.sequencer.editor import sequencer_edit

        result = sequencer_edit({"action": "unknown_action_x"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("Unknown action", result["error"]["message"])
        bpy.context.scene.sequence_editor_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
