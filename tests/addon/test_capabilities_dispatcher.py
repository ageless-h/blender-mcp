# -*- coding: utf-8 -*-
"""Unit tests for capability dispatcher — execute_capability, dispatch, undo."""

from __future__ import annotations

import sys
import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _install_mock_bpy(mock_bpy):
    sys.modules["bpy"] = mock_bpy


def _remove_mock_bpy():
    sys.modules.pop("bpy", None)


class TestExecuteCapabilityValidation(unittest.TestCase):
    def test_non_dict_request(self):
        from blender_mcp_addon.capabilities.base import execute_capability

        result = execute_capability("not a dict")
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_request")

    def test_missing_capability(self):
        from blender_mcp_addon.capabilities.base import execute_capability

        result = execute_capability({})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_request")

    def test_empty_capability(self):
        from blender_mcp_addon.capabilities.base import execute_capability

        result = execute_capability({"capability": ""})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_request")

    def test_non_string_capability(self):
        from blender_mcp_addon.capabilities.base import execute_capability

        result = execute_capability({"capability": 123})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_request")

    def test_none_payload(self):
        from blender_mcp_addon.capabilities.base import execute_capability

        result = execute_capability({"capability": "test.op", "payload": None})
        self.assertIn("ok", result)

    def test_non_dict_payload(self):
        from blender_mcp_addon.capabilities.base import execute_capability

        result = execute_capability({"capability": "test.op", "payload": "bad"})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_request")

    def test_unsupported_capability(self):
        from blender_mcp_addon.capabilities.base import execute_capability

        result = execute_capability({"capability": "something.unknown"})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "unsupported_capability")


class TestCapabilityHandlerRegistry(unittest.TestCase):
    def test_registry_has_handlers(self):
        from blender_mcp_addon.capabilities.base import _CAPABILITY_HANDLERS

        self.assertGreater(len(_CAPABILITY_HANDLERS), 20)

    def test_perception_handlers(self):
        from blender_mcp_addon.capabilities.base import _CAPABILITY_HANDLERS

        perception = [
            "blender.get_objects",
            "blender.get_object_data",
            "blender.get_node_tree",
            "blender.get_animation_data",
            "blender.get_materials",
            "blender.get_scene",
            "blender.get_collections",
            "blender.get_armature_data",
            "blender.get_images",
            "blender.capture_viewport",
            "blender.get_selection",
        ]
        for cap in perception:
            self.assertIn(cap, _CAPABILITY_HANDLERS)

    def test_write_capabilities_set(self):
        from blender_mcp_addon.capabilities.base import _WRITE_CAPABILITIES

        self.assertIn("blender.create_object", _WRITE_CAPABILITIES)
        self.assertIn("blender.execute_script", _WRITE_CAPABILITIES)
        self.assertNotIn("blender.get_objects", _WRITE_CAPABILITIES)


class TestDispatchNewCapability(unittest.TestCase):
    def test_unknown_capability(self):
        from blender_mcp_addon.capabilities.base import _dispatch_new_capability

        result = _dispatch_new_capability("blender.nonexistent", {}, _started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "unsupported_capability")


class TestPushUndoStep(unittest.TestCase):
    @patch("blender_mcp_addon.capabilities.base._push_undo_step")
    def test_write_capability_pushes_undo(self, mock_push):
        from blender_mcp_addon.capabilities.base import (
            _WRITE_CAPABILITIES,
            execute_capability,
        )

        bpy = MagicMock()
        bpy.ops.ed.undo_push = MagicMock()
        _install_mock_bpy(bpy)

        try:
            mock_push.return_value = None
            execute_capability({"capability": "blender.create_object", "payload": {}})
            if "blender.create_object" in _WRITE_CAPABILITIES:
                pass
        finally:
            _remove_mock_bpy()

    def test_push_undo_step_with_mock_bpy(self):
        bpy = MagicMock()
        bpy.ops.ed.undo_push = MagicMock()
        _install_mock_bpy(bpy)

        try:
            from blender_mcp_addon.capabilities.base import _push_undo_step

            _push_undo_step("blender.create_object")
            bpy.ops.ed.undo_push.assert_called_once()
        finally:
            _remove_mock_bpy()


class TestExceptionHandling(unittest.TestCase):
    def test_handler_exception_caught(self):
        from blender_mcp_addon.capabilities.base import _CAPABILITY_HANDLERS, execute_capability

        def failing_handler(payload, started):
            raise RuntimeError("handler crashed")

        original = _CAPABILITY_HANDLERS.get("blender.get_objects")
        _CAPABILITY_HANDLERS["blender.get_objects"] = failing_handler

        try:
            result = execute_capability({"capability": "blender.get_objects"})
            self.assertFalse(result["ok"])
            self.assertEqual(result["error"]["code"], "addon_exception")
            self.assertIn("RuntimeError", result["error"]["message"])
            self.assertIn("traceback", result["error"]["data"])
        finally:
            if original:
                _CAPABILITY_HANDLERS["blender.get_objects"] = original


class TestTimingInResponse(unittest.TestCase):
    def test_response_includes_timing(self):
        from blender_mcp_addon.capabilities.base import execute_capability

        result = execute_capability({"capability": "blender.nonexistent"})
        self.assertIn("timing_ms", result)


if __name__ == "__main__":
    unittest.main()
