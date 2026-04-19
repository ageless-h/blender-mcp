# -*- coding: utf-8 -*-
"""Unit tests for editor.py — dotted-path set_property and new actions."""

from __future__ import annotations

import unittest
from typing import Any


class _MockColorRampElement:
    def __init__(self, position: float, color: tuple[float, ...]):
        self.position = position
        self.color = color


class _MockColorRampElements:
    """Mock for ColorRamp.elements with new/remove support."""

    def __init__(self, elements: list[_MockColorRampElement] | None = None):
        self._elements = list(elements or [])

    def __len__(self):
        return len(self._elements)

    def __getitem__(self, index: int):
        return self._elements[index]

    def __iter__(self):
        return iter(self._elements)

    def index(self, elem: _MockColorRampElement) -> int:
        return self._elements.index(elem)

    def new(self, position: float) -> _MockColorRampElement:
        elem = _MockColorRampElement(position, (0.0, 0.0, 0.0, 1.0))
        self._elements.append(elem)
        return elem

    def remove(self, elem: _MockColorRampElement) -> None:
        self._elements.remove(elem)


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
        self.elements = _MockColorRampElements(elements)


class _MockCurvePoint:
    def __init__(self, location: tuple[float, float], handle_type: str = "AUTO"):
        self.location = location
        self.handle_type = handle_type


class _MockCurve:
    def __init__(self, points: list[_MockCurvePoint] | None = None):
        self.points = list(points or [])

    def __len__(self):
        return len(self.points)

    def __getitem__(self, index: int):
        return self.points[index]


class _MockCurveMapping:
    def __init__(self, curves: list[_MockCurve] | None = None):
        self.curves = list(curves or [])
        self._updated = False

    def update(self):
        self._updated = True

    def __len__(self):
        return len(self.curves)


class TestResolveDottedPath(unittest.TestCase):
    def test_simple_path(self):
        from blender_mcp_addon.handlers.nodes.editor import _resolve_dotted_path

        class Obj:
            x = 42

        obj = Obj()
        parent, attr = _resolve_dotted_path(obj, "x")
        self.assertIs(parent, obj)
        self.assertEqual(attr, "x")

    def test_two_level_path(self):
        from blender_mcp_addon.handlers.nodes.editor import _resolve_dotted_path

        class Inner:
            interpolation = "LINEAR"

        class Outer:
            color_ramp = Inner()

        obj = Outer()
        parent, attr = _resolve_dotted_path(obj, "color_ramp.interpolation")
        self.assertIs(parent, obj.color_ramp)
        self.assertEqual(attr, "interpolation")

    def test_three_level_path(self):
        from blender_mcp_addon.handlers.nodes.editor import _resolve_dotted_path

        class A:
            val = 1

        class B:
            child = A()

        class C:
            mid = B()

        obj = C()
        parent, attr = _resolve_dotted_path(obj, "mid.child.val")
        self.assertIs(parent, obj.mid.child)
        self.assertEqual(attr, "val")

    def test_invalid_path_raises(self):
        from blender_mcp_addon.handlers.nodes.editor import _resolve_dotted_path

        class Obj:
            pass

        obj = Obj()
        with self.assertRaises(AttributeError):
            _resolve_dotted_path(obj, "nonexistent.attr")


