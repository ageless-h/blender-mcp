# -*- coding: utf-8 -*-
"""Unit tests for operator executor — context override, operator dispatch, scope mapping."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


class TestGetOperatorScopes(unittest.TestCase):
    def test_known_category(self):
        from blender_mcp_addon.handlers.operator.executor import get_operator_scopes

        scopes = get_operator_scopes("mesh.primitive_cube_add")
        self.assertEqual(scopes, ["mesh:execute"])

    def test_unknown_category(self):
        from blender_mcp_addon.handlers.operator.executor import get_operator_scopes

        scopes = get_operator_scopes("custom.my_operator")
        self.assertEqual(scopes, ["operator:execute"])

    def test_no_dot(self):
        from blender_mcp_addon.handlers.operator.executor import get_operator_scopes

        scopes = get_operator_scopes("no_dot_operator")
        self.assertEqual(scopes, ["operator:execute"])

    def test_animation_category(self):
        from blender_mcp_addon.handlers.operator.executor import get_operator_scopes

        scopes = get_operator_scopes("anim.keyframe_insert")
        self.assertEqual(scopes, ["animation:execute"])


class TestOperatorExecuteValidation(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.operator.executor.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.operator.executor import operator_execute

        result = operator_execute({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.operator.executor.check_bpy_available")
    def test_missing_operator(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.operator.executor import operator_execute

        result = operator_execute({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("operator", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.operator.executor.check_bpy_available")
    def test_invalid_operator_format(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.operator.executor import operator_execute

        result = operator_execute({"operator": "no_dot"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("Invalid operator", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.operator.executor.check_bpy_available")
    def test_unknown_category(self, mock_check):
        bpy = MagicMock()
        del bpy.ops.nonexistent
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.operator.executor import operator_execute

        result = operator_execute({"operator": "nonexistent.op"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_operator")


class TestResultToString(unittest.TestCase):
    def test_finished_set(self):
        from blender_mcp_addon.handlers.operator.executor import _result_to_string

        self.assertEqual(_result_to_string({"FINISHED"}), "FINISHED")

    def test_cancelled_set(self):
        from blender_mcp_addon.handlers.operator.executor import _result_to_string

        self.assertEqual(_result_to_string({"CANCELLED"}), "CANCELLED")

    def test_running_modal_set(self):
        from blender_mcp_addon.handlers.operator.executor import _result_to_string

        self.assertEqual(_result_to_string({"RUNNING_MODAL"}), "RUNNING_MODAL")

    def test_pass_through_set(self):
        from blender_mcp_addon.handlers.operator.executor import _result_to_string

        self.assertEqual(_result_to_string({"PASS_THROUGH"}), "PASS_THROUGH")

    def test_interface_set(self):
        from blender_mcp_addon.handlers.operator.executor import _result_to_string

        self.assertEqual(_result_to_string({"INTERFACE"}), "INTERFACE")

    def test_non_set_value(self):
        from blender_mcp_addon.handlers.operator.executor import _result_to_string

        self.assertEqual(_result_to_string("FINISHED"), "FINISHED")

    def test_empty_set(self):
        from blender_mcp_addon.handlers.operator.executor import _result_to_string

        result = _result_to_string(set())
        self.assertEqual(result, "set()")


if __name__ == "__main__":
    unittest.main()
