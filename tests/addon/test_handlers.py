# -*- coding: utf-8 -*-
"""Unit tests for the handler system."""
from __future__ import annotations

import unittest

from blender_mcp_addon.handlers.base import BaseHandler
from blender_mcp_addon.handlers.registry import HandlerRegistry
from blender_mcp_addon.handlers.response import (
    _error,
    _ok,
    invalid_params_error,
    not_found_error,
    unsupported_type_error,
)
from blender_mcp_addon.handlers.types import (
    ATTACHED_TYPES,
    PSEUDO_TYPES,
    DataType,
    get_collection_name,
    is_attached_type,
    is_pseudo_type,
)


class TestDataType(unittest.TestCase):
    """Tests for DataType enumeration."""

    def test_core_object_types(self):
        """Test core object types are defined."""
        self.assertEqual(DataType.OBJECT.value, "object")
        self.assertEqual(DataType.MESH.value, "mesh")
        self.assertEqual(DataType.CURVE.value, "curve")
        self.assertEqual(DataType.ARMATURE.value, "armature")

    def test_appearance_types(self):
        """Test appearance types are defined."""
        self.assertEqual(DataType.MATERIAL.value, "material")
        self.assertEqual(DataType.TEXTURE.value, "texture")
        self.assertEqual(DataType.IMAGE.value, "image")
        self.assertEqual(DataType.WORLD.value, "world")

    def test_organization_types(self):
        """Test organization types are defined."""
        self.assertEqual(DataType.COLLECTION.value, "collection")
        self.assertEqual(DataType.SCENE.value, "scene")
        self.assertEqual(DataType.WORKSPACE.value, "workspace")

    def test_pseudo_types(self):
        """Test pseudo-types are defined."""
        self.assertEqual(DataType.CONTEXT.value, "context")
        self.assertEqual(DataType.PREFERENCES.value, "preferences")
        self.assertIn(DataType.CONTEXT, PSEUDO_TYPES)
        self.assertIn(DataType.PREFERENCES, PSEUDO_TYPES)

    def test_attached_types(self):
        """Test attached types are defined."""
        self.assertEqual(DataType.MODIFIER.value, "modifier")
        self.assertEqual(DataType.CONSTRAINT.value, "constraint")
        self.assertIn(DataType.MODIFIER, ATTACHED_TYPES)
        self.assertIn(DataType.CONSTRAINT, ATTACHED_TYPES)

    def test_collection_mapping(self):
        """Test DataType to bpy.data collection mapping."""
        self.assertEqual(get_collection_name(DataType.OBJECT), "objects")
        self.assertEqual(get_collection_name(DataType.MESH), "meshes")
        self.assertEqual(get_collection_name(DataType.MATERIAL), "materials")
        self.assertEqual(get_collection_name(DataType.NODE_TREE), "node_groups")
        self.assertIsNone(get_collection_name(DataType.CONTEXT))

    def test_is_pseudo_type(self):
        """Test is_pseudo_type helper."""
        self.assertTrue(is_pseudo_type(DataType.CONTEXT))
        self.assertTrue(is_pseudo_type(DataType.PREFERENCES))
        self.assertFalse(is_pseudo_type(DataType.OBJECT))
        self.assertFalse(is_pseudo_type(DataType.MESH))

    def test_is_attached_type(self):
        """Test is_attached_type helper."""
        self.assertTrue(is_attached_type(DataType.MODIFIER))
        self.assertTrue(is_attached_type(DataType.CONSTRAINT))
        self.assertFalse(is_attached_type(DataType.OBJECT))
        self.assertFalse(is_attached_type(DataType.CONTEXT))


