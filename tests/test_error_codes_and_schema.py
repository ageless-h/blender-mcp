# -*- coding: utf-8 -*-
"""Tests for error codes and response schema."""
from __future__ import annotations

import time
import unittest

from blender_mcp_addon.handlers.error_codes import ErrorCode
from blender_mcp_addon.handlers.response_schema import (
    validate_response, ResponseValidationError,
    is_ok, is_error, get_error_code,
)
from blender_mcp_addon.handlers.response import _ok, _error


class TestErrorCodes(unittest.TestCase):

    def test_count(self):
        self.assertEqual(len(ErrorCode), 15)

    def test_all_snake_case(self):
        for c in ErrorCode:
            self.assertRegex(c.value, r"^[a-z_]+$")

    def test_no_duplicates(self):
        vals = [c.value for c in ErrorCode]
        self.assertEqual(len(vals), len(set(vals)))

    def test_lookup(self):
        self.assertEqual(ErrorCode("not_found"), ErrorCode.NOT_FOUND)

    def test_in_error_helper(self):
        t = time.perf_counter()
        r = _error(code=ErrorCode.NOT_FOUND, message="x", started=t)
        self.assertEqual(r["error"]["code"], "not_found")


class TestResponseSchema(unittest.TestCase):

    def _ok(self):
        return _ok(result={"k": "v"}, started=time.perf_counter())

    def _err(self):
        return _error(code="t", message="m", started=time.perf_counter())

    def test_valid_ok(self):
        validate_response(self._ok())

    def test_valid_error(self):
        validate_response(self._err())

    def test_rejects_non_dict(self):
        with self.assertRaises(ResponseValidationError):
            validate_response("bad")

    def test_rejects_missing_keys(self):
        with self.assertRaises(ResponseValidationError):
            validate_response({"ok": True})

    def test_rejects_extra_keys(self):
        r = self._ok(); r["extra"] = 1
        with self.assertRaises(ResponseValidationError):
            validate_response(r)

    def test_rejects_non_bool_ok(self):
        r = self._ok(); r["ok"] = 1
        with self.assertRaises(ResponseValidationError):
            validate_response(r)

    def test_ok_with_none_result(self):
        r = self._ok(); r["result"] = None
        with self.assertRaises(ResponseValidationError):
            validate_response(r)

    def test_err_with_non_none_result(self):
        r = self._err(); r["result"] = {"x": 1}
        with self.assertRaises(ResponseValidationError):
            validate_response(r)

    def test_is_ok_helper(self):
        self.assertTrue(is_ok(self._ok()))
        self.assertFalse(is_ok(self._err()))

    def test_is_error_helper(self):
        self.assertTrue(is_error(self._err()))
        self.assertFalse(is_error(self._ok()))

    def test_get_error_code(self):
        self.assertEqual(get_error_code(self._err()), "t")
        self.assertIsNone(get_error_code(self._ok()))


if __name__ == "__main__":
    unittest.main()
