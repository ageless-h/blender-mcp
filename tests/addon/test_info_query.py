# -*- coding: utf-8 -*-
"""Unit tests for info/query handler — reports, last_op, undo_history, etc."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


class TestInfoQueryHandler(unittest.TestCase):
    """Test cases for info_query handler."""

    def setUp(self):
        """Set up mock bpy for each test."""
        self.mock_bpy = MagicMock()
        self.mock_context = MagicMock()
        self.mock_scene = MagicMock()
        self.mock_bpy.context = self.mock_context
        self.mock_context.scene = self.mock_scene
        self.mock_scene.name = "TestScene"
        self.mock_scene.objects = []
        self.mock_scene.frame_current = 1
        self.mock_scene.frame_start = 1
        self.mock_scene.frame_end = 250
        self.mock_scene.render = MagicMock()
        self.mock_scene.render.engine = "BLENDER_EEVEE"
        self.mock_scene.render.resolution_x = 1920
        self.mock_scene.render.resolution_y = 1080

    def test_invalid_query_type(self):
        """Test that invalid query type returns error."""
        from blender_mcp_addon.handlers.info.query import info_query

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "invalid_type"}, started=_started())
            self.assertFalse(result["ok"])
            self.assertIn("Invalid query type", result["error"]["message"])

    def test_missing_type_parameter(self):
        """Test that missing type parameter returns error."""
        from blender_mcp_addon.handlers.info.query import info_query

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({}, started=_started())
            self.assertFalse(result["ok"])
            self.assertIn("'type' parameter is required", result["error"]["message"])

    def test_query_version(self):
        """Test version query returns valid result."""
        from blender_mcp_addon.handlers.info.query import info_query

        self.mock_bpy.app = MagicMock()
        self.mock_bpy.app.version = (5, 1, 0)
        self.mock_bpy.app.version_string = "5.1.0"

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "version"}, started=_started())
            self.assertTrue(result["ok"])
            self.assertIn("blender_version", result["result"])
            self.assertEqual(result["result"]["blender_version"], [5, 1, 0])

    def test_query_scene_stats(self):
        """Test scene stats query returns valid result."""
        from blender_mcp_addon.handlers.info.query import info_query

        # Mock depsgraph
        mock_depsgraph = MagicMock()
        self.mock_context.evaluated_depsgraph_get.return_value = mock_depsgraph

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "scene_stats"}, started=_started())
            self.assertTrue(result["ok"])
            stats = result["result"]
            self.assertEqual(stats["scene_name"], "TestScene")
            self.assertEqual(stats["object_count"], 0)
            self.assertEqual(stats["mesh_objects"], 0)

    def test_query_selection_empty(self):
        """Test selection query with empty selection."""
        from blender_mcp_addon.handlers.info.query import info_query

        self.mock_context.mode = "OBJECT"
        self.mock_context.selected_objects = []
        self.mock_context.active_object = None
        self.mock_context.view_layer = MagicMock()
        self.mock_context.view_layer.objects = MagicMock()
        self.mock_context.view_layer.objects.active = None

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "selection"}, started=_started())
            self.assertTrue(result["ok"])
            selection = result["result"]
            self.assertEqual(selection["selected_count"], 0)

    def test_query_mode(self):
        """Test mode query returns current mode."""
        from blender_mcp_addon.handlers.info.query import info_query

        self.mock_context.mode = "EDIT_MESH"

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "mode"}, started=_started())
            self.assertTrue(result["ok"])
            self.assertEqual(result["result"]["mode"], "EDIT_MESH")

    def test_query_last_op_empty(self):
        """Test last_op query with no recorded operation."""
        import blender_mcp_addon.handlers.info.query as query_module
        from blender_mcp_addon.handlers.info.query import info_query

        query_module._last_op_info = {}

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "last_op"}, started=_started())
            self.assertTrue(result["ok"])
            last_op = result["result"]
            self.assertIsNone(last_op["operator"])

    def test_query_last_op_with_data(self):
        """Test last_op query with recorded operation."""
        from blender_mcp_addon.handlers.info.query import info_query, record_last_op

        # Record an operation
        record_last_op(
            operator="object.add",
            success=True,
            result="Created cube",
            reports=[],
            duration_ms=15.5,
            params={"type": "CUBE"},
        )

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "last_op"}, started=_started())
            self.assertTrue(result["ok"])
            last_op = result["result"]
            self.assertEqual(last_op["operator"], "object.add")
            self.assertTrue(last_op["success"])
            self.assertEqual(last_op["duration_ms"], 15.5)

    def test_query_undo_history_empty(self):
        """Test undo_history query with empty history."""
        from blender_mcp_addon.handlers.info.query import info_query

        mock_wm = MagicMock()
        self.mock_context.window_manager = mock_wm
        # No undo_stack attribute
        del mock_wm.undo_stack

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "undo_history"}, started=_started())
            self.assertTrue(result["ok"])
            history = result["result"]
            self.assertEqual(history["history"], [])
            self.assertFalse(history["can_undo"])

    def test_query_reports_empty(self):
        """Test reports query with no reports."""
        from blender_mcp_addon.handlers.info.query import info_query

        mock_wm = MagicMock()
        self.mock_context.window_manager = mock_wm
        # No reports attribute
        del mock_wm.reports

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "reports"}, started=_started())
            self.assertTrue(result["ok"])
            reports = result["result"]
            self.assertEqual(reports["reports"], [])
            self.assertEqual(reports["count"], 0)

    def test_query_memory(self):
        """Test memory query returns memory info."""
        from blender_mcp_addon.handlers.info.query import info_query

        self.mock_bpy.utils = MagicMock()

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "memory"}, started=_started())
            self.assertTrue(result["ok"])
            self.assertIn("total_mb", result["result"])

    def test_query_changes_initial(self):
        """Test changes query returns change tracking."""
        # Reset change tracking
        import blender_mcp_addon.handlers.info.query as query_module
        from blender_mcp_addon.handlers.info.query import info_query

        query_module._change_tracking = {
            "modified_objects": set(),
            "added_objects": set(),
            "deleted_objects": set(),
        }

        with patch(
            "blender_mcp_addon.handlers.info.query.check_bpy_available",
            return_value=(True, self.mock_bpy),
        ):
            result = info_query({"type": "changes"}, started=_started())
            self.assertTrue(result["ok"])
            changes = result["result"]
            self.assertEqual(changes["modified_objects"], [])
            self.assertEqual(changes["added_objects"], [])
            self.assertEqual(changes["deleted_objects"], [])


class TestInfoTypeEnum(unittest.TestCase):
    """Test InfoType enum values."""

    def test_all_types_defined(self):
        """Test that all expected info types are defined."""
        from blender_mcp_addon.handlers.info.query import InfoType

        expected_types = [
            "reports",
            "last_op",
            "undo_history",
            "scene_stats",
            "selection",
            "mode",
            "changes",
            "viewport_capture",
            "version",
            "memory",
            "node_types",
        ]

        for type_name in expected_types:
            self.assertIn(type_name, [t.value for t in InfoType])


class TestRecordLastOp(unittest.TestCase):
    """Test record_last_op function."""

    def test_record_and_retrieve(self):
        """Test that recorded operation can be retrieved."""
        import blender_mcp_addon.handlers.info.query as query_module
        from blender_mcp_addon.handlers.info.query import record_last_op

        record_last_op(
            operator="mesh.primitive_cube_add",
            success=True,
            result="Added cube",
            reports=[{"type": "INFO", "message": "Cube added"}],
            duration_ms=25.3,
            params={"size": 2, "location": [0, 0, 0]},
        )

        self.assertEqual(query_module._last_op_info["operator"], "mesh.primitive_cube_add")
        self.assertTrue(query_module._last_op_info["success"])
        self.assertEqual(len(query_module._last_op_info["reports"]), 1)


if __name__ == "__main__":
    unittest.main()
