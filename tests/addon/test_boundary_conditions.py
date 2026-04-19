# -*- coding: utf-8 -*-
"""Boundary tests for response helpers and core utilities."""

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


def _started() -> float:
    return time.perf_counter()


class TestOkResponseBoundaries(unittest.TestCase):
    def test_ok_with_none_result(self):
        result = _ok(result=None, started=_started())
        self.assertTrue(result["ok"])
        self.assertIsNone(result["result"])

    def test_ok_with_nested_dict(self):
        nested = {"level1": {"level2": {"level3": "deep_value"}}}
        result = _ok(result=nested, started=_started())
        self.assertEqual(result["result"]["level1"]["level2"]["level3"], "deep_value")

    def test_ok_with_list_result(self):
        result = _ok(result=[1, 2, 3, 4, 5], started=_started())
        self.assertEqual(result["result"], [1, 2, 3, 4, 5])

    def test_ok_with_empty_list(self):
        result = _ok(result=[], started=_started())
        self.assertEqual(result["result"], [])

    def test_ok_timing_positive(self):
        start = time.perf_counter()
        time.sleep(0.001)
        result = _ok(result={}, started=start)
        self.assertGreater(result["timing_ms"], 0)


class TestErrorResponseBoundaries(unittest.TestCase):
    def test_error_with_empty_code(self):
        result = _error(code="", message="test", started=_started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["code"], "")

    def test_error_with_unicode_message(self):
        result = _error(code="test", message="错误信息 测试 🎨", started=_started())
        self.assertIn("错误", result["error"]["message"])

    def test_error_with_very_long_message(self):
        long_msg = "x" * 10000
        result = _error(code="test", message=long_msg, started=_started())
        self.assertEqual(len(result["error"]["message"]), 10000)

    def test_error_with_special_characters(self):
        special = "test\n\t\r\"'\\<>&"
        result = _error(code="test", message=special, started=_started())
        self.assertEqual(result["error"]["message"], special)

    def test_error_with_none_data(self):
        result = _error(code="test", message="msg", started=_started(), data=None)
        self.assertNotIn("data", result["error"])

    def test_error_with_complex_data(self):
        complex_data = {"nested": {"list": [1, 2, {"key": "value"}]}}
        result = _error(code="test", message="msg", started=_started(), data=complex_data)
        self.assertEqual(result["error"]["data"]["nested"]["list"][2]["key"], "value")


class TestNotFoundBoundaries(unittest.TestCase):
    def test_not_found_with_empty_name(self):
        result = not_found_error("object", "", _started())
        self.assertFalse(result["ok"])
        self.assertIn("object", result["error"]["message"])

    def test_not_found_with_special_name(self):
        result = not_found_error("mesh", "Cube/@#$%^&*()", _started())
        self.assertIn("Cube/@#$%^&*()", result["error"]["message"])

    def test_not_found_with_unicode_type(self):
        result = not_found_error("材质", "TestMat", _started())
        self.assertIn("材质", result["error"]["message"])


class TestInvalidParamsBoundaries(unittest.TestCase):
    def test_invalid_params_empty_message(self):
        result = invalid_params_error("", _started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["message"], "")

    def test_invalid_params_with_none_data(self):
        result = invalid_params_error("test", _started(), data=None)
        self.assertNotIn("data", result["error"])


class TestOperationFailedBoundaries(unittest.TestCase):
    def test_operation_failed_with_exception_chain(self):
        try:
            raise ValueError("inner error")
        except ValueError as e:
            try:
                raise RuntimeError("outer error") from e
            except RuntimeError as exc:
                result = operation_failed_error("test.op", exc, _started())
                self.assertFalse(result["ok"])
                self.assertIn("RuntimeError", result["error"]["data"]["exception_type"])

    def test_operation_failed_with_none_exception_message(self):
        exc = RuntimeError()
        result = operation_failed_error("op", exc, _started())
        self.assertFalse(result["ok"])

    def test_operation_failed_truncates_very_long_messages(self):
        exc = ValueError("x" * 10000)
        result = operation_failed_error("op", exc, _started())
        self.assertLess(len(result["error"]["message"]), 10000)


class TestUnsupportedTypeBoundaries(unittest.TestCase):
    def test_unsupported_type_empty(self):
        result = unsupported_type_error("", _started())
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["data"]["type"], "")

    def test_unsupported_type_with_slash(self):
        result = unsupported_type_error("invalid/type", _started())
        self.assertIn("invalid/type", result["error"]["message"])

    def test_unsupported_type_with_unicode(self):
        result = unsupported_type_error("类型", _started())
        self.assertIn("类型", result["error"]["message"])


class TestResponseTimingBoundaries(unittest.TestCase):
    def test_timing_with_zero_start(self):
        result = _ok(result={}, started=0.0)
        self.assertGreaterEqual(result["timing_ms"], 0)

    def test_timing_with_future_start(self):
        future = time.perf_counter() + 1000
        result = _ok(result={}, started=future)
        self.assertIsInstance(result["timing_ms"], int)


if __name__ == "__main__":
    unittest.main()
