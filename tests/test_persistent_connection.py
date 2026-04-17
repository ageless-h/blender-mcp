# -*- coding: utf-8 -*-
"""Tests for persistent connection functionality in SocketAdapter."""

from __future__ import annotations

import socket
import sys
import unittest
from unittest.mock import MagicMock, patch

from blender_mcp.adapters.socket import SocketAdapter


class TestEnsureConnected(unittest.TestCase):
    """Tests for _ensure_connected method."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.adapter = SocketAdapter(use_persistent_connection=True)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.adapter.close()

    def test_first_connection_creates_socket(self) -> None:
        """_socket=None 时调用 _connect() 创建新连接."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b""

        with patch.object(self.adapter, "_connect", return_value=mock_sock) as mock_connect:
            result = self.adapter._ensure_connected()

            mock_connect.assert_called_once()
            self.assertIs(result, mock_sock)
            self.assertIs(self.adapter._socket, mock_sock)
            self.assertTrue(self.adapter._connected)

    def test_healthy_socket_is_reused(self) -> None:
        """BlockingIOError 路径 → socket 被重用."""
        mock_sock = MagicMock()
        # First call to setblocking(False) succeeds
        # recv with MSG_PEEK raises BlockingIOError (socket is healthy, no data waiting)
        mock_sock.recv.side_effect = BlockingIOError()

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_connect") as mock_connect:
            result = self.adapter._ensure_connected()

            # _connect should NOT be called since socket is healthy
            mock_connect.assert_not_called()
            self.assertIs(result, mock_sock)
            self.assertIs(self.adapter._socket, mock_sock)

    def test_closed_socket_triggers_reconnect(self) -> None:
        """recv 返回空数据 → _close_socket + 重连."""
        old_sock = MagicMock()
        old_sock.recv.return_value = b""  # Empty data means connection closed

        new_sock = MagicMock()

        self.adapter._socket = old_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_connect", return_value=new_sock) as mock_connect:
            result = self.adapter._ensure_connected()

            # Old socket should be closed, new one created
            old_sock.close.assert_called_once()
            mock_connect.assert_called_once()
            self.assertIs(result, new_sock)
            self.assertIs(self.adapter._socket, new_sock)

    def test_socket_error_triggers_reconnect(self) -> None:
        """OSError/ConnectionError → _close_socket + 重连."""
        old_sock = MagicMock()
        old_sock.recv.side_effect = OSError("Connection reset")

        new_sock = MagicMock()

        self.adapter._socket = old_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_connect", return_value=new_sock) as mock_connect:
            result = self.adapter._ensure_connected()

            # Old socket should be closed, new one created
            old_sock.close.assert_called_once()
            mock_connect.assert_called_once()
            self.assertIs(result, new_sock)

    def test_connection_error_triggers_reconnect(self) -> None:
        """ConnectionError subclass → _close_socket + 重连."""
        old_sock = MagicMock()
        old_sock.recv.side_effect = ConnectionError("Connection broken")

        new_sock = MagicMock()

        self.adapter._socket = old_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_connect", return_value=new_sock) as mock_connect:
            result = self.adapter._ensure_connected()

            old_sock.close.assert_called_once()
            mock_connect.assert_called_once()
            self.assertIs(result, new_sock)

    def test_finally_restores_blocking_mode(self) -> None:
        """确认 setblocking(True) + settimeout 总是被调用."""
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = BlockingIOError()

        self.adapter._socket = mock_sock
        self.adapter._connected = True
        self.adapter.timeout = 42.0

        self.adapter._ensure_connected()

        # Verify that setblocking(True) and settimeout were called in finally block
        mock_sock.setblocking.assert_called_with(True)
        mock_sock.settimeout.assert_called_with(42.0)

    def test_setblocking_called_after_blockingioerror(self) -> None:
        """When BlockingIOError is raised, finally block restores blocking mode."""
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = BlockingIOError()

        self.adapter._socket = mock_sock
        self.adapter._connected = True
        self.adapter.timeout = 99.0

        self.adapter._ensure_connected()

        # setblocking(True) should be called twice:
        # 1. setblocking(False) for the check
        # 2. setblocking(True) in the finally block
        self.assertEqual(mock_sock.setblocking.call_count, 2)
        mock_sock.setblocking.assert_called_with(True)
        mock_sock.settimeout.assert_called_with(99.0)

    def test_finally_guards_none_socket(self) -> None:
        """_close_socket 后 finally 不会 AttributeError."""
        mock_sock = MagicMock()
        # recv returns empty, triggering _close_socket which sets _socket = None
        mock_sock.recv.return_value = b""

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        new_sock = MagicMock()
        with patch.object(self.adapter, "_connect", return_value=new_sock):
            # This should not raise AttributeError in the finally block
            result = self.adapter._ensure_connected()

        self.assertIs(result, new_sock)
        self.assertIs(self.adapter._socket, new_sock)

    @unittest.skipIf(sys.platform == "win32", "MSG_DONTWAIT not available on Windows")
    def test_unix_uses_msg_dontwait(self) -> None:
        """Unix systems should use MSG_DONTWAIT flag."""
        if not hasattr(socket, "MSG_DONTWAIT"):
            self.skipTest("MSG_DONTWAIT not available on this platform")

        mock_sock = MagicMock()
        mock_sock.recv.side_effect = BlockingIOError()

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        self.adapter._ensure_connected()

        # Verify recv was called with MSG_PEEK | MSG_DONTWAIT
        expected_flags = socket.MSG_PEEK | socket.MSG_DONTWAIT
        mock_sock.recv.assert_called_once_with(1, expected_flags)

    @unittest.skipIf(sys.platform != "win32", "Windows-specific test")
    def test_windows_no_msg_dontwait(self) -> None:
        """Windows 上不使用 MSG_DONTWAIT."""
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = BlockingIOError()

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        self.adapter._ensure_connected()

        # On Windows, only MSG_PEEK should be used (MSG_DONTWAIT doesn't exist)
        expected_flags = socket.MSG_PEEK
        mock_sock.recv.assert_called_once_with(1, expected_flags)


