# -*- coding: utf-8 -*-
"""Unit tests for metadata system — registry, resolver, and types."""

from __future__ import annotations

import unittest

from blender_mcp_addon.metadata import (
    get_all_supported_properties,
    get_blender_version,
    get_handler_metadata,
    get_readable_properties,
    register_handler_metadata,
    resolve_property_path,
    resolve_property_value,
)
from blender_mcp_addon.metadata.types import HandlerMetadata, PropertyMetadata


class TestPropertyMetadata(unittest.TestCase):
    """Tests for PropertyMetadata dataclass."""

    def test_basic_property(self):
        """Create a basic property metadata."""
        prop = PropertyMetadata(
            name="mass",
            blender_path="settings.mass",
            prop_type="float",
            default=1.0,
            description="Mass in kg",
        )
        self.assertEqual(prop.name, "mass")
        self.assertEqual(prop.blender_path, "settings.mass")
        self.assertEqual(prop.prop_type, "float")
        self.assertEqual(prop.default, 1.0)
        self.assertIsNone(prop.min_value)
        self.assertIsNone(prop.max_value)

    def test_property_with_constraints(self):
        """Create a property with min/max constraints."""
        prop = PropertyMetadata(
            name="levels",
            blender_path="levels",
            prop_type="int",
            default=1,
            min_value=0,
            max_value=12,
        )
        self.assertEqual(prop.min_value, 0)
        self.assertEqual(prop.max_value, 12)

    def test_enum_property(self):
        """Create an enum property."""
        prop = PropertyMetadata(
            name="operation",
            blender_path="operation",
            prop_type="enum",
            enum_items=("DIFFERENCE", "UNION", "INTERSECT"),
            default="DIFFERENCE",
        )
        self.assertEqual(prop.enum_items, ("DIFFERENCE", "UNION", "INTERSECT"))

    def test_version_constrained_property(self):
        """Create a property with version constraints."""
        prop = PropertyMetadata(
            name="use_axis",
            blender_path="use_axis",
            prop_type="vector",
            default=(True, False, False),
            version_min=(5, 0, 0),
            version_max=None,
        )
        self.assertEqual(prop.version_min, (5, 0, 0))
        self.assertIsNone(prop.version_max)


class TestHandlerMetadata(unittest.TestCase):
    """Tests for HandlerMetadata dataclass."""

    def test_basic_handler(self):
        """Create a basic handler metadata."""
        handler = HandlerMetadata(
            handler_type="TEST_MOD",
            category="modifier",
            container_path="",
            properties={
                "strength": PropertyMetadata(
                    name="strength",
                    blender_path="strength",
                    prop_type="float",
                    default=1.0,
                )
            },
            readable_properties=("strength",),
        )
        self.assertEqual(handler.handler_type, "TEST_MOD")
        self.assertEqual(handler.category, "modifier")
        self.assertIn("strength", handler.properties)
        self.assertEqual(handler.readable_properties, ("strength",))


class TestMetadataRegistry(unittest.TestCase):
    """Tests for metadata registry functions."""

    def test_get_builtin_modifier_metadata(self):
        """Retrieve built-in MIRROR modifier metadata."""
        meta = get_handler_metadata("MIRROR", "modifier")
        self.assertIsNotNone(meta)
        self.assertEqual(meta.handler_type, "MIRROR")
        self.assertIn("use_clip", meta.properties)

    def test_get_builtin_constraint_metadata(self):
        """Retrieve built-in COPY_LOCATION constraint metadata."""
        meta = get_handler_metadata("COPY_LOCATION", "constraint")
        self.assertIsNotNone(meta)
        self.assertEqual(meta.handler_type, "COPY_LOCATION")
        self.assertIn("target", meta.properties)

    def test_get_builtin_physics_metadata(self):
        """Retrieve built-in CLOTH physics metadata."""
        meta = get_handler_metadata("CLOTH", "physics")
        self.assertIsNotNone(meta)
        self.assertEqual(meta.handler_type, "CLOTH")
        self.assertIn("mass", meta.properties)

    def test_get_nonexistent_metadata(self):
        """Return None for non-existent handler type."""
        meta = get_handler_metadata("NONEXISTENT", "modifier")
        self.assertIsNone(meta)

    def test_register_custom_metadata(self):
        """Register and retrieve custom handler metadata."""
        custom = HandlerMetadata(
            handler_type="CUSTOM_MOD",
            category="modifier",
            container_path="",
            properties={
                "custom_prop": PropertyMetadata(
                    name="custom_prop",
                    blender_path="custom_prop",
                    prop_type="float",
                    default=0.5,
                )
            },
            readable_properties=("custom_prop",),
        )
        register_handler_metadata(custom)

        retrieved = get_handler_metadata("CUSTOM_MOD", "modifier")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.handler_type, "CUSTOM_MOD")

    def test_get_readable_properties(self):
        """Get readable properties for a handler type."""
        props = get_readable_properties("SUBSURF", "modifier")
        self.assertIn("levels", props)
        self.assertIn("render_levels", props)

    def test_get_readable_properties_nonexistent(self):
        """Return empty tuple for non-existent handler."""
        props = get_readable_properties("NONEXISTENT", "modifier")
        self.assertEqual(props, ())


