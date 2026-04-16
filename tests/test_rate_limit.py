# -*- coding: utf-8 -*-
"""Tests for rate limiter."""

from __future__ import annotations

import threading
import time
import unittest

from blender_mcp.security.rate_limit import RateLimiter


class TestRateLimiter(unittest.TestCase):
    def test_no_limit_allows(self):
        rl = RateLimiter()
        self.assertTrue(rl.allow("blender.get_object_data"))

    def test_limit_enforced(self):
        rl = RateLimiter(limits={"blender.get_object_data": 2}, window_seconds=60.0)
        self.assertTrue(rl.allow("blender.get_object_data"))
        self.assertTrue(rl.allow("blender.get_object_data"))
        self.assertFalse(rl.allow("blender.get_object_data"))

    def test_different_caps_independent(self):
        rl = RateLimiter(limits={"a": 1, "b": 1})
        self.assertTrue(rl.allow("a"))
        self.assertFalse(rl.allow("a"))
        self.assertTrue(rl.allow("b"))

    def test_default_limit_used(self):
        """Test that default_limit is used when no specific limit is set."""
        rl = RateLimiter(default_limit=3, window_seconds=60.0)
        self.assertTrue(rl.allow("unknown_capability"))
        self.assertTrue(rl.allow("unknown_capability"))
        self.assertTrue(rl.allow("unknown_capability"))
        self.assertFalse(rl.allow("unknown_capability"))

    def test_cleanup_expired_removes_old_events(self):
        """Test that cleanup_expired removes events outside the window."""
        rl = RateLimiter(window_seconds=0.1)  # 100ms window
        # Add some events
        rl.allow("test_cap")
        rl.allow("test_cap")
        # Wait for window to expire
        time.sleep(0.15)
        # Cleanup should remove expired events
        removed = rl.cleanup_expired()
        self.assertEqual(removed, 2)
        # Bucket should be empty and removed
        self.assertNotIn("test_cap", rl.events)

    def test_cleanup_expired_keeps_recent_events(self):
        """Test that cleanup_expired keeps events within the window."""
        rl = RateLimiter(window_seconds=60.0)
        rl.allow("test_cap")
        rl.allow("test_cap")
        # Cleanup immediately - nothing should be removed
        removed = rl.cleanup_expired()
        self.assertEqual(removed, 0)
        # Bucket should still exist
        self.assertIn("test_cap", rl.events)
        self.assertEqual(len(rl.events["test_cap"]), 2)

    def test_cleanup_expired_partial_removal(self):
        """Test partial bucket cleanup - only old events removed."""
        rl = RateLimiter(window_seconds=0.1)
        # Add old events
        rl.allow("test_cap")
        rl.allow("test_cap")
        # Wait for partial expiry
        time.sleep(0.08)
        # Add new events
        rl.allow("test_cap")
        # Wait for old ones to expire
        time.sleep(0.05)
        removed = rl.cleanup_expired()
        # First 2 should be removed
        self.assertEqual(removed, 2)
        # Last one should remain
        self.assertEqual(len(rl.events["test_cap"]), 1)

    def test_cleanup_multiple_buckets(self):
        """Test cleanup across multiple capability buckets."""
        rl = RateLimiter(window_seconds=0.1)
        rl.allow("cap_a")
        rl.allow("cap_b")
        rl.allow("cap_c")
        time.sleep(0.15)
        removed = rl.cleanup_expired()
        self.assertEqual(removed, 3)
        # All buckets should be removed
        self.assertEqual(len(rl.events), 0)

    def test_thread_safety_allow(self):
        """Test that allow() is thread-safe."""
        rl = RateLimiter(default_limit=100, window_seconds=60.0)
        results = []
        errors = []

        def worker():
            try:
                for _ in range(50):
                    results.append(rl.allow("concurrent_cap"))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)
        # Total successful allows should be exactly 100 (the limit)
        self.assertEqual(sum(1 for r in results if r), 100)

    def test_thread_safety_cleanup(self):
        """Test that cleanup_expired() is thread-safe."""
        rl = RateLimiter(window_seconds=0.05)
        errors = []

        def allow_worker():
            try:
                for _ in range(20):
                    rl.allow("cap")
                    time.sleep(0.005)
            except Exception as e:
                errors.append(e)

        def cleanup_worker():
            try:
                for _ in range(10):
                    rl.cleanup_expired()
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        threads = [
            *[threading.Thread(target=allow_worker) for _ in range(2)],
            *[threading.Thread(target=cleanup_worker) for _ in range(2)],
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
