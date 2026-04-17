# -*- coding: utf-8 -*-
"""Tests for version compatibility checking."""

from __future__ import annotations

import unittest

from catalog_utils.catalog import (
    CapabilityMeta,
    _lt,
    _parse_version,
    capability_availability,
)


class TestVersionParsing(unittest.TestCase):
    def test_parse_simple_version(self):
        self.assertEqual(_parse_version("4.2"), (4, 2))
        self.assertEqual(_parse_version("5.0"), (5, 0))
        self.assertEqual(_parse_version("5.1"), (5, 1))

    def test_parse_triple_version(self):
        self.assertEqual(_parse_version("4.2.12"), (4, 2, 12))
        self.assertEqual(_parse_version("5.0.1"), (5, 0, 1))

    def test_parse_version_with_suffix(self):
        self.assertEqual(_parse_version("4.2 LTS"), (4, 2))
        self.assertEqual(_parse_version("5.0+"), (5, 0))

    def test_parse_invalid_version(self):
        self.assertIsNone(_parse_version(""))
        self.assertIsNone(_parse_version("invalid"))

    def test_parse_single_digit(self):
        self.assertEqual(_parse_version("4"), (4,))
        self.assertEqual(_parse_version("5"), (5,))


class TestVersionComparison(unittest.TestCase):
    def test_lt_simple(self):
        self.assertTrue(_lt((4, 2), (5, 0)))
        self.assertTrue(_lt((4, 2), (4, 3)))
        self.assertFalse(_lt((5, 0), (4, 2)))
        self.assertFalse(_lt((4, 2), (4, 2)))

    def test_lt_different_lengths(self):
        self.assertTrue(_lt((4,), (4, 2)))
        self.assertTrue(_lt((4, 2), (4, 2, 1)))
        self.assertFalse(_lt((4, 2), (4,)))

    def test_lt_with_zero_padding(self):
        self.assertFalse(_lt((4, 0), (4, 0, 0)))
        self.assertTrue(_lt((4, 0), (4, 0, 1)))


class TestCapabilityAvailability(unittest.TestCase):
    def test_available_no_version_constraint(self):
        cap = CapabilityMeta(name="test", description="Test capability")
        available, reason = capability_availability(cap, "4.2")
        self.assertTrue(available)
        self.assertIsNone(reason)

    def test_available_no_target_version(self):
        cap = CapabilityMeta(name="test", description="Test", min_version="4.2")
        available, reason = capability_availability(cap, None)
        self.assertTrue(available)
        self.assertIsNone(reason)

    def test_version_below_min(self):
        cap = CapabilityMeta(name="test", description="Test", min_version="5.0")
        available, reason = capability_availability(cap, "4.2")
        self.assertFalse(available)
        self.assertEqual(reason, "version_below_min")

    def test_version_at_min(self):
        cap = CapabilityMeta(name="test", description="Test", min_version="4.2")
        available, reason = capability_availability(cap, "4.2")
        self.assertTrue(available)
        self.assertIsNone(reason)

    def test_version_above_max(self):
        cap = CapabilityMeta(name="test", description="Test", max_version="4.5")
        available, reason = capability_availability(cap, "5.0")
        self.assertFalse(available)
        self.assertEqual(reason, "version_at_or_above_max")

    def test_version_below_max(self):
        cap = CapabilityMeta(name="test", description="Test", max_version="5.0")
        available, reason = capability_availability(cap, "4.2")
        self.assertTrue(available)
        self.assertIsNone(reason)

    def test_version_within_range(self):
        cap = CapabilityMeta(
            name="test",
            description="Test",
            min_version="4.2",
            max_version="5.0",
        )
        available, reason = capability_availability(cap, "4.5")
        self.assertTrue(available)
        self.assertIsNone(reason)

    def test_version_outside_range(self):
        cap = CapabilityMeta(
            name="test",
            description="Test",
            min_version="4.5",
            max_version="5.0",
        )
        available, reason = capability_availability(cap, "4.2")
        self.assertFalse(available)
        self.assertEqual(reason, "version_below_min")

    def test_invalid_target_version(self):
        cap = CapabilityMeta(name="test", description="Test", min_version="4.2")
        available, reason = capability_availability(cap, "invalid")
        self.assertTrue(available)
        self.assertIsNone(reason)


class TestCapabilityMeta(unittest.TestCase):
    def test_capability_meta_defaults(self):
        cap = CapabilityMeta(name="test", description="Test capability")
        self.assertEqual(cap.name, "test")
        self.assertEqual(cap.description, "Test capability")
        self.assertEqual(cap.scopes, [])
        self.assertIsNone(cap.min_version)
        self.assertIsNone(cap.max_version)

    def test_capability_meta_full(self):
        cap = CapabilityMeta(
            name="test",
            description="Test",
            scopes=["read", "write"],
            min_version="4.2",
            max_version="5.0",
        )
        self.assertEqual(cap.scopes, ["read", "write"])
        self.assertEqual(cap.min_version, "4.2")
        self.assertEqual(cap.max_version, "5.0")


if __name__ == "__main__":
    unittest.main()
