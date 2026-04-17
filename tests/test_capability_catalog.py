# -*- coding: utf-8 -*-
"""Tests for capability catalog."""

from __future__ import annotations

import unittest

from blender_mcp.catalog.catalog import (
    CapabilityCatalog,
    CapabilityMeta,
    capability_availability,
    capability_scope_map,
    capability_to_dict,
    minimal_capability_set,
)


class TestCapabilityCatalog(unittest.TestCase):
    def test_minimal_capability_set_contains_expected(self) -> None:
        capabilities = minimal_capability_set()
        names = {cap.name for cap in capabilities}
        expected = {
            # Perception layer (11)
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
            # Declarative write layer (3)
            "blender.edit_nodes",
            "blender.edit_animation",
            "blender.edit_sequencer",
            # Imperative write layer (10)
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
            # Fallback layer (5)
            "blender.execute_operator",
            "blender.execute_script",
            "blender.import_export",
            "blender.render_scene",
            "blender.batch_execute",
        }
        self.assertEqual(names, expected)
        for cap in capabilities:
            self.assertEqual(cap.min_version, "4.2")
            self.assertTrue(cap.scopes)


class TestCapabilityDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        self.capabilities = minimal_capability_set()
        self.catalog = CapabilityCatalog()
        for capability in self.capabilities:
            self.catalog.register(capability)

    def test_catalog_list_returns_all(self) -> None:
        names = {cap.name for cap in self.catalog.list()}
        self.assertEqual(names, {cap.name for cap in self.capabilities})

    def test_catalog_get_by_name(self) -> None:
        cap = self.catalog.get("blender.get_scene")
        self.assertIsNotNone(cap)
        self.assertEqual(cap.name, "blender.get_scene")

    def test_catalog_get_unknown_returns_none(self) -> None:
        self.assertIsNone(self.catalog.get("nonexistent"))

    def test_capability_availability_below_min(self) -> None:
        cap = CapabilityMeta(name="test", description="t", min_version="4.2")
        available, reason = capability_availability(cap, "4.0")
        self.assertFalse(available)
        self.assertEqual(reason, "version_below_min")

    def test_capability_availability_at_min(self) -> None:
        cap = CapabilityMeta(name="test", description="t", min_version="4.2")
        available, _ = capability_availability(cap, "4.2")
        self.assertTrue(available)

    def test_capability_to_dict_with_version(self) -> None:
        cap = CapabilityMeta(name="test", description="t", min_version="4.2")
        d = capability_to_dict(cap, "4.0")
        self.assertFalse(d["available"])
        self.assertEqual(d["unavailable_reason"], "version_below_min")

        d_ok = capability_to_dict(cap, "4.2")
        self.assertTrue(d_ok["available"])

    def test_scope_map(self) -> None:
        scope_map = capability_scope_map(self.capabilities)
        self.assertIn("blender.get_scene", scope_map)
        self.assertIn("info:read", scope_map["blender.get_scene"])


if __name__ == "__main__":
    unittest.main()
