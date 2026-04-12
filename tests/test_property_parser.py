# -*- coding: utf-8 -*-
"""Tests for the property_parser module."""

import unittest

from blender_mcp_addon.handlers.utils.property_parser import coerce_value


class TestCoerceValue(unittest.TestCase):
    def test_none_passthrough(self):
        self.assertIsNone(coerce_value(None))

    def test_bool_strings(self):
        self.assertTrue(coerce_value("true"))
        self.assertTrue(coerce_value("yes"))
        self.assertFalse(coerce_value("false"))
        self.assertFalse(coerce_value("no"))

    def test_numeric_strings(self):
        self.assertEqual(coerce_value("42"), 42)
        self.assertAlmostEqual(coerce_value("3.14"), 3.14)

    def test_hex_color(self):
        result = coerce_value("#ff0000")
        self.assertEqual(len(result), 4)
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 0.0)
        self.assertAlmostEqual(result[2], 0.0)
        self.assertAlmostEqual(result[3], 1.0)

    def test_hex_color_with_alpha(self):
        result = coerce_value("#ff000080")
        self.assertEqual(len(result), 4)
        self.assertAlmostEqual(result[3], 128 / 255.0, places=3)

    def test_vector3_string(self):
        result = coerce_value("Vector3(1, 2, 3)")
        self.assertEqual(result, (1.0, 2.0, 3.0))

    def test_vector_string(self):
        result = coerce_value("Vector(10, 20, 30)")
        self.assertEqual(result, (10.0, 20.0, 30.0))

    def test_color_string(self):
        result = coerce_value("Color(1, 0, 0, 1)")
        self.assertEqual(result, (1.0, 0.0, 0.0, 1.0))

    def test_color_string_rgb(self):
        result = coerce_value("Color(0.5, 0.5, 0.5)")
        self.assertEqual(result, (0.5, 0.5, 0.5, 1.0))

    def test_list_to_color_target(self):
        target = (0.0, 0.0, 0.0, 1.0)
        result = coerce_value([1, 0, 0, 1], target)
        self.assertEqual(result, (1, 0, 0, 1))

    def test_list_to_vector_target(self):
        result = coerce_value([1, 2, 3], target=None)
        self.assertEqual(result, [1, 2, 3])

    def test_bool_target(self):
        self.assertTrue(coerce_value("yes", False))
        self.assertFalse(coerce_value("no", True))

    def test_float_target(self):
        self.assertAlmostEqual(coerce_value("2.5", 1.0), 2.5)

    def test_int_target(self):
        self.assertEqual(coerce_value("7", 0), 7)

    def test_plain_string_passthrough(self):
        self.assertEqual(coerce_value("hello"), "hello")

    def test_list_passthrough_no_target(self):
        self.assertEqual(coerce_value([1, 2, 3]), [1, 2, 3])

    def test_euler_string(self):
        result = coerce_value("Euler(0.5, 1.0, 1.5)")
        self.assertEqual(result, (0.5, 1.0, 1.5))


if __name__ == "__main__":
    unittest.main()
