# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch, MagicMock

from blender_mcp.adapters.types import AdapterResult
from blender_mcp.adapters.base import BlenderAdapter
from blender_mcp.adapters.mock import MockAdapter
from blender_mcp.adapters.socket import SocketAdapter


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


class TestBlenderAdapterProtocol(unittest.TestCase):
    def test_mock_adapter_implements_protocol(self) -> None:
        adapter = MockAdapter()
        self.assertIsInstance(adapter, BlenderAdapter)

    def test_socket_adapter_implements_protocol(self) -> None:
        adapter = SocketAdapter()
        self.assertIsInstance(adapter, BlenderAdapter)


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
        adapter.set_response("scene.read", expected)
        
        result = adapter.execute("scene.read", {})
        self.assertEqual(result, expected)

    def test_configured_error_response(self) -> None:
        adapter = MockAdapter()
        expected = AdapterResult(ok=False, error="test_error")
        adapter.set_response("scene.read", expected)
        
        result = adapter.execute("scene.read", {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "test_error")

    def test_different_capabilities_independent(self) -> None:
        adapter = MockAdapter()
        adapter.set_response("scene.read", AdapterResult(ok=True, result={"a": 1}))
        adapter.set_response("scene.write", AdapterResult(ok=True, result={"b": 2}))
        
        self.assertEqual(adapter.execute("scene.read", {}).result, {"a": 1})
        self.assertEqual(adapter.execute("scene.write", {}).result, {"b": 2})


class TestSocketAdapter(unittest.TestCase):
    def test_default_configuration(self) -> None:
        adapter = SocketAdapter()
        self.assertEqual(adapter.host, "127.0.0.1")
        self.assertEqual(adapter.port, 9876)
        self.assertEqual(adapter.timeout, 30.0)

    def test_custom_configuration(self) -> None:
        adapter = SocketAdapter(host="localhost", port=8080, timeout=10.0)
        self.assertEqual(adapter.host, "localhost")
        self.assertEqual(adapter.port, 8080)
        self.assertEqual(adapter.timeout, 10.0)

    def test_connection_refused_returns_unavailable(self) -> None:
        adapter = SocketAdapter(host="127.0.0.1", port=59999)
        result = adapter.execute("scene.read", {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "adapter_unavailable")
        self.assertIsNotNone(result.timing_ms)

    @patch("blender_mcp.adapters.socket.socket.socket")
    def test_timeout_returns_timeout_error(self, mock_socket_class: MagicMock) -> None:
        import socket
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = socket.timeout("timed out")
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)
        
        adapter = SocketAdapter()
        result = adapter.execute("scene.read", {})
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "adapter_timeout")


if __name__ == "__main__":
    unittest.main()