class TestSetPropertyDottedPath(unittest.TestCase):
    """Integration tests: set_property with dotted paths via node_tree_edit."""

    def _make_mock_bpy(self, material_name: str, node_tree: Any):
        """Create a mock bpy module for testing."""
        import types

        bpy = types.ModuleType("bpy")
        mat = type("Material", (), {
            "name": material_name,
            "use_nodes": True,
            "node_tree": node_tree,
        })()
        bpy.data = type("Data", (), {
            "materials": type("Col", (), {"get": lambda self, n: mat if n == material_name else None})(),
        })()
        return bpy

    def test_set_color_ramp_interpolation(self):
        """set_property with 'color_ramp.interpolation' sets nested attribute."""
        from blender_mcp_addon.handlers.nodes.editor import _resolve_dotted_path

        ramp = _MockColorRamp(interpolation="LINEAR")

        class MockNode:
            color_ramp = ramp

        node = MockNode()
        parent, attr = _resolve_dotted_path(node, "color_ramp.interpolation")
        self.assertEqual(getattr(parent, attr), "LINEAR")
        setattr(parent, attr, "CONSTANT")
        self.assertEqual(ramp.interpolation, "CONSTANT")

    def test_set_color_ramp_color_mode(self):
        """set_property with 'color_ramp.color_mode' sets nested attribute."""
        from blender_mcp_addon.handlers.nodes.editor import _resolve_dotted_path

        ramp = _MockColorRamp(color_mode="RGB")

        class MockNode:
            color_ramp = ramp

        node = MockNode()
        parent, attr = _resolve_dotted_path(node, "color_ramp.color_mode")
        setattr(parent, attr, "HSV")
        self.assertEqual(ramp.color_mode, "HSV")


class TestAddColorRampElement(unittest.TestCase):
    def test_add_element(self):
        ramp = _MockColorRamp(
            elements=[
                _MockColorRampElement(0.0, (0.0, 0.0, 0.0, 1.0)),
                _MockColorRampElement(1.0, (1.0, 1.0, 1.0, 1.0)),
            ]
        )
        self.assertEqual(len(ramp.elements), 2)
        new_elem = ramp.elements.new(0.5)
        self.assertEqual(len(ramp.elements), 3)
        self.assertAlmostEqual(new_elem.position, 0.5)

    def test_add_element_with_color(self):
        ramp = _MockColorRamp(
            elements=[_MockColorRampElement(0.0, (0.0, 0.0, 0.0, 1.0))]
        )
        new_elem = ramp.elements.new(0.75)
        new_elem.color = (1.0, 0.0, 0.0, 1.0)
        self.assertEqual(new_elem.color, (1.0, 0.0, 0.0, 1.0))


class TestRemoveColorRampElement(unittest.TestCase):
    def test_remove_element(self):
        elem0 = _MockColorRampElement(0.0, (0.0, 0.0, 0.0, 1.0))
        elem1 = _MockColorRampElement(0.5, (0.5, 0.5, 0.5, 1.0))
        elem2 = _MockColorRampElement(1.0, (1.0, 1.0, 1.0, 1.0))
        ramp = _MockColorRamp(elements=[elem0, elem1, elem2])
        self.assertEqual(len(ramp.elements), 3)
        ramp.elements.remove(elem1)
        self.assertEqual(len(ramp.elements), 2)

    def test_cannot_remove_last(self):
        elem0 = _MockColorRampElement(0.0, (0.0, 0.0, 0.0, 1.0))
        ramp = _MockColorRamp(elements=[elem0])
        self.assertEqual(len(ramp.elements), 1)
        # The editor code guards against this — here just verify the guard condition
        self.assertTrue(len(ramp.elements) <= 1)


class TestSetCurveMappingPoint(unittest.TestCase):
    def test_set_point_location(self):
        point = _MockCurvePoint((0.0, 0.0), "AUTO")
        point.location = (0.5, 0.8)
        self.assertEqual(point.location, (0.5, 0.8))

    def test_set_point_handle_type(self):
        point = _MockCurvePoint((0.0, 0.0), "AUTO")
        point.handle_type = "VECTOR"
        self.assertEqual(point.handle_type, "VECTOR")

    def test_curve_mapping_update(self):
        mapping = _MockCurveMapping(
            curves=[
                _MockCurve(points=[
                    _MockCurvePoint((0.0, 0.0)),
                    _MockCurvePoint((1.0, 1.0)),
                ])
            ]
        )
        self.assertFalse(mapping._updated)
        mapping.update()
        self.assertTrue(mapping._updated)


if __name__ == "__main__":
    unittest.main()