class TestHandlerRegistry(unittest.TestCase):
    """Tests for HandlerRegistry."""

    def setUp(self):
        """Clear registry before each test."""
        HandlerRegistry.clear()

    def tearDown(self):
        """Clear registry after each test."""
        HandlerRegistry.clear()

    def test_register_handler(self):
        """Test handler registration via decorator."""
        @HandlerRegistry.register
        class TestHandler(BaseHandler):
            data_type = DataType.OBJECT
            def create(self, name, params): return {}
            def read(self, name, path, params): return {}
            def write(self, name, properties, params): return {}
            def delete(self, name, params): return {}
            def list_items(self, filter_params): return {}

        self.assertTrue(HandlerRegistry.is_registered(DataType.OBJECT))
        self.assertIsNotNone(HandlerRegistry.get(DataType.OBJECT))

    def test_register_without_data_type_raises(self):
        """Test registration without data_type raises ValueError."""
        with self.assertRaises(ValueError):
            @HandlerRegistry.register
            class BadHandler(BaseHandler):
                def create(self, name, params): return {}
                def read(self, name, path, params): return {}
                def write(self, name, properties, params): return {}
                def delete(self, name, params): return {}
                def list_items(self, filter_params): return {}

    def test_parse_type(self):
        """Test type string parsing."""
        self.assertEqual(HandlerRegistry.parse_type("object"), DataType.OBJECT)
        self.assertEqual(HandlerRegistry.parse_type("MESH"), DataType.MESH)
        self.assertEqual(HandlerRegistry.parse_type("Material"), DataType.MATERIAL)
        self.assertIsNone(HandlerRegistry.parse_type("invalid_type"))

    def test_get_or_error_raises(self):
        """Test get_or_error raises for unregistered type."""
        with self.assertRaises(KeyError):
            HandlerRegistry.get_or_error(DataType.OBJECT)

    def test_registered_types(self):
        """Test registered_types returns correct list."""
        @HandlerRegistry.register
        class TestHandler1(BaseHandler):
            data_type = DataType.OBJECT
            def create(self, name, params): return {}
            def read(self, name, path, params): return {}
            def write(self, name, properties, params): return {}
            def delete(self, name, params): return {}
            def list_items(self, filter_params): return {}

        @HandlerRegistry.register
        class TestHandler2(BaseHandler):
            data_type = DataType.MESH
            def create(self, name, params): return {}
            def read(self, name, path, params): return {}
            def write(self, name, properties, params): return {}
            def delete(self, name, params): return {}
            def list_items(self, filter_params): return {}

        types = HandlerRegistry.registered_types()
        self.assertIn(DataType.OBJECT, types)
        self.assertIn(DataType.MESH, types)
        self.assertEqual(len(types), 2)


class TestResponseHelpers(unittest.TestCase):
    """Tests for response helper functions."""

    def test_ok_response(self):
        """Test _ok creates correct response."""
        import time
        started = time.perf_counter()
        result = _ok(result={"test": "value"}, started=started)

        self.assertTrue(result["ok"])
        self.assertEqual(result["result"], {"test": "value"})
        self.assertNotIn("error", result)
        self.assertIsInstance(result["timing_ms"], int)

    def test_error_response(self):
        """Test _error creates correct response."""
        import time
        started = time.perf_counter()
        result = _error(
            code="test_error",
            message="Test message",
            started=started,
            data={"key": "value"},
        )

        self.assertFalse(result["ok"])
        self.assertNotIn("result", result)
        self.assertEqual(result["error"]["code"], "test_error")
        self.assertEqual(result["error"]["message"], "Test message")
        self.assertEqual(result["error"]["data"], {"key": "value"})

    def test_not_found_error(self):
        """Test not_found_error helper."""
        import time
        started = time.perf_counter()
        result = not_found_error("object", "Cube", started)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")
        self.assertIn("Cube", result["error"]["message"])

    def test_invalid_params_error(self):
        """Test invalid_params_error helper."""
        import time
        started = time.perf_counter()
        result = invalid_params_error("Missing required field", started)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")

    def test_unsupported_type_error(self):
        """Test unsupported_type_error helper."""
        import time
        started = time.perf_counter()
        result = unsupported_type_error("unknown_type", started)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "unsupported_type")