class TestExecutePersistent(unittest.TestCase):
    """Tests for _execute_persistent method."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.adapter = SocketAdapter(use_persistent_connection=True)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.adapter.close()

    def test_normal_request_response(self) -> None:
        """正常流程：连接 → 发送 → 接收."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b'{"ok": true, "result": {"data": "test"}}\n'

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            result = self.adapter._execute_persistent("blender.get_scene", {})

            self.assertTrue(result.ok)
            self.assertEqual(result.result, {"data": "test"})
            # Verify sendall was called with proper format
            sent_data = mock_sock.sendall.call_args[0][0]
            self.assertIn(b'"capability": "blender.get_scene"', sent_data)

    def test_connection_reuse_across_calls(self) -> None:
        """两次 execute → 只调用 _connect 一次."""
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            BlockingIOError(),  # First _ensure_connected health check
            b'{"ok": true, "result": {"count": 1}}\n',  # First _recv_response
            BlockingIOError(),  # Second _ensure_connected health check
            b'{"ok": true, "result": {"count": 2}}\n',  # Second _recv_response
        ]

        # Pre-set the socket to simulate an existing connection
        self.adapter._socket = mock_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_connect", return_value=mock_sock) as mock_connect:
            result1 = self.adapter._execute_persistent("blender.get_scene", {})
            result2 = self.adapter._execute_persistent("blender.get_objects", {})

            # _connect should NOT be called since we started with a valid socket
            mock_connect.assert_not_called()
            self.assertTrue(result1.ok)
            self.assertTrue(result2.ok)
            self.assertEqual(result1.result, {"count": 1})
            self.assertEqual(result2.result, {"count": 2})

    def test_socket_timeout_closes_connection(self) -> None:
        """Socket timeout should close the connection."""
        mock_sock = MagicMock()
        mock_sock.sendall.side_effect = socket.timeout("Timed out")

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            result = self.adapter._execute_persistent("blender.get_scene", {})

            self.assertFalse(result.ok)
            self.assertEqual(result.error, "adapter_timeout")
            self.assertIsNone(self.adapter._socket)
            self.assertFalse(self.adapter._connected)

    def test_connection_error_closes_connection(self) -> None:
        """Connection error should close the connection."""
        mock_sock = MagicMock()
        mock_sock.sendall.side_effect = ConnectionRefusedError("Connection refused")

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            result = self.adapter._execute_persistent("blender.get_scene", {})

            self.assertFalse(result.ok)
            self.assertEqual(result.error, "adapter_unavailable")
            self.assertIsNone(self.adapter._socket)
            self.assertFalse(self.adapter._connected)

    def test_os_error_closes_connection(self) -> None:
        """OSError should close the connection."""
        mock_sock = MagicMock()
        mock_sock.sendall.side_effect = OSError("Network error")

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            result = self.adapter._execute_persistent("blender.get_scene", {})

            self.assertFalse(result.ok)
            self.assertEqual(result.error, "adapter_unavailable")
            self.assertIsNone(self.adapter._socket)

    def test_error_response_in_result(self) -> None:
        """Error response from Blender should be parsed correctly."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = (
            b'{"ok": false, "error": {"code": "object_not_found", "message": "Object not found"}}\n'
        )

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            result = self.adapter._execute_persistent("blender.modify_object", {"name": "NonExistent"})

            self.assertFalse(result.ok)
            self.assertEqual(result.error, "object_not_found")
            self.assertEqual(result.error_message, "Object not found")

    def test_empty_response_returns_error(self) -> None:
        """Empty response should return adapter_empty_response error."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b"\n"

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            result = self.adapter._execute_persistent("blender.get_scene", {})

            self.assertFalse(result.ok)
            self.assertEqual(result.error, "adapter_empty_response")

    def test_invalid_json_returns_error(self) -> None:
        """Invalid JSON response should return adapter_invalid_response error."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b"not valid json\n"

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            result = self.adapter._execute_persistent("blender.get_scene", {})

            self.assertFalse(result.ok)
            self.assertEqual(result.error, "adapter_invalid_response")

    def test_payload_encoded_as_utf8(self) -> None:
        """Payload with unicode characters should be encoded correctly."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b'{"ok": true, "result": {}}\n'

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            self.adapter._execute_persistent("blender.modify_object", {"name": "中文对象"})

            sent_data = mock_sock.sendall.call_args[0][0]
            # Verify UTF-8 encoding
            self.assertIn("中文对象".encode("utf-8"), sent_data)


