# -*- coding: utf-8 -*-
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_mcp.security.rate_limit import RateLimiter


class TestRateLimiter(unittest.TestCase):
    def test_no_limit_allows(self):
        rl = RateLimiter()
        self.assertTrue(rl.allow("data.read"))

    def test_limit_enforced(self):
        rl = RateLimiter(limits={"data.read": 2}, window_seconds=60.0)
        self.assertTrue(rl.allow("data.read"))
        self.assertTrue(rl.allow("data.read"))
        self.assertFalse(rl.allow("data.read"))

    def test_different_caps_independent(self):
        rl = RateLimiter(limits={"a": 1, "b": 1})
        self.assertTrue(rl.allow("a"))
        self.assertFalse(rl.allow("a"))
        self.assertTrue(rl.allow("b"))


if __name__ == "__main__":
    unittest.main()
