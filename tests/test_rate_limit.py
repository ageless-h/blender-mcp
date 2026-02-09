# -*- coding: utf-8 -*-
"""Tests for rate limiter."""
from __future__ import annotations

import unittest

from blender_mcp.security.rate_limit import RateLimiter


class TestRateLimiter(unittest.TestCase):
    def test_no_limit_allows(self):
        rl = RateLimiter()
        self.assertTrue(rl.allow("blender.get_object_data"))

    def test_limit_enforced(self):
        rl = RateLimiter(limits={"blender.get_object_data": 2}, window_seconds=60.0)
        self.assertTrue(rl.allow("blender.get_object_data"))
        self.assertTrue(rl.allow("blender.get_object_data"))
        self.assertFalse(rl.allow("blender.get_object_data"))

    def test_different_caps_independent(self):
        rl = RateLimiter(limits={"a": 1, "b": 1})
        self.assertTrue(rl.allow("a"))
        self.assertFalse(rl.allow("a"))
        self.assertTrue(rl.allow("b"))


if __name__ == "__main__":
    unittest.main()