class TestMetadataResolver(unittest.TestCase):
    """Tests for metadata resolver functions."""

    def test_resolve_simple_property_path(self):
        """Resolve a simple property path without container."""
        result = resolve_property_path("SUBSURF", "modifier", "levels")
        self.assertIsNotNone(result)
        container, prop = result
        self.assertEqual(container, "")
        self.assertEqual(prop, "levels")

    def test_resolve_nested_property_path(self):
        """Resolve a nested property path with container."""
        result = resolve_property_path("CLOTH", "physics", "mass")
        self.assertIsNotNone(result)
        container, prop = result
        self.assertEqual(container, "settings")
        self.assertEqual(prop, "mass")

    def test_resolve_nonexistent_property(self):
        """Return None for non-existent property."""
        result = resolve_property_path("SUBSURF", "modifier", "nonexistent")
        self.assertIsNone(result)

    def test_resolve_property_value_simple(self):
        """Resolve a simple property value."""
        result = resolve_property_value("BEVEL", "modifier", "width", 0.5)
        self.assertIsNotNone(result)
        container, prop, value = result
        self.assertEqual(prop, "width")
        self.assertEqual(value, 0.5)

    def test_get_all_supported_properties(self):
        """Get all supported properties for a handler."""
        props = get_all_supported_properties("ARRAY", "modifier")
        self.assertIn("count", props)
        self.assertIn("fit_type", props)

    def test_get_blender_version_returns_tuple(self):
        """get_blender_version returns a tuple."""
        version = get_blender_version()
        self.assertIsInstance(version, tuple)
        self.assertGreaterEqual(len(version), 2)


class TestVersionAwareResolution(unittest.TestCase):
    """Tests for version-aware property resolution."""

    def test_mirror_use_x_blender_4x(self):
        """MIRROR use_x property is valid in Blender 4.x."""
        result = resolve_property_path("MIRROR", "modifier", "use_x", (4, 2, 0))
        self.assertIsNotNone(result)

    def test_mirror_use_axis_blender_50(self):
        """MIRROR use_axis property is valid in Blender 5.0+."""
        result = resolve_property_path("MIRROR", "modifier", "use_axis", (5, 0, 0))
        self.assertIsNotNone(result)

    def test_mirror_use_x_blender_50_returns_use_axis(self):
        """Requesting use_x in Blender 5.0+ uses use_axis special handling."""
        result = resolve_property_value("MIRROR", "modifier", "use_x", True, (5, 0, 0))
        self.assertIsNotNone(result)
        if result is not None:
            container, prop, value = result
            self.assertEqual(prop, "use_axis")
            self.assertEqual(value, (0, True))


class TestExpandedMetadata(unittest.TestCase):
    """Tests for newly added modifier, constraint, and physics metadata."""

    def test_decimate_modifier_metadata(self):
        """DECIMATE modifier has metadata."""
        meta = get_handler_metadata("DECIMATE", "modifier")
        self.assertIsNotNone(meta)
        self.assertIn("ratio", meta.properties)
        self.assertIn("decimate_type", meta.properties)

    def test_remesh_modifier_metadata(self):
        """REMESH modifier has metadata."""
        meta = get_handler_metadata("REMESH", "modifier")
        self.assertIsNotNone(meta)
        self.assertIn("voxel_size", meta.properties)
        self.assertIn("mode", meta.properties)

    def test_shrinkwrap_modifier_metadata(self):
        """SHRINKWRAP modifier has metadata."""
        meta = get_handler_metadata("SHRINKWRAP", "modifier")
        self.assertIsNotNone(meta)
        self.assertIn("target", meta.properties)
        self.assertIn("wrap_method", meta.properties)

    def test_ik_constraint_metadata(self):
        """IK constraint has metadata."""
        meta = get_handler_metadata("IK", "constraint")
        self.assertIsNotNone(meta)
        self.assertIn("target", meta.properties)
        self.assertIn("chain_count", meta.properties)
        self.assertIn("iterations", meta.properties)

    def test_track_to_constraint_metadata(self):
        """TRACK_TO constraint has metadata."""
        meta = get_handler_metadata("TRACK_TO", "constraint")
        self.assertIsNotNone(meta)
        self.assertIn("track_axis", meta.properties)
        self.assertIn("up_axis", meta.properties)

    def test_rigid_body_physics_metadata(self):
        """RIGID_BODY physics has metadata."""
        meta = get_handler_metadata("RIGID_BODY", "physics")
        self.assertIsNotNone(meta)
        self.assertIn("mass", meta.properties)
        self.assertIn("friction", meta.properties)
        self.assertIn("collision_shape", meta.properties)

    def test_particle_physics_metadata(self):
        """PARTICLE physics has metadata."""
        meta = get_handler_metadata("PARTICLE", "physics")
        self.assertIsNotNone(meta)
        self.assertIn("count", meta.properties)
        self.assertIn("lifetime", meta.properties)

    def test_force_field_physics_metadata(self):
        """FORCE_FIELD physics has metadata."""
        meta = get_handler_metadata("FORCE_FIELD", "physics")
        self.assertIsNotNone(meta)
        self.assertIn("strength", meta.properties)
        self.assertIn("falloff_type", meta.properties)


if __name__ == "__main__":
    unittest.main()
