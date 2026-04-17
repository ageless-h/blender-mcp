# -*- coding: utf-8 -*-
"""Tests for adapter implementations."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from blender_mcp.adapters.mock import MockAdapter
from blender_mcp.adapters.socket import _FRIENDLY_ERRORS, SocketAdapter, _friendly_error
from blender_mcp.adapters.types import AdapterResult


class TestAdapterResult(unittest.TestCase):
    def test_successful_result(self) -> None:
        result = AdapterResult(ok=True, result={"data": "test"})
        self.assertTrue(result.ok)
        self.assertEqual(result.result, {"data": "test"})
        self.assertIsNone(result.error)
        self.assertIsNone(result.timing_ms)

    def test_failed_result(self) -> None:
        result = AdapterResult(ok=False, error="test_error", timing_ms=10.5)
        self.assertFalse(result.ok)
        self.assertIsNone(result.result)
        self.assertEqual(result.error, "test_error")
        self.assertEqual(result.timing_ms, 10.5)


class TestMockAdapter(unittest.TestCase):
    def test_default_behavior_returns_empty_result(self) -> None:
        adapter = MockAdapter()
        result = adapter.execute("unknown.capability", {})
        self.assertTrue(result.ok)
        self.assertEqual(result.result, {})
        self.assertIsNone(result.error)

    def test_configured_response_returned(self) -> None:
        adapter = MockAdapter()
        expected = AdapterResult(ok=True, result={"scene_name": "Test"})
        adapter.set_response("blender.get_scene", expected)

        result = adapter.execute("blender.get_scene", {})
        self.assertEqual(result, expected)

    def test_configured_error_response(self) -> None:
        adapter = MockAdapter()
        expected = AdapterResult(ok=False, error="test_error")
        adapter.set_response("blender.get_scene", expected)

        result = adapter.execute("blender.get_scene", {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "test_error")

    def test_different_capabilities_independent(self) -> None:
        adapter = MockAdapter()
        adapter.set_response("blender.get_scene", AdapterResult(ok=True, result={"a": 1}))
        adapter.set_response("blender.modify_object", AdapterResult(ok=True, result={"b": 2}))

        self.assertEqual(adapter.execute("blender.get_scene", {}).result, {"a": 1})
        self.assertEqual(adapter.execute("blender.modify_object", {}).result, {"b": 2})


class TestSocketAdapter(unittest.TestCase):
    def test_default_configuration(self) -> None:
        adapter = SocketAdapter()
        self.assertEqual(adapter.host, "127.0.0.1")
        self.assertEqual(adapter.port, 9876)
        self.assertEqual(adapter.timeout, 300.0)

    def test_custom_configuration(self) -> None:
        adapter = SocketAdapter(host="localhost", port=8080, timeout=10.0)
        self.assertEqual(adapter.host, "localhost")
        self.assertEqual(adapter.port, 8080)
        self.assertEqual(adapter.timeout, 10.0)

    def test_connection_refused_returns_friendly_error(self) -> None:
        adapter = SocketAdapter(host="127.0.0.1", port=59999, max_retries=1)
        result = adapter.execute("blender.get_scene", {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error, _FRIENDLY_ERRORS["adapter_unavailable"])
        self.assertIsNotNone(result.timing_ms)

    @patch("blender_mcp.adapters.socket.socket.socket")
    def test_timeout_returns_friendly_error(self, mock_socket_class: MagicMock) -> None:
        import socket

        mock_sock = MagicMock()
        mock_sock.connect.side_effect = socket.timeout("timed out")
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

        adapter = SocketAdapter(max_retries=1, use_persistent_connection=False)
        result = adapter.execute("blender.get_scene", {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error, _FRIENDLY_ERRORS["adapter_timeout"])

    def test_retry_params_stored(self) -> None:
        adapter = SocketAdapter(max_retries=5, retry_base_delay=2.0)
        self.assertEqual(adapter.max_retries, 5)
        self.assertEqual(adapter.retry_base_delay, 2.0)


class TestSocketAdapterRetry(unittest.TestCase):
    """Tests for retry and reconnect logic."""

    @patch.object(SocketAdapter, "_execute_once")
    def test_retry_on_unavailable(self, mock_exec: MagicMock) -> None:
        fail = AdapterResult(ok=False, error="adapter_unavailable", timing_ms=1.0)
        success = AdapterResult(ok=True, result={"ok": True}, timing_ms=2.0)
        mock_exec.side_effect = [fail, success]

        adapter = SocketAdapter(max_retries=3, retry_base_delay=0.01, use_persistent_connection=False)
        result = adapter.execute("blender.get_scene", {})
        self.assertTrue(result.ok)
        self.assertEqual(mock_exec.call_count, 2)

    @patch.object(SocketAdapter, "_execute_once")
    def test_retry_on_timeout(self, mock_exec: MagicMock) -> None:
        fail = AdapterResult(ok=False, error="adapter_timeout", timing_ms=1.0)
        success = AdapterResult(ok=True, result={"ok": True}, timing_ms=2.0)
        mock_exec.side_effect = [fail, fail, success]

        adapter = SocketAdapter(max_retries=3, retry_base_delay=0.01, use_persistent_connection=False)
        result = adapter.execute("blender.get_scene", {})
        self.assertTrue(result.ok)
        self.assertEqual(mock_exec.call_count, 3)

    @patch.object(SocketAdapter, "_execute_once")
    def test_no_retry_on_non_retryable_error(self, mock_exec: MagicMock) -> None:
        fail = AdapterResult(ok=False, error="adapter_invalid_response", timing_ms=1.0)
        mock_exec.return_value = fail

        adapter = SocketAdapter(max_retries=3, retry_base_delay=0.01, use_persistent_connection=False)
        result = adapter.execute("blender.get_scene", {})
        self.assertFalse(result.ok)
        self.assertEqual(mock_exec.call_count, 1)

    @patch.object(SocketAdapter, "_execute_once")
    def test_all_retries_exhausted_returns_friendly_error(self, mock_exec: MagicMock) -> None:
        fail = AdapterResult(ok=False, error="adapter_unavailable", timing_ms=1.0)
        mock_exec.return_value = fail

        adapter = SocketAdapter(max_retries=3, retry_base_delay=0.01, use_persistent_connection=False)
        result = adapter.execute("blender.get_scene", {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error, _FRIENDLY_ERRORS["adapter_unavailable"])
        self.assertEqual(mock_exec.call_count, 3)

    @patch.object(SocketAdapter, "_execute_once")
    def test_success_on_first_try_no_retry(self, mock_exec: MagicMock) -> None:
        success = AdapterResult(ok=True, result={"data": 1}, timing_ms=5.0)
        mock_exec.return_value = success

        adapter = SocketAdapter(max_retries=3, retry_base_delay=0.01, use_persistent_connection=False)
        result = adapter.execute("blender.get_scene", {})
        self.assertTrue(result.ok)
        self.assertEqual(mock_exec.call_count, 1)


class TestFriendlyErrors(unittest.TestCase):
    def test_known_error_codes_have_friendly_messages(self) -> None:
        for code in ["adapter_timeout", "adapter_unavailable", "adapter_empty_response", "adapter_invalid_response"]:
            msg = _friendly_error(code)
            self.assertNotEqual(msg, code, f"Error code '{code}' should have a friendly message")
            self.assertGreater(len(msg), 20)

    def test_unknown_error_code_returns_as_is(self) -> None:
        self.assertEqual(_friendly_error("some_unknown_code"), "some_unknown_code")


if __name__ == "__main__":
    unittest.main()
