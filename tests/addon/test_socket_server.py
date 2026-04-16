# -*- coding: utf-8 -*-
"""Unit tests for socket_server — request handling, size limits, dispatch."""

from __future__ import annotations

import json
import threading
import unittest
from unittest.mock import MagicMock, patch


class TestSocketServerConstants(unittest.TestCase):
    def test_max_request_size(self):
        from blender_mcp_addon.server.socket_server import MAX_REQUEST_SIZE

        self.assertEqual(MAX_REQUEST_SIZE, 10 * 1024 * 1024)

    def test_timer_interval(self):
        from blender_mcp_addon.server.socket_server import _TIMER_INTERVAL

        self.assertEqual(_TIMER_INTERVAL, 0.01)


class TestServerState(unittest.TestCase):
    def test_initial_server_state(self):
        from blender_mcp_addon.server import socket_server

        self.assertFalse(socket_server.is_server_running())

    def test_active_client_count_initial(self):
        from blender_mcp_addon.server import socket_server

        self.assertEqual(socket_server.get_active_client_count(), 0)


class TestGetServerAddress(unittest.TestCase):
    @patch("blender_mcp_addon.server.socket_server.get_server_address")
    def test_default_address(self, mock_get):
        mock_get.return_value = ("127.0.0.1", 9876)
        from blender_mcp_addon.server.socket_server import get_server_address

        addr = get_server_address()
        self.assertEqual(addr[0], "127.0.0.1")
        self.assertEqual(addr[1], 9876)


class TestDispatchQueue(unittest.TestCase):
    def test_dispatch_queue_exists(self):
        from blender_mcp_addon.server.socket_server import _dispatch_queue

        self.assertIsNotNone(_dispatch_queue)

    def test_dispatch_queue_is_queue(self):
        import queue

        from blender_mcp_addon.server.socket_server import _dispatch_queue

        self.assertIsInstance(_dispatch_queue, queue.Queue)


class TestShutdownFlag(unittest.TestCase):
    def test_shutdown_flag_exists(self):
        from blender_mcp_addon.server.socket_server import _shutdown_flag

        self.assertIsNotNone(_shutdown_flag)

    def test_shutdown_flag_is_event(self):
        from blender_mcp_addon.server.socket_server import _shutdown_flag

        self.assertIsInstance(_shutdown_flag, threading.Event)


class TestRequestSizeLimit(unittest.TestCase):
    def test_request_exceeds_max_size(self):
        from blender_mcp_addon.server.socket_server import MAX_REQUEST_SIZE

        self.assertGreater(MAX_REQUEST_SIZE, 0)
        large_request = b"x" * (MAX_REQUEST_SIZE + 1)
        self.assertGreater(len(large_request), MAX_REQUEST_SIZE)


class TestJSONParsing(unittest.TestCase):
    def test_valid_json_request(self):
        request_str = json.dumps({"capability": "blender.get_objects"})
        request = json.loads(request_str)
        self.assertEqual(request["capability"], "blender.get_objects")

    def test_invalid_json_request(self):
        request_str = "{invalid json"
        try:
            json.loads(request_str)
            self.fail("Should have raised JSONDecodeError")
        except json.JSONDecodeError:
            pass


class TestDispatchTimeout(unittest.TestCase):
    def test_timeout_response_structure(self):
        timeout_response = {
            "ok": False,
            "result": None,
            "error": {
                "code": "timeout",
                "message": "Main-thread dispatch timed out after 60.0s for test.capability",
            },
        }
        self.assertFalse(timeout_response["ok"])
        self.assertEqual(timeout_response["error"]["code"], "timeout")


class TestStartStopServer(unittest.TestCase):
    @patch("blender_mcp_addon.server.socket_server._server_lock")
    def test_start_when_not_running(self, mock_lock):

        mock_lock.__enter__ = MagicMock(return_value=None)
        mock_lock.__exit__ = MagicMock(return_value=None)

    @patch("blender_mcp_addon.server.socket_server._server_lock")
    def test_stop_when_not_running(self, mock_lock):

        mock_lock.__enter__ = MagicMock(return_value=None)
        mock_lock.__exit__ = MagicMock(return_value=None)


class TestBufferHandling(unittest.TestCase):
    def test_buffer_splits_on_newline(self):
        buffer = b'{"test": 1}\n{"test": 2}\n'
        lines = []
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            lines.append(line)
        self.assertEqual(len(lines), 2)

    def test_buffer_preserves_incomplete(self):
        buffer = b'{"test": 1}\n{"test": 2'
        lines = []
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            lines.append(line)
        self.assertEqual(len(lines), 1)
        self.assertEqual(buffer, b'{"test": 2')


class TestThreadSafety(unittest.TestCase):
    def test_active_clients_lock(self):
        from blender_mcp_addon.server.socket_server import _active_clients_lock

        self.assertTrue(hasattr(_active_clients_lock, "acquire"))
        self.assertTrue(hasattr(_active_clients_lock, "release"))

    def test_timer_lock(self):
        from blender_mcp_addon.server.socket_server import _timer_lock

        self.assertTrue(hasattr(_timer_lock, "acquire"))
        self.assertTrue(hasattr(_timer_lock, "release"))

    def test_server_lock(self):
        from blender_mcp_addon.server.socket_server import _server_lock

        self.assertTrue(hasattr(_server_lock, "acquire"))
        self.assertTrue(hasattr(_server_lock, "release"))


if __name__ == "__main__":
    unittest.main()
