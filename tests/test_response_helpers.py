# -*- coding: utf-8 -*-
"""Tests for response helper functions."""
from __future__ import annotations

import time
import unittest

from blender_mcp_addon.handlers.response import (
    _error,
    _ok,
    invalid_params_error,
    not_found_error,
    operation_failed_error,
    unsupported_type_error,
)


class TestResponseHelpers(unittest.TestCase):
    def test_ok_response(self):
        t = time.perf_counter()
        r = _ok(result={"key": "val"}, started=t)
        self.assertTrue(r["ok"])
        self.assertEqual(r["result"]["key"], "val")
        self.assertNotIn("error", r)
        self.assertGreaterEqual(r["timing_ms"], 0)

    def test_error_response(self):
        t = time.perf_counter()
        r = _error(code="test", message="msg", started=t)
        self.assertFalse(r["ok"])
        self.assertNotIn("result", r)
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