class TestCloseSocket(unittest.TestCase):
    """Tests for _close_socket method."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.adapter = SocketAdapter(use_persistent_connection=True)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.adapter.close()

    def test_close_sets_none(self) -> None:
        """close 后 _socket=None, _connected=False."""
        mock_sock = MagicMock()

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        self.adapter._close_socket()

        self.assertIsNone(self.adapter._socket)
        self.assertFalse(self.adapter._connected)
        mock_sock.close.assert_called_once()

    def test_close_handles_oserror(self) -> None:
        """socket.close() 抛 OSError 不传播."""
        mock_sock = MagicMock()
        mock_sock.close.side_effect = OSError("Close error")

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        # Should not raise
        self.adapter._close_socket()

        self.assertIsNone(self.adapter._socket)
        self.assertFalse(self.adapter._connected)

    def test_close_handles_runtime_error(self) -> None:
        """socket.close() 抛 RuntimeError 不传播."""
        mock_sock = MagicMock()
        mock_sock.close.side_effect = RuntimeError("Runtime error during close")

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        # Should not raise
        self.adapter._close_socket()

        self.assertIsNone(self.adapter._socket)
        self.assertFalse(self.adapter._connected)

    def test_close_when_already_none(self) -> None:
        """_socket=None 时 close 是 no-op."""
        self.adapter._socket = None
        self.adapter._connected = False

        # Should not raise
        self.adapter._close_socket()

        self.assertIsNone(self.adapter._socket)
        self.assertFalse(self.adapter._connected)

    def test_public_close_uses_lock(self) -> None:
        """Public close() method should use the lock."""
        mock_sock = MagicMock()

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        self.adapter.close()

        self.assertIsNone(self.adapter._socket)
        self.assertFalse(self.adapter._connected)

    def test_close_is_idempotent(self) -> None:
        """Calling close multiple times should be safe."""
        mock_sock = MagicMock()

        self.adapter._socket = mock_sock
        self.adapter._connected = True

        self.adapter.close()
        self.adapter.close()  # Second call
        self.adapter.close()  # Third call

        # Should only close once
        mock_sock.close.assert_called_once()
        self.assertIsNone(self.adapter._socket)


class TestPersistentConnectionIntegration(unittest.TestCase):
    """Integration tests for persistent connection behavior."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.adapter = SocketAdapter(use_persistent_connection=True, max_retries=1)

    def tearDown(self) -> None:
        """Clean up after tests."""
        self.adapter.close()

    def test_execute_persistent_flag_uses_persistent_method(self) -> None:
        """Adapter with use_persistent_connection=True should use _execute_persistent."""
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b'{"ok": true, "result": {}}\n'

        with patch.object(self.adapter, "_ensure_connected", return_value=mock_sock):
            with patch.object(
                self.adapter, "_execute_persistent", wraps=self.adapter._execute_persistent
            ) as mock_persistent:
                with patch.object(self.adapter, "_execute_once", wraps=self.adapter._execute_once) as mock_once:
                    self.adapter.execute("blender.get_scene", {})

                    mock_persistent.assert_called_once()
                    mock_once.assert_not_called()

    def test_execute_non_persistent_uses_once_method(self) -> None:
        """Adapter with use_persistent_connection=False should use _execute_once."""
        adapter = SocketAdapter(use_persistent_connection=False, max_retries=1)

        with patch.object(adapter, "_execute_once", wraps=adapter._execute_once) as mock_once:
            with patch.object(adapter, "_execute_persistent", wraps=adapter._execute_persistent) as mock_persistent:
                # This will fail to connect but that's fine for this test
                adapter.execute("blender.get_scene", {})

                mock_once.assert_called()
                mock_persistent.assert_not_called()

    def test_reconnect_after_error_in_ensure_connected(self) -> None:
        """After error in _ensure_connected, next call should try to reconnect."""
        old_sock = MagicMock()
        old_sock.recv.side_effect = OSError("Connection lost")

        new_sock = MagicMock()
        new_sock.recv.return_value = b'{"ok": true, "result": {"reconnected": true}}\n'

        self.adapter._socket = old_sock
        self.adapter._connected = True

        with patch.object(self.adapter, "_connect", return_value=new_sock):
            result = self.adapter.execute("blender.get_scene", {})

            self.assertTrue(result.ok)
            self.assertEqual(result.result, {"reconnected": True})
            # Old socket should be closed, new one connected
            old_sock.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
