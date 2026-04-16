# -*- coding: utf-8 -*-
"""Tests for version support matrix."""

from __future__ import annotations

import unittest

from blender_mcp.versioning.support_matrix import SupportMatrix


class TestSupportMatrix(unittest.TestCase):
    def test_support_matrix_defaults(self):
        matrix = SupportMatrix()
        self.assertEqual(matrix.lts_versions, [])
        self.assertIsNone(matrix.latest_version)
        self.assertEqual(matrix.deprecated_versions, [])

    def test_is_supported_latest_version(self):
        matrix = SupportMatrix(lts_versions=["4.2", "4.5"], latest_version="5.0")
        self.assertTrue(matrix.is_supported("5.0"))

    def test_is_supported_lts_version(self):
        matrix = SupportMatrix(lts_versions=["4.2", "4.5"], latest_version="5.0")
        self.assertTrue(matrix.is_supported("4.2"))
        self.assertTrue(matrix.is_supported("4.5"))

    def test_is_supported_unsupported_version(self):
        matrix = SupportMatrix(lts_versions=["4.2", "4.5"], latest_version="5.0")
        self.assertFalse(matrix.is_supported("3.6"))
        self.assertFalse(matrix.is_supported("4.0"))

    def test_is_supported_empty_matrix(self):
        matrix = SupportMatrix()
        self.assertFalse(matrix.is_supported("4.2"))

    def test_is_supported_no_latest(self):
        matrix = SupportMatrix(lts_versions=["4.2", "4.5"])
        self.assertTrue(matrix.is_supported("4.2"))
        self.assertFalse(matrix.is_supported("5.0"))

    def test_is_supported_no_lts(self):
        matrix = SupportMatrix(latest_version="5.0")
        self.assertTrue(matrix.is_supported("5.0"))
        self.assertFalse(matrix.is_supported("4.2"))


if __name__ == "__main__":
    unittest.main()
