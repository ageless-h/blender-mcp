# -*- coding: utf-8 -*-
"""Test that catalog and schemas stay in sync."""

from __future__ import annotations

import unittest

from blender_mcp.schemas.tools import TOOL_DEFINITIONS
from catalog_utils.catalog import minimal_capability_set, new_tool_scope_map


class TestCatalogSchemaSync(unittest.TestCase):
    def test_capability_count_matches(self):
        catalog_caps = minimal_capability_set()
        schema_caps = [t.get("internal_capability") for t in TOOL_DEFINITIONS if "internal_capability" in t]
        self.assertEqual(len(catalog_caps), len(schema_caps))

    def test_all_catalog_names_in_schema(self):
        catalog_caps = minimal_capability_set()
        schema_caps = {t.get("internal_capability") for t in TOOL_DEFINITIONS if "internal_capability" in t}
        for cap in catalog_caps:
            self.assertIn(cap.name, schema_caps, f"Catalog capability {cap.name} not in schema")

    def test_all_schema_names_in_catalog(self):
        catalog_names = {c.name for c in minimal_capability_set()}
        for tool in TOOL_DEFINITIONS:
            cap = tool.get("internal_capability")
            if cap:
                self.assertIn(cap, catalog_names, f"Schema capability {cap} not in catalog")

    def test_scope_map_matches_capability_set(self):
        catalog_caps = minimal_capability_set()
        scope_map = new_tool_scope_map()
        catalog_names = {c.name for c in catalog_caps}
        scope_names = set(scope_map.keys())
        self.assertEqual(catalog_names, scope_names)

    def test_scope_count_matches_capability_count(self):
        catalog_caps = minimal_capability_set()
        scope_map = new_tool_scope_map()
        self.assertEqual(len(catalog_caps), len(scope_map))

    def test_all_capabilities_have_min_version(self):
        catalog_caps = minimal_capability_set()
        for cap in catalog_caps:
            self.assertIsNotNone(cap.min_version, f"{cap.name} missing min_version")
            self.assertEqual(cap.min_version, "4.2")

    def test_perception_layer_count(self):
        catalog_caps = minimal_capability_set()
        perception = [
            c for c in catalog_caps if c.name.startswith("blender.get_") or c.name == "blender.capture_viewport"
        ]
        self.assertEqual(len(perception), 11)

    def test_declarative_layer_count(self):
        catalog_caps = minimal_capability_set()
        declarative_names = ["blender.edit_nodes", "blender.edit_animation", "blender.edit_sequencer"]
        declarative = [c for c in catalog_caps if c.name in declarative_names]
        self.assertEqual(len(declarative), 3)

    def test_imperative_layer_count(self):
        catalog_caps = minimal_capability_set()
        imperative_names = [
            "blender.create_object",
            "blender.modify_object",
            "blender.manage_material",
            "blender.manage_modifier",
            "blender.manage_collection",
            "blender.manage_uv",
            "blender.manage_constraints",
            "blender.manage_physics",
            "blender.setup_scene",
            "blender.edit_mesh",
        ]
        imperative = [c for c in catalog_caps if c.name in imperative_names]
        self.assertEqual(len(imperative), 10)

    def test_fallback_layer_count(self):
        catalog_caps = minimal_capability_set()
        fallback_names = [
            "blender.execute_operator",
            "blender.execute_script",
            "blender.import_export",
            "blender.render_scene",
            "blender.batch_execute",
        ]
        fallback = [c for c in catalog_caps if c.name in fallback_names]
        self.assertEqual(len(fallback), 5)

    def test_total_capability_count(self):
        catalog_caps = minimal_capability_set()
        self.assertEqual(len(catalog_caps), 29)


if __name__ == "__main__":
    unittest.main()
