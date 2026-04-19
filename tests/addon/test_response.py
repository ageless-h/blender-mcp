# -*- coding: utf-8 -*-
"""Unit tests for response helpers — _ok, _error, operation_failed_error, etc."""

from __future__ import annotations

import time
import unittest
from unittest.mock import patch


def _started() -> float:
    return time.perf_counter()


class TestOkResponse(unittest.TestCase):
    def test_basic_ok(self):
        from blender_mcp_addon.handlers.response import _ok

        result = _ok(result={"foo": "bar"}, started=_started())
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["foo"], "bar")
        self.assertNotIn("error", result)
        self.assertIn("timing_ms", result)

    def test_timing_is_positive(self):
        from blender_mcp_addon.handlers.response import _ok

        s = time.perf_counter()
        result = _ok(result={}, started=s)
        self.assertGreaterEqual(result["timing_ms"], 0)

    def test_empty_result(self):
        from blender_mcp_addon.handlers.response import _ok

        result = _ok(result={}, started=_started())
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"], {})


class TestErrorResponse(unittest.TestCase):
    def test_basic_error(self):
        from blender_mcp_addon.handlers.response import _error

        result = _error(code="test_error", message="something broke", started=_started())
        self.assertFalse(result["ok"])
        self.assertNotIn("result", result)
        self.assertEqual(result["error"]["code"], "test_error")
        self.assertEqual(result["error"]["message"], "something broke")

    def test_error_with_data(self):
        from blender_mcp_addon.handlers.response import _error

        result = _error(code="test_error", message="msg", started=_started(), data={"key": "val"})
        self.assertEqual(result["error"]["data"]["key"], "val")

    def test_error_with_suggestion(self):
        from blender_mcp_addon.handlers.response import _error

        result = _error(code="test_error", message="msg", started=_started(), suggestion="try this")
        self.assertEqual(result["error"]["suggestion"], "try this")

    def test_error_default_suggestion_lookup(self):
        from blender_mcp_addon.handlers.response import _error

        result = _error(code="bpy_unavailable", message="msg", started=_started())
        self.assertIn("suggestion", result["error"])
        self.assertIn("Blender", result["error"]["suggestion"])

    def test_error_none_data(self):
        from blender_mcp_addon.handlers.response import _error

        result = _error(code="test_error", message="msg", started=_started())
        self.assertNotIn("data", result["error"])


class TestBpyUnavailable(unittest.TestCase):
    def test_bpy_unavailable_error(self):
        from blender_mcp_addon.handlers.response import bpy_unavailable_error

        result = bpy_unavailable_error(_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "bpy_unavailable")

    @patch("blender_mcp_addon.handlers.response.check_bpy_available")
    def test_check_bpy_available_missing(self, mock_check):
        import blender_mcp_addon.handlers.response as resp

        original = resp.check_bpy_available
        try:
            resp.check_bpy_available = lambda: (False, None)
            available, mod = resp.check_bpy_available()
            self.assertFalse(available)
            self.assertIsNone(mod)
        finally:
            resp.check_bpy_available = original


class TestNotFoundError(unittest.TestCase):
    def test_not_found_error(self):
        from blender_mcp_addon.handlers.response import not_found_error

        result = not_found_error("object", "Cube", _started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "not_found")
        self.assertIn("object", result["error"]["message"])
        self.assertIn("Cube", result["error"]["message"])
        self.assertEqual(result["error"]["data"]["type"], "object")
        self.assertEqual(result["error"]["data"]["name"], "Cube")


class TestInvalidParamsError(unittest.TestCase):
    def test_basic_invalid_params(self):
        from blender_mcp_addon.handlers.response import invalid_params_error

        result = invalid_params_error("missing field", _started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "invalid_params")
        self.assertEqual(result["error"]["message"], "missing field")

    def test_invalid_params_with_data(self):
        from blender_mcp_addon.handlers.response import invalid_params_error

        result = invalid_params_error("bad", _started(), data={"field": "name"})
        self.assertEqual(result["error"]["data"]["field"], "name")


class TestOperationFailedError(unittest.TestCase):
    def test_basic_operation_failed(self):
        from blender_mcp_addon.handlers.response import operation_failed_error

        exc = RuntimeError("boom")
        result = operation_failed_error("data.read", exc, _started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "operation_failed")
        self.assertIn("data.read", result["error"]["message"])
        self.assertIn("boom", result["error"]["message"])
        self.assertEqual(result["error"]["data"]["exception_type"], "RuntimeError")

    def test_long_message_truncated(self):
        from blender_mcp_addon.handlers.response import operation_failed_error

        exc = ValueError("x" * 600)
        result = operation_failed_error("op", exc, _started())
        error_msg = result["error"]["message"]
        self.assertLess(len(error_msg), 700)

    def test_short_message_preserved(self):
        from blender_mcp_addon.handlers.response import operation_failed_error

        exc = ValueError("short error")
        result = operation_failed_error("op", exc, _started())
        self.assertIn("short error", result["error"]["message"])


class TestUnsupportedTypeError(unittest.TestCase):
    def test_unsupported_type(self):
        from blender_mcp_addon.handlers.response import unsupported_type_error

        result = unsupported_type_error("foobar", _started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "unsupported_type")
        self.assertIn("foobar", result["error"]["message"])
        self.assertEqual(result["error"]["data"]["type"], "foobar")


if __name__ == "__main__":
    unittest.main()
