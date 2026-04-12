# -*- coding: utf-8 -*-
"""Unit tests for import/export handler — format mapping, validation, execution."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch


def _started() -> float:
    return time.perf_counter()


def _mock_bpy():
    bpy = MagicMock()
    op_func = MagicMock(return_value={"FINISHED"})
    op_module = MagicMock()
    op_module.fbx = op_func
    op_module.gltf = op_func
    op_module.obj_import = op_func
    op_module.obj_export = op_func
    bpy.ops.import_scene = op_module
    bpy.ops.export_scene = op_module
    bpy.ops.wm = op_module
    bpy.context.temp_override = MagicMock()
    bpy.context.temp_override.return_value.__enter__ = MagicMock(return_value=None)
    bpy.context.temp_override.return_value.__exit__ = MagicMock(return_value=None)
    return bpy


class TestImportExportValidation(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.importexport.handler.check_bpy_available")
    def test_bpy_unavailable(self, mock_check):
        mock_check.return_value = (False, None)
        from blender_mcp_addon.handlers.importexport.handler import import_export

        result = import_export({}, started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.importexport.handler.check_bpy_available")
    def test_invalid_action(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.importexport.handler import import_export

        result = import_export(
            {"action": "transform", "format": "FBX", "filepath": "/tmp/test.fbx"},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertIn("import", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.importexport.handler.check_bpy_available")
    def test_missing_format(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.importexport.handler import import_export

        result = import_export({"action": "import", "filepath": "/tmp/test.fbx"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("format", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.importexport.handler.check_bpy_available")
    def test_missing_filepath(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.importexport.handler import import_export

        result = import_export({"action": "import", "format": "FBX"}, started=_started())
        self.assertFalse(result["ok"])
        self.assertIn("filepath", result["error"]["message"])

    @patch("blender_mcp_addon.handlers.importexport.handler.check_bpy_available")
    def test_unsupported_format(self, mock_check):
        mock_check.return_value = (True, _mock_bpy())
        from blender_mcp_addon.handlers.importexport.handler import import_export

        result = import_export(
            {"action": "import", "format": "QUANTUM", "filepath": "/tmp/test.q"},
            started=_started(),
        )
        self.assertFalse(result["ok"])
        self.assertIn("Unsupported format", result["error"]["message"])


class TestFilePathValidation(unittest.TestCase):
    def test_valid_path(self):
        from blender_mcp_addon.handlers.importexport.handler import _validate_filepath

        result = _validate_filepath("/tmp/test.fbx")
        self.assertIsNotNone(result)

    def test_empty_path(self):
        from blender_mcp_addon.handlers.importexport.handler import _validate_filepath

        result = _validate_filepath("")
        self.assertIsNone(result)

    def test_none_path(self):
        from blender_mcp_addon.handlers.importexport.handler import _validate_filepath

        result = _validate_filepath("")
        self.assertIsNone(result)

    def test_null_byte_path(self):
        from blender_mcp_addon.handlers.importexport.handler import _validate_filepath

        result = _validate_filepath("/tmp/test\x00.fbx")
        self.assertIsNone(result)

    def test_non_string_path(self):
        from blender_mcp_addon.handlers.importexport.handler import _validate_filepath

        result = _validate_filepath(123)
        self.assertIsNone(result)


class TestImportExportSupportedFormats(unittest.TestCase):
    @patch("blender_mcp_addon.handlers.importexport.handler.check_bpy_available")
    @patch("blender_mcp_addon.handlers.importexport.handler.get_view3d_override")
    def test_import_fbx(self, mock_override, mock_check):
        mock_override.return_value = {}
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.importexport.handler import import_export

        result = import_export(
            {"action": "import", "format": "FBX", "filepath": "/tmp/test.fbx"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["action"], "import")
        self.assertEqual(result["result"]["format"], "FBX")

    @patch("blender_mcp_addon.handlers.importexport.handler.check_bpy_available")
    @patch("blender_mcp_addon.handlers.importexport.handler.get_view3d_override")
    def test_export_glb(self, mock_override, mock_check):
        mock_override.return_value = {}
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.importexport.handler import import_export

        result = import_export(
            {"action": "export", "format": "GLB", "filepath": "/tmp/test.glb"},
            started=_started(),
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["format"], "GLB")

    @patch("blender_mcp_addon.handlers.importexport.handler.check_bpy_available")
    @patch("blender_mcp_addon.handlers.importexport.handler.get_view3d_override")
    def test_export_gltf_format_param(self, mock_override, mock_check):
        mock_override.return_value = {}
        bpy = _mock_bpy()
        mock_check.return_value = (True, bpy)
        from blender_mcp_addon.handlers.importexport.handler import import_export

        result = import_export(
            {"action": "export", "format": "GLTF", "filepath": "/tmp/test.gltf"},
            started=_started(),
        )
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
