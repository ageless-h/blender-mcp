# -*- coding: utf-8 -*-
"""Tests for MCP progress notification support."""

from __future__ import annotations

import os
import time
import unittest

os.environ.setdefault("MCP_ADAPTER", "mock")

from blender_mcp.mcp_protocol import MCPServer


class TestProgressNotification(unittest.TestCase):
    """Verify progress notification infrastructure."""

    def setUp(self):
        self.server = MCPServer()
        self.notifications: list[dict] = []
        self.server._notification_callback = lambda n: self.notifications.append(n)

    def test_send_progress_basic(self):
        """Send a basic progress notification."""
        self.server._active_progress_tokens["token-123"] = {"tool": "test"}
        result = self.server.send_progress("token-123", 50, 100, "Halfway done")

        self.assertTrue(result)
        self.assertEqual(len(self.notifications), 1)
        notif = self.notifications[0]
        self.assertEqual(notif["jsonrpc"], "2.0")
        self.assertEqual(notif["method"], "notifications/progress")
        self.assertEqual(notif["params"]["progressToken"], "token-123")
        self.assertEqual(notif["params"]["progress"], 50)
        self.assertEqual(notif["params"]["total"], 100)
        self.assertEqual(notif["params"]["message"], "Halfway done")

    def test_send_progress_minimal(self):
        """Send progress without optional fields."""
        self.server._active_progress_tokens["token-456"] = {"tool": "test"}
        result = self.server.send_progress("token-456", 25)

        self.assertTrue(result)
        self.assertEqual(len(self.notifications), 1)
        notif = self.notifications[0]
        self.assertEqual(notif["params"]["progressToken"], "token-456")
        self.assertEqual(notif["params"]["progress"], 25)
        self.assertNotIn("total", notif["params"])
        self.assertNotIn("message", notif["params"])

    def test_send_progress_integer_token(self):
        """Send progress with integer token."""
        self.server._active_progress_tokens[42] = {"tool": "test"}
        self.server.send_progress(42, 75, 100)

        self.assertEqual(self.notifications[0]["params"]["progressToken"], 42)

    def test_send_progress_inactive_token(self):
        """Progress notification fails for inactive token."""
        result = self.server.send_progress("inactive-token", 50)
        self.assertFalse(result)
        self.assertEqual(len(self.notifications), 0)

    def test_send_progress_rate_limited(self):
        """Progress notifications are rate-limited."""
        self.server._active_progress_tokens["rate-test"] = {"tool": "test"}
        self.server.send_progress("rate-test", 10)
        self.assertEqual(len(self.notifications), 1)

        self.server.send_progress("rate-test", 20)
        self.assertEqual(len(self.notifications), 1)

        time.sleep(0.15)
        self.server.send_progress("rate-test", 30)
        self.assertEqual(len(self.notifications), 2)

    def test_send_progress_message_truncated(self):
        """Progress message is truncated if too long."""
        self.server._active_progress_tokens["truncate-test"] = {"tool": "test"}
        long_message = "x" * 2000
        self.server.send_progress("truncate-test", 50, message=long_message)

        notif = self.notifications[0]
        self.assertLessEqual(len(notif["params"]["message"]), 1000)
        self.assertTrue(notif["params"]["message"].endswith("..."))

    def test_handle_request_with_progress_token(self):
        """Request with progressToken is tracked."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "blender_get_scene",
                "arguments": {},
                "_meta": {"progressToken": "op-789"},
            },
        }

        response = self.server.handle_request(request)

        self.assertIsNotNone(response)
        self.assertIn("result", response)
        self.assertNotIn("op-789", self.server._active_progress_tokens)

    def test_handle_cancelled_notification(self):
        """Handle notifications/cancelled for progress token."""
        self.server._active_progress_tokens["cancel-me"] = {"tool": "test"}

        self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "method": "notifications/cancelled",
                "params": {"requestId": "cancel-me"},
            }
        )

        self.assertNotIn("cancel-me", self.server._active_progress_tokens)

    def test_max_active_tokens(self):
        """Max active tokens limit is enforced."""
        for i in range(self.server._max_active_tokens):
            self.server._active_progress_tokens[f"token-{i}"] = {"tool": "test"}

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "blender_get_scene",
                "arguments": {},
                "_meta": {"progressToken": "overflow-token"},
            },
        }

        response = self.server.handle_request(request)
        self.assertIn("error", response)

    def test_initialize_response(self):
        """Initialize response includes capabilities."""
        response = self.server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {},
            }
        )

        self.assertEqual(response["result"]["protocolVersion"], "2024-11-05")
        self.assertEqual(response["result"]["serverInfo"]["name"], "blender-mcp")
        self.assertIn("tools", response["result"]["capabilities"])


if __name__ == "__main__":
    unittest.main()
