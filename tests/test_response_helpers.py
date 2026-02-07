# -*- coding: utf-8 -*-
import unittest
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_mcp_addon.handlers.response import (
    _ok, _error, not_found_error, invalid_params_error,
    operation_failed_error, unsupported_type_error,
)


class TestResponseHelpers(unittest.TestCase):
    def test_ok_response(self):
        t = time.perf_counter()
        r = _ok(result={"key": "val"}, started=t)
        self.assertTrue(r["ok"])
        self.assertEqual(r["result"]["key"], "val")
        self.assertIsNone(r["error"])
        self.assertGreaterEqual(r["timing_ms"], 0)

    def test_error_response(self):
        t = time.perf_counter()
        r = _error(code="test", message="msg", started=t)
        self.assertFalse(r["ok"])
        self.assertIsNone(r["result"])
        self.assertEqual(r["error"]["code"], "test")

    def test_not_found(self):
        t = time.perf_counter()
        r = not_found_error("mesh", "Cube", t)
        self.assertFalse(r["ok"])
        self.assertIn("Cube", r["error"]["message"])

    def test_invalid_params(self):
        t = time.perf_counter()
        r = invalid_params_error("bad param", t)
        self.assertFalse(r["ok"])
        self.assertEqual(r["error"]["code"], "invalid_params")

    def test_operation_failed_truncates(self):
        t = time.perf_counter()
        long_msg = "x" * 1000
        r = operation_failed_error("op", Exception(long_msg), t)
        self.assertLessEqual(len(r["error"]["message"]), 600)

    def test_unsupported_type(self):
        t = time.perf_counter()
        r = unsupported_type_error("unknown", t)
        self.assertIn("unknown", r["error"]["message"])


if __name__ == "__main__":
    unittest.main()