class TestOperatorExecutor(unittest.TestCase):
    """Tests for operator execution."""

    def test_get_operator_scopes(self):
        """Test operator scope mapping."""
        from blender_mcp_addon.handlers.operator.executor import get_operator_scopes

        self.assertEqual(get_operator_scopes("mesh.primitive_cube_add"), ["mesh:execute"])
        self.assertEqual(get_operator_scopes("render.render"), ["render:execute"])
        self.assertEqual(get_operator_scopes("export_scene.gltf"), ["export:execute"])
        self.assertEqual(get_operator_scopes("unknown"), ["operator:execute"])


class TestInfoQuery(unittest.TestCase):
    """Tests for info query types."""

    def test_info_type_enum(self):
        """Test InfoType enumeration."""
        from blender_mcp_addon.handlers.info.query import InfoType

        self.assertEqual(InfoType.REPORTS.value, "reports")
        self.assertEqual(InfoType.LAST_OP.value, "last_op")
        self.assertEqual(InfoType.UNDO_HISTORY.value, "undo_history")
        self.assertEqual(InfoType.SCENE_STATS.value, "scene_stats")
        self.assertEqual(InfoType.SELECTION.value, "selection")
        self.assertEqual(InfoType.MODE.value, "mode")
        self.assertEqual(InfoType.CHANGES.value, "changes")
        self.assertEqual(InfoType.VIEWPORT_CAPTURE.value, "viewport_capture")
        self.assertEqual(InfoType.VERSION.value, "version")
        self.assertEqual(InfoType.MEMORY.value, "memory")


class TestScriptExecutor(unittest.TestCase):
    """Tests for script execution security."""

    def test_default_disabled(self):
        """Test script execution is disabled by default."""
        from blender_mcp_addon.handlers.script.executor import is_script_execution_enabled

        self.assertFalse(is_script_execution_enabled())

    def test_configure_script_execution(self):
        """Test script execution configuration."""
        from blender_mcp_addon.handlers.script.executor import configure_script_execution, is_script_execution_enabled

        configure_script_execution(enabled=True)
        self.assertTrue(is_script_execution_enabled())

        configure_script_execution(enabled=False)
        self.assertFalse(is_script_execution_enabled())


class TestAllowlist(unittest.TestCase):
    """Tests for security allowlist."""

    def test_default_allowed_tools(self):
        """Test default allowlist includes core tools."""
        from blender_mcp.security.allowlist import Allowlist

        allowlist = Allowlist()

        self.assertTrue(allowlist.is_allowed("blender.get_objects"))
        self.assertTrue(allowlist.is_allowed("blender.get_object_data"))
        self.assertTrue(allowlist.is_allowed("blender.create_object"))
        self.assertTrue(allowlist.is_allowed("blender.execute_operator"))
        self.assertTrue(allowlist.is_allowed("blender.get_scene"))

    def test_script_execute_blocked_by_default(self):
        """Test blender.execute_script is blocked by default."""
        from blender_mcp.security.allowlist import Allowlist

        allowlist = Allowlist()
        self.assertFalse(allowlist.is_allowed("blender.execute_script"))

    def test_enable_script_execute(self):
        """Test enabling blender.execute_script."""
        from blender_mcp.security.allowlist import Allowlist

        allowlist = Allowlist()
        allowlist.enable_script_execute()

        self.assertTrue(allowlist.is_allowed("blender.execute_script"))

    def test_disable_script_execute(self):
        """Test disabling blender.execute_script."""
        from blender_mcp.security.allowlist import Allowlist

        allowlist = Allowlist()
        allowlist.enable_script_execute()
        allowlist.disable_script_execute()

        self.assertFalse(allowlist.is_allowed("blender.execute_script"))


if __name__ == "__main__":
    unittest.main()
