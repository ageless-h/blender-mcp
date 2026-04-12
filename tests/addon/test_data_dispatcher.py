# -*- coding: utf-8 -*-
"""Unit tests for data dispatcher — create/read/write/delete/list/link."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


class TestDataCreate(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.data.dispatcher import data_create

        result = data_create({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_missing_type(self, mock_registry, mock_check):
        mock_check.return_value = (True, MagicMock())
        mock_registry.parse_type.return_value = None
        from blender_mcp_addon.handlers.data.dispatcher import data_create

        result = data_create({"name": "test"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_missing_name(self, mock_registry, mock_check):
        mock_check.return_value = (True, MagicMock())
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = MagicMock()
        from blender_mcp_addon.handlers.data.dispatcher import data_create

        result = data_create({"type": "object"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("name", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_unsupported_type(self, mock_registry, mock_check):
        mock_check.return_value = (True, MagicMock())
        mock_registry.parse_type.return_value = None
        from blender_mcp_addon.handlers.data.dispatcher import data_create

        result = data_create({"type": "quantum"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "unsupported_type")

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_successful_create(self, mock_registry, mock_check):
        handler = MagicMock()
        handler.create.return_value = {"name": "Cube", "type": "MESH"}
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = handler
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_create

        result = data_create({"type": "object", "name": "Cube"}, started=_started())
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["name"], "Cube")


class TestDataRead(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_successful_read(self, mock_registry, mock_check):
        handler = MagicMock()
        handler.read.return_value = {"name": "Cube", "type": "MESH"}
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = handler
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_read

        result = data_read({"type": "object", "name": "Cube"}, started=_started())
        self.assertTrue(result["ok"])

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_read_not_found(self, mock_registry, mock_check):
        handler = MagicMock()
        handler.read.side_effect = KeyError("Cube")
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = handler
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_read

        result = data_read({"type": "object", "name": "Ghost"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")


class TestDataWrite(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_missing_properties(self, mock_registry, mock_check):
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = MagicMock()
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_write

        result = data_write({"type": "object", "name": "Cube"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("properties", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_successful_write(self, mock_registry, mock_check):
        handler = MagicMock()
        handler.write.return_value = {"name": "Cube", "modified": ["location"]}
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = handler
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_write

        result = data_write(
            {"type": "object", "name": "Cube", "properties": {"location": [1, 2, 3]}},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result["result"]["success"])

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_write_not_found(self, mock_registry, mock_check):
        handler = MagicMock()
        handler.write.side_effect = KeyError("Cube")
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = handler
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_write

        result = data_write(
            {"type": "object", "name": "Ghost", "properties": {"location": [0, 0, 0]}},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")


class TestDataDelete(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_successful_delete(self, mock_registry, mock_check):
        handler = MagicMock()
        handler.delete.return_value = {"name": "Cube", "deleted": True}
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = handler
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_delete

        result = data_delete({"type": "object", "name": "Cube"}, started=_started())
        self.assertTrue(result["ok"])
        self.assertTrue(result["result"]["success"])


class TestDataList(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    @patch("blender_mcp_addon.handlers.data.dispatcher.HandlerRegistry")
    def test_successful_list(self, mock_registry, mock_check):
        handler = MagicMock()
        handler.list_items.return_value = [{"name": "Cube"}, {"name": "Sphere"}]
        mock_registry.parse_type.return_value = "object"
        mock_registry.get.return_value = handler
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_list

        result = data_list({"type": "object"}, started=_started())
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["result"]), 2)


class TestDataLink(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    def test_link_missing_source(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_link

        result = data_link({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("source", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    def test_link_missing_target(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_link

        result = data_link({"source": {"type": "material", "name": "Mat"}}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("target", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.data.dispatcher.check_bpy_available")
    def test_link_source_missing_fields(self, mock_check):
        mock_check.return_value = (True, MagicMock())
        from blender_mcp_addon.handlers.data.dispatcher import data_link

        result = data_link(
            {"source": {"type": "material"}, "target": {"type": "object", "name": "Cube"}},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertIn("type", result["error"]["message"])


if __name__ == "__main__":
    unittest.main()
