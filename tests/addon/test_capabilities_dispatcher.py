# -*- coding: utf-8 -*-
"""Unit tests for capability dispatcher — execute_capability, dispatch, undo."""

from __future__ import annotations

import time
import unittest


def _started() -> float:
    return time.perf_counter()


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


if __name__ == "__main__":
    unittest.main()
