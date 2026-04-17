# -*- coding: utf-8 -*-
"""Tests for progress notification pipeline."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from blender_mcp.adapters.socket import SocketAdapter


class TestProgressTokenInRequest(unittest.TestCase):
    """Verify progress_token is included in request JSON."""

    @patch("blender_mcp.adapters.socket.socket.socket")
    def test_progress_token_included_in_persistent_request(self, mock_socket_class):
        mock_sock = MagicMock()
        mock_sock.recv.return_value = (json.dumps({"ok": True, "result": {}}) + "\n").encode()
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

        adapter = SocketAdapter(use_persistent_connection=False)
        adapter._connect = MagicMock(return_value=mock_sock)
        adapter._socket = None

        adapter.execute("blender.get_scene", {}, progress_token="tok-123")

        send_call_args = mock_sock.sendall.call_args[0][0]
        request = json.loads(send_call_args.decode().strip())
        self.assertEqual(request["progress_token"], "tok-123")

    @patch("blender_mcp.adapters.socket.socket.socket")
    def test_no_progress_token_when_not_provided(self, mock_socket_class):
        mock_sock = MagicMock()
        mock_sock.recv.return_value = (json.dumps({"ok": True, "result": {}}) + "\n").encode()
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

        adapter = SocketAdapter(use_persistent_connection=False)
        adapter._connect = MagicMock(return_value=mock_sock)
        adapter._socket = None

        adapter.execute("blender.get_scene", {})

        send_call_args = mock_sock.sendall.call_args[0][0]
        request = json.loads(send_call_args.decode().strip())
        self.assertNotIn("progress_token", request)


class TestRecvResponseHandlesProgressMessages(unittest.TestCase):
    """Verify _recv_response correctly separates progress messages from final response."""

    def test_single_progress_message_then_final_response(self):
        adapter = SocketAdapter()
        callback = MagicMock()
        adapter._progress_callback = callback

        progress_msg = json.dumps({"type": "progress", "progress": 50, "total": 100, "message": "Halfway"})
        final_msg = json.dumps({"ok": True, "result": {"status": "done"}})
        response_data = (progress_msg + "\n" + final_msg + "\n").encode()

        mock_sock = MagicMock()
        mock_sock.recv.return_value = response_data

        result = adapter._recv_response(mock_sock, 0.0)

        self.assertTrue(result.ok)
        self.assertEqual(result.result, {"status": "done"})
        callback.assert_called_once_with(50, 100, "Halfway")

    def test_multiple_progress_messages(self):
        adapter = SocketAdapter()
        callback = MagicMock()
        adapter._progress_callback = callback

        messages = [
            json.dumps({"type": "progress", "progress": 25, "total": 100, "message": "Step 1"}),
            json.dumps({"type": "progress", "progress": 50, "total": 100, "message": "Step 2"}),
            json.dumps({"type": "progress", "progress": 75, "total": 100, "message": "Step 3"}),
            json.dumps({"ok": True, "result": {"count": 3}}),
        ]
        response_data = "\n".join(messages).encode() + b"\n"

        mock_sock = MagicMock()
        mock_sock.recv.return_value = response_data

        result = adapter._recv_response(mock_sock, 0.0)

        self.assertTrue(result.ok)
        self.assertEqual(result.result, {"count": 3})
        self.assertEqual(callback.call_count, 3)

    def test_no_progress_callback_still_works(self):
        adapter = SocketAdapter()
        adapter._progress_callback = None

        progress_msg = json.dumps({"type": "progress", "progress": 50, "total": 100, "message": "Halfway"})
        final_msg = json.dumps({"ok": True, "result": {"status": "done"}})
        response_data = (progress_msg + "\n" + final_msg + "\n").encode()

        mock_sock = MagicMock()
        mock_sock.recv.return_value = response_data

        result = adapter._recv_response(mock_sock, 0.0)

        self.assertTrue(result.ok)

    def test_progress_without_type_field_is_final_response(self):
        adapter = SocketAdapter()
        callback = MagicMock()
        adapter._progress_callback = callback

        final_msg = json.dumps({"ok": True, "result": {"status": "done"}})
        response_data = (final_msg + "\n").encode()

        mock_sock = MagicMock()
        mock_sock.recv.return_value = response_data

        result = adapter._recv_response(mock_sock, 0.0)

        self.assertTrue(result.ok)
        callback.assert_not_called()


class TestProgressCallbackExceptionSafe(unittest.TestCase):
    """Verify callback exceptions don't affect final response."""

    def test_callback_exception_does_not_break_response(self):
        adapter = SocketAdapter()

        def bad_callback(progress, total, message):
            raise ValueError("Callback error!")

        adapter._progress_callback = bad_callback

        progress_msg = json.dumps({"type": "progress", "progress": 50, "total": 100, "message": "Halfway"})
        final_msg = json.dumps({"ok": True, "result": {"status": "done"}})
        response_data = (progress_msg + "\n" + final_msg + "\n").encode()

        mock_sock = MagicMock()
        mock_sock.recv.return_value = response_data

        result = adapter._recv_response(mock_sock, 0.0)

        self.assertTrue(result.ok)
        self.assertEqual(result.result, {"status": "done"})


class TestBackwardCompatibility(unittest.TestCase):
    """Verify behavior without progress_token matches old behavior."""

    @patch("blender_mcp.adapters.socket.socket.socket")
    def test_old_style_response_still_works(self, mock_socket_class):
        mock_sock = MagicMock()
        mock_sock.recv.return_value = (json.dumps({"ok": True, "result": {"version": "4.2"}}) + "\n").encode()
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

        adapter = SocketAdapter(use_persistent_connection=False)
        adapter._connect = MagicMock(return_value=mock_sock)
        adapter._socket = None

        result = adapter.execute("blender.get_scene", {})

        self.assertTrue(result.ok)
        self.assertEqual(result.result, {"version": "4.2"})

    @patch("blender_mcp.adapters.socket.socket.socket")
    def test_error_response_format_unchanged(self, mock_socket_class):
        mock_sock = MagicMock()
        error_response = {"ok": False, "error": {"code": "not_found", "message": "Object not found"}}
        mock_sock.recv.return_value = (json.dumps(error_response) + "\n").encode()
        mock_socket_class.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

        adapter = SocketAdapter(use_persistent_connection=False)
        adapter._connect = MagicMock(return_value=mock_sock)
        adapter._socket = None

        result = adapter.execute("blender.get_object", {"name": "Missing"})

        self.assertFalse(result.ok)
        self.assertEqual(result.error, "not_found")
        self.assertEqual(result.error_message, "Object not found")


if __name__ == "__main__":
    unittest.main()
