# -*- coding: utf-8 -*-
"""Unit tests for node reader — especially node-specific property reading."""

from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------


class _MockProp:
    """Minimal mock for a Blender RNA property descriptor."""

    def __init__(
        self,
        identifier: str,
        prop_type: str = "ENUM",
        is_readonly: bool = False,
    ):
        self.identifier = identifier
        self.type = prop_type
        self.is_readonly = is_readonly


class _MockColorRampElement:
    def __init__(self, position: float, color: tuple[float, ...]):
        self.position = position
        self.color = color


class _MockColorRamp:
    def __init__(
        self,
        interpolation: str = "LINEAR",
        color_mode: str = "RGB",
        hue_interpolation: str = "NEAR",
        elements: list[_MockColorRampElement] | None = None,
    ):
        self.interpolation = interpolation
        self.color_mode = color_mode
        self.hue_interpolation = hue_interpolation
        self.elements = elements or []

    # Make type().__name__ return "ColorRamp"
    class __class_override:
        __name__ = "ColorRamp"

    def __class_getitem__(cls, item):
        return cls


# Patch __class__ so type(instance).__name__ == "ColorRamp"
_MockColorRamp.__name__ = "ColorRamp"  # type: ignore[attr-defined]


class _MockCurvePoint:
    def __init__(self, location: tuple[float, float], handle_type: str = "AUTO"):
        self.location = location
        self.handle_type = handle_type


class _MockCurve:
    def __init__(self, points: list[_MockCurvePoint] | None = None):
        self.points = points or []


class _MockCurveMapping:
    def __init__(
        self,
        curves: list[_MockCurve] | None = None,
        use_clip: bool = False,
        clip_min_x: float = 0.0,
        clip_min_y: float = 0.0,
        clip_max_x: float = 1.0,
        clip_max_y: float = 1.0,
    ):
        self.curves = curves or []
        self.use_clip = use_clip
        self.clip_min_x = clip_min_x
        self.clip_min_y = clip_min_y
        self.clip_max_x = clip_max_x
        self.clip_max_y = clip_max_y


_MockCurveMapping.__name__ = "CurveMapping"  # type: ignore[attr-defined]


class _MockImage:
    def __init__(self, name: str, filepath: str = ""):
        self.name = name
        self.filepath = filepath


_MockImage.__name__ = "Image"  # type: ignore[attr-defined]


class _MockSocket:
    def __init__(self, name: str, socket_type: str = "VALUE", is_linked: bool = False, default_value: Any = None):
        self.name = name
        self.type = socket_type
        self.is_linked = is_linked
        if default_value is not None:
            self.default_value = default_value


class _MockBlRna:
    def __init__(self, props: list[_MockProp]):
        self.properties = props


