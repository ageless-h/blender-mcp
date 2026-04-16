# -*- coding: utf-8 -*-
"""Concurrency tests for thread-safe components."""

from __future__ import annotations

import threading
import time
import unittest

from blender_mcp.security.rate_limit import RateLimiter


class TestRateLimiterConcurrency(unittest.TestCase):
    def test_concurrent_allows_respect_limit(self):
        rl = RateLimiter(default_limit=50, window_seconds=60.0)
        success_count = [0]
        lock = threading.Lock()

        def try_allow():
            if rl.allow("concurrent_test"):
                with lock:
                    success_count[0] += 1

        threads = [threading.Thread(target=try_allow) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(success_count[0], 50)

    def test_concurrent_different_capabilities(self):
        rl = RateLimiter(default_limit=10, window_seconds=60.0)
        results = {"a": 0, "b": 0, "c": 0}
        lock = threading.Lock()

        def try_allow(cap):
            if rl.allow(cap):
                with lock:
                    results[cap] += 1

        threads = []
        for cap in ["a", "b", "c"]:
            for _ in range(20):
                threads.append(threading.Thread(target=try_allow, args=(cap,)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(results["a"], 10)
        self.assertEqual(results["b"], 10)
        self.assertEqual(results["c"], 10)

    def test_concurrent_cleanup_during_allow(self):
        rl = RateLimiter(default_limit=100, window_seconds=0.05)
        errors = []

        def allow_worker():
            try:
                for _ in range(50):
                    rl.allow("test_cap")
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        def cleanup_worker():
            try:
                for _ in range(25):
                    rl.cleanup_expired()
                    time.sleep(0.002)
            except Exception as e:
                errors.append(e)

        threads = [
            *[threading.Thread(target=allow_worker) for _ in range(4)],
            *[threading.Thread(target=cleanup_worker) for _ in range(2)],
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)

    def test_concurrent_cleanup_multiple_buckets(self):
        rl = RateLimiter(default_limit=100, window_seconds=0.05)
        errors = []

        def allow_and_cleanup(cap):
            try:
                for _ in range(20):
                    rl.allow(cap)
                    time.sleep(0.001)
                rl.cleanup_expired()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=allow_and_cleanup, args=(f"cap_{i}",)) for i in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)


class TestRateLimiterStressTest(unittest.TestCase):
    def test_high_contention_single_capability(self):
        rl = RateLimiter(default_limit=1000, window_seconds=60.0)
        success_count = [0]
        lock = threading.Lock()

        def rapid_fire():
            for _ in range(100):
                if rl.allow("stress_test"):
                    with lock:
                        success_count[0] += 1

        threads = [threading.Thread(target=rapid_fire) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(success_count[0], 1000)

    def test_rapid_cleanup_cycles(self):
        rl = RateLimiter(window_seconds=0.01)
        errors = []

        def cleanup_only():
            try:
                for _ in range(100):
                    rl.cleanup_expired()
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=cleanup_only) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
