# -*- coding: utf-8 -*-
"""Schema validation tests for all 27 tools."""

from __future__ import annotations

import os
import unittest

os.environ["MCP_ADAPTER"] = "mock"

from blender_mcp.schemas.tools import TOOL_DEFINITIONS, get_tool

ANN_KEYS = ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]


class TestToolCount(unittest.TestCase):
    def test_exactly_27(self):
        self.assertEqual(len(TOOL_DEFINITIONS), 27)

    def test_unique_names(self):
        names = [t["name"] for t in TOOL_DEFINITIONS]
        self.assertEqual(len(names), len(set(names)))

    def test_blender_prefix(self):
        for t in TOOL_DEFINITIONS:
            self.assertTrue(t["name"].startswith("blender_"), t["name"])


class TestSchemaStructure(unittest.TestCase):
    def test_type_object(self):
        for t in TOOL_DEFINITIONS:
            self.assertEqual(t["inputSchema"]["type"], "object", t["name"])

    def test_no_additional_properties(self):
        for t in TOOL_DEFINITIONS:
            self.assertFalse(t["inputSchema"].get("additionalProperties", True), t["name"])

    def test_no_payload_wrapper(self):
        for t in TOOL_DEFINITIONS:
            props = t["inputSchema"].get("properties", {})
            self.assertNotIn("payload", props, t["name"])

    def test_properties_have_types(self):
        for t in TOOL_DEFINITIONS:
            for pname, pdef in t["inputSchema"].get("properties", {}).items():
                has_type = "type" in pdef or "enum" in pdef or "description" in pdef
                self.assertTrue(has_type, f"{t['name']}.{pname} missing type")

    def test_required_is_list(self):
        for t in TOOL_DEFINITIONS:
            req = t["inputSchema"].get("required")
            if req is not None:
                self.assertIsInstance(req, list, t["name"])


class TestAnnotations(unittest.TestCase):
    def test_all_have_annotations(self):
        for t in TOOL_DEFINITIONS:
            self.assertIn("annotations", t, t["name"])

    def test_annotation_keys(self):
        for t in TOOL_DEFINITIONS:
            for k in ANN_KEYS:
                self.assertIn(k, t["annotations"], f"{t['name']} missing {k}")

    def test_perception_readonly(self):
        perception = [
            t
            for t in TOOL_DEFINITIONS
            if t["name"].startswith("blender_get_") or t["name"] == "blender_capture_viewport"
        ]
        for t in perception:
            self.assertTrue(t["annotations"]["readOnlyHint"], t["name"])
            self.assertTrue(t["annotations"]["idempotentHint"], t["name"])

    def test_script_destructive(self):
        t = get_tool("blender_execute_script")
        assert t is not None
        self.assertTrue(t["annotations"]["destructiveHint"])


class TestInternalCapability(unittest.TestCase):
    def test_all_have_capability(self):
        for t in TOOL_DEFINITIONS:
            self.assertIn("internal_capability", t, t["name"])
            self.assertTrue(t["internal_capability"], t["name"])


class TestGetToolLookup(unittest.TestCase):
    def test_known_tool(self):
        self.assertIsNotNone(get_tool("blender_get_objects"))

    def test_unknown_tool(self):
        self.assertIsNone(get_tool("nonexistent"))


class TestEnumValues(unittest.TestCase):
    def test_create_object_types(self):
        t = get_tool("blender_create_object")
        assert t is not None
        enum = t["inputSchema"]["properties"]["object_type"]["enum"]
        for val in ["MESH", "LIGHT", "CAMERA", "CURVE", "EMPTY", "ARMATURE", "TEXT"]:
            self.assertIn(val, enum)

    def test_create_object_primitives(self):
        t = get_tool("blender_create_object")
        assert t is not None
        enum = t["inputSchema"]["properties"]["primitive"]["enum"]
        for val in ["cube", "sphere", "cylinder", "cone", "plane", "torus", "icosphere"]:
            self.assertIn(val, enum)

    def test_material_actions(self):
        t = get_tool("blender_manage_material")
        assert t is not None
        enum = t["inputSchema"]["properties"]["action"]["enum"]
        for val in ["create", "edit", "assign", "unassign", "duplicate", "delete"]:
            self.assertIn(val, enum)

    def test_import_export_formats(self):
        t = get_tool("blender_import_export")
        assert t is not None
        enum = t["inputSchema"]["properties"]["format"]["enum"]
        for val in ["FBX", "OBJ", "GLTF", "GLB", "USD", "STL"]:
            self.assertIn(val, enum)


class TestRequiredParams(unittest.TestCase):
    def test_get_object_data_requires_name(self):
        t = get_tool("blender_get_object_data")
        assert t is not None
        self.assertIn("name", t["inputSchema"]["required"])

    def test_create_object_requires_name(self):
        t = get_tool("blender_create_object")
        assert t is not None
        self.assertIn("name", t["inputSchema"]["required"])

    def test_modify_object_requires_name(self):
        t = get_tool("blender_modify_object")
        assert t is not None
        self.assertIn("name", t["inputSchema"]["required"])

    def test_manage_material_requires_action_name(self):
        t = get_tool("blender_manage_material")
        assert t is not None
        self.assertIn("action", t["inputSchema"]["required"])
        self.assertIn("name", t["inputSchema"]["required"])

    def test_execute_operator_requires_operator(self):
        t = get_tool("blender_execute_operator")
        assert t is not None
        self.assertIn("operator", t["inputSchema"]["required"])

    def test_execute_script_requires_code(self):
        t = get_tool("blender_execute_script")
        assert t is not None
        self.assertIn("code", t["inputSchema"]["required"])

    def test_import_export_requires_all(self):
        t = get_tool("blender_import_export")
        for r in ["action", "format", "filepath"]:
            self.assertIn(r, t["inputSchema"]["required"])

    def test_no_required_for_optional_tools(self):
        optional = [
            "blender_get_objects",
            "blender_get_materials",
            "blender_get_scene",
            "blender_get_collections",
            "blender_get_images",
            "blender_capture_viewport",
            "blender_get_selection",
            "blender_setup_scene",
        ]
        for name in optional:
            t = get_tool(name)
            assert t is not None
            self.assertNotIn("required", t["inputSchema"], name)


if __name__ == "__main__":
    unittest.main()