class _MockNode:
    """Mock node with bl_rna.properties and arbitrary attributes."""

    def __init__(
        self,
        name: str = "TestNode",
        bl_idname: str = "ShaderNodeMath",
        node_type: str = "MATH",
        rna_props: list[_MockProp] | None = None,
        **attrs: Any,
    ):
        self.name = name
        self.bl_idname = bl_idname
        self.label = name
        self.type = node_type
        self.location = MagicMock(x=0.0, y=0.0)
        self.inputs: list[_MockSocket] = []
        self.outputs: list[_MockSocket] = []
        if rna_props is not None:
            self.bl_rna = _MockBlRna(rna_props)
        for k, v in attrs.items():
            setattr(self, k, v)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSerializeColorRamp(unittest.TestCase):
    def test_basic_color_ramp(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_color_ramp

        ramp = _MockColorRamp(
            interpolation="EASE",
            color_mode="RGB",
            hue_interpolation="NEAR",
            elements=[
                _MockColorRampElement(0.0, (0.0, 0.0, 0.0, 1.0)),
                _MockColorRampElement(0.5, (1.0, 0.5, 0.0, 1.0)),
                _MockColorRampElement(1.0, (1.0, 1.0, 1.0, 1.0)),
            ],
        )
        result = _serialize_color_ramp(ramp)

        self.assertEqual(result["interpolation"], "EASE")
        self.assertEqual(result["color_mode"], "RGB")
        self.assertEqual(len(result["elements"]), 3)
        self.assertAlmostEqual(result["elements"][0]["position"], 0.0)
        self.assertAlmostEqual(result["elements"][1]["position"], 0.5)
        self.assertEqual(result["elements"][1]["color"], [1.0, 0.5, 0.0, 1.0])


class TestSerializeCurveMapping(unittest.TestCase):
    def test_basic_curve_mapping(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_curve_mapping

        mapping = _MockCurveMapping(
            curves=[
                _MockCurve(
                    points=[
                        _MockCurvePoint((0.0, 0.0), "AUTO"),
                        _MockCurvePoint((1.0, 1.0), "AUTO"),
                    ]
                ),
            ],
            use_clip=True,
            clip_max_x=2.0,
        )
        result = _serialize_curve_mapping(mapping)

        self.assertTrue(result["use_clip"])
        self.assertEqual(result["clip_max_x"], 2.0)
        self.assertEqual(len(result["curves"]), 1)
        self.assertEqual(len(result["curves"][0]["points"]), 2)
        self.assertEqual(result["curves"][0]["points"][0]["location"], [0.0, 0.0])
        self.assertEqual(result["curves"][0]["points"][1]["handle_type"], "AUTO")


class TestSerializePropValue(unittest.TestCase):
    def test_enum_property(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_prop_value

        prop = _MockProp("operation", "ENUM")
        node = _MockNode(operation="ADD")
        self.assertEqual(_serialize_prop_value(node, prop), "ADD")

    def test_boolean_property(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_prop_value

        prop = _MockProp("use_clamp", "BOOLEAN")
        node = _MockNode(use_clamp=True)
        self.assertTrue(_serialize_prop_value(node, prop))

    def test_float_property(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_prop_value

        prop = _MockProp("factor", "FLOAT")
        node = _MockNode(factor=0.75)
        self.assertAlmostEqual(_serialize_prop_value(node, prop), 0.75)

    def test_pointer_color_ramp(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_prop_value

        ramp = _MockColorRamp(
            interpolation="LINEAR",
            elements=[_MockColorRampElement(0.0, (0.0, 0.0, 0.0, 1.0))],
        )
        # Need type(ramp).__name__ == "ColorRamp"
        prop = _MockProp("color_ramp", "POINTER", is_readonly=True)
        node = _MockNode(color_ramp=ramp)
        result = _serialize_prop_value(node, prop)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["interpolation"], "LINEAR")
        self.assertEqual(len(result["elements"]), 1)

    def test_pointer_image(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_prop_value

        img = _MockImage("my_texture.png", "/textures/my_texture.png")
        prop = _MockProp("image", "POINTER")
        node = _MockNode(image=img)
        result = _serialize_prop_value(node, prop)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["name"], "my_texture.png")
        self.assertEqual(result["filepath"], "/textures/my_texture.png")

    def test_pointer_image_no_filepath(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_prop_value

        img = _MockImage("generated_img")
        prop = _MockProp("image", "POINTER")
        node = _MockNode(image=img)
        result = _serialize_prop_value(node, prop)
        self.assertEqual(result, {"name": "generated_img"})

    def test_pointer_named_datablock(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_prop_value

        obj = MagicMock()
        obj.name = "Cube"
        type(obj).__name__ = "Object"
        prop = _MockProp("object", "POINTER")
        node = _MockNode(object=obj)
        result = _serialize_prop_value(node, prop)
        self.assertEqual(result, "Cube")

    def test_none_value_returns_none(self):
        from blender_mcp_addon.handlers.nodes.reader import _serialize_prop_value

        prop = _MockProp("image", "POINTER")
        node = _MockNode(image=None)
        self.assertIsNone(_serialize_prop_value(node, prop))


class TestReadNodeProperties(unittest.TestCase):
    def test_reads_enum_and_bool(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node_properties

        rna_props = [
            _MockProp("operation", "ENUM"),
            _MockProp("use_clamp", "BOOLEAN"),
        ]
        node = _MockNode(
            rna_props=rna_props,
            operation="MULTIPLY",
            use_clamp=False,
        )
        result = _read_node_properties(node)
        self.assertEqual(result["operation"], "MULTIPLY")
        self.assertFalse(result["use_clamp"])

    def test_skips_base_node_props(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node_properties

        rna_props = [
            _MockProp("name", "STRING"),  # base prop — should be skipped
            _MockProp("operation", "ENUM"),
        ]
        node = _MockNode(rna_props=rna_props, operation="ADD")
        result = _read_node_properties(node)
        self.assertNotIn("name", result)
        self.assertIn("operation", result)

    def test_skips_readonly_simple_props(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node_properties

        rna_props = [
            _MockProp("internal_id", "INT", is_readonly=True),
            _MockProp("operation", "ENUM"),
        ]
        node = _MockNode(rna_props=rna_props, internal_id=42, operation="ADD")
        result = _read_node_properties(node)
        self.assertNotIn("internal_id", result)
        self.assertIn("operation", result)

    def test_includes_readonly_pointer_color_ramp(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node_properties

        ramp = _MockColorRamp(
            interpolation="B_SPLINE",
            elements=[
                _MockColorRampElement(0.0, (0.0, 0.0, 0.0, 1.0)),
                _MockColorRampElement(1.0, (1.0, 1.0, 1.0, 1.0)),
            ],
        )
        rna_props = [
            _MockProp("color_ramp", "POINTER", is_readonly=True),
        ]
        node = _MockNode(rna_props=rna_props, color_ramp=ramp)
        result = _read_node_properties(node)
        self.assertIn("color_ramp", result)
        self.assertEqual(result["color_ramp"]["interpolation"], "B_SPLINE")
        self.assertEqual(len(result["color_ramp"]["elements"]), 2)

    def test_skips_collection_props(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node_properties

        rna_props = [
            _MockProp("items", "COLLECTION"),
            _MockProp("operation", "ENUM"),
        ]
        node = _MockNode(rna_props=rna_props, items=[], operation="ADD")
        result = _read_node_properties(node)
        self.assertNotIn("items", result)
        self.assertIn("operation", result)

    def test_skips_node_tree_prop(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node_properties

        rna_props = [
            _MockProp("node_tree", "POINTER"),
        ]
        node = _MockNode(rna_props=rna_props, node_tree=MagicMock(name="MyGroup"))
        result = _read_node_properties(node)
        self.assertNotIn("node_tree", result)

    def test_no_bl_rna_returns_empty(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node_properties

        node = _MockNode()
        # Remove bl_rna
        if hasattr(node, "bl_rna"):
            del node.bl_rna
        result = _read_node_properties(node)
        self.assertEqual(result, {})


class TestReadNodeFull(unittest.TestCase):
    """Test that _read_node includes properties in depth='full' mode."""

    def test_full_depth_includes_properties(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node

        rna_props = [
            _MockProp("operation", "ENUM"),
            _MockProp("use_clamp", "BOOLEAN"),
        ]
        node = _MockNode(
            name="Math",
            bl_idname="ShaderNodeMath",
            rna_props=rna_props,
            operation="ADD",
            use_clamp=True,
        )
        result = _read_node(node, depth="full")
        self.assertIn("properties", result)
        self.assertEqual(result["properties"]["operation"], "ADD")
        self.assertTrue(result["properties"]["use_clamp"])

    def test_summary_depth_excludes_properties(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node

        rna_props = [_MockProp("operation", "ENUM")]
        node = _MockNode(rna_props=rna_props, operation="ADD")
        result = _read_node(node, depth="summary")
        self.assertNotIn("properties", result)

    def test_full_depth_color_ramp_node(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node

        ramp = _MockColorRamp(
            interpolation="CONSTANT",
            color_mode="HSV",
            hue_interpolation="FAR",
            elements=[
                _MockColorRampElement(0.0, (1.0, 0.0, 0.0, 1.0)),
                _MockColorRampElement(0.3, (0.0, 1.0, 0.0, 1.0)),
                _MockColorRampElement(1.0, (0.0, 0.0, 1.0, 1.0)),
            ],
        )
        rna_props = [
            _MockProp("color_ramp", "POINTER", is_readonly=True),
        ]
        node = _MockNode(
            name="ColorRamp",
            bl_idname="ShaderNodeValToRGB",
            rna_props=rna_props,
            color_ramp=ramp,
        )
        result = _read_node(node, depth="full")
        props = result["properties"]
        self.assertEqual(props["color_ramp"]["interpolation"], "CONSTANT")
        self.assertEqual(props["color_ramp"]["color_mode"], "HSV")
        self.assertEqual(len(props["color_ramp"]["elements"]), 3)
        self.assertEqual(props["color_ramp"]["elements"][0]["color"], [1.0, 0.0, 0.0, 1.0])
        self.assertAlmostEqual(props["color_ramp"]["elements"][1]["position"], 0.3)

    def test_no_properties_key_when_empty(self):
        from blender_mcp_addon.handlers.nodes.reader import _read_node

        node = _MockNode(rna_props=[])
        result = _read_node(node, depth="full")
        self.assertNotIn("properties", result)


if __name__ == "__main__":
    unittest.main()
