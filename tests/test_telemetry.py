# -*- coding: utf-8 -*-
"""Tests for telemetry collection."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from blender_mcp.telemetry import (
    TelemetryCollector,
    ToolMetrics,
    _is_telemetry_enabled,
    get_collector,
    telemetry_tool,
)


class TestToolMetrics(unittest.TestCase):
    def test_initial_state(self) -> None:
        m = ToolMetrics()
        self.assertEqual(m.call_count, 0)
        self.assertEqual(m.avg_ms, 0.0)

    def test_record_success(self) -> None:
        m = ToolMetrics()
        m.record(success=True, elapsed_ms=10.0)
        self.assertEqual(m.call_count, 1)
        self.assertEqual(m.success_count, 1)
        self.assertEqual(m.failure_count, 0)
        self.assertEqual(m.avg_ms, 10.0)

    def test_record_failure(self) -> None:
        m = ToolMetrics()
        m.record(success=False, elapsed_ms=5.0)
        self.assertEqual(m.failure_count, 1)
        self.assertEqual(m.success_count, 0)

    def test_min_max_avg(self) -> None:
        m = ToolMetrics()
        m.record(True, 10.0)
        m.record(True, 30.0)
        self.assertEqual(m.min_ms, 10.0)
        self.assertEqual(m.max_ms, 30.0)
        self.assertEqual(m.avg_ms, 20.0)


class TestTelemetryCollector(unittest.TestCase):
    def test_disabled_collector_ignores_records(self) -> None:
        c = TelemetryCollector(enabled=False)
        c.record("test_tool", True, 5.0)
        self.assertEqual(len(c.tools), 0)

    def test_enabled_collector_records(self) -> None:
        c = TelemetryCollector(enabled=True)
        c.record("tool_a", True, 10.0)
        c.record("tool_a", False, 20.0)
        c.record("tool_b", True, 5.0)
        self.assertEqual(len(c.tools), 2)
        self.assertEqual(c.tools["tool_a"].call_count, 2)
        self.assertEqual(c.tools["tool_b"].call_count, 1)

    def test_summary_empty(self) -> None:
        c = TelemetryCollector(enabled=True)
        s = c.summary()
        self.assertEqual(s["total_calls"], 0)

    def test_summary_with_data(self) -> None:
        c = TelemetryCollector(enabled=True)
        c.record("tool_a", True, 10.0)
        c.record("tool_a", True, 20.0)
        s = c.summary()
        self.assertEqual(s["total_calls"], 2)
        self.assertEqual(s["tools"]["tool_a"]["calls"], 2)
        self.assertEqual(s["tools"]["tool_a"]["avg_ms"], 15.0)

    def test_reset(self) -> None:
        c = TelemetryCollector(enabled=True)
        c.record("tool_a", True, 10.0)
        c.reset()
        self.assertEqual(len(c.tools), 0)


class TestTelemetryEnabled(unittest.TestCase):
    @patch.dict(os.environ, {"DISABLE_TELEMETRY": "true"}, clear=False)
    def test_disable_telemetry_overrides(self) -> None:
        self.assertFalse(_is_telemetry_enabled())

    @patch.dict(os.environ, {"MCP_TELEMETRY": "true", "DISABLE_TELEMETRY": "true"}, clear=False)
    def test_disable_overrides_enable(self) -> None:
        self.assertFalse(_is_telemetry_enabled())

    @patch.dict(os.environ, {"MCP_TELEMETRY": "true"}, clear=False)
    def test_mcp_telemetry_enables(self) -> None:
        # Remove DISABLE_TELEMETRY if present
        os.environ.pop("DISABLE_TELEMETRY", None)
        self.assertTrue(_is_telemetry_enabled())

    @patch.dict(os.environ, {}, clear=False)
    def test_default_disabled(self) -> None:
        os.environ.pop("MCP_TELEMETRY", None)
        os.environ.pop("DISABLE_TELEMETRY", None)
        self.assertFalse(_is_telemetry_enabled())


class TestTelemetryDecorator(unittest.TestCase):
    def test_decorator_records_success(self) -> None:
        collector = get_collector()
        collector.enabled = True
        collector.reset()

        class FakeServer:
            @telemetry_tool
            def tools_call(self, name: str, arguments: dict) -> dict:
                return {"content": [{"type": "text", "text": "ok"}]}

        server = FakeServer()
        result = server.tools_call("test_tool", {})
        self.assertNotIn("isError", result)
        self.assertIn("test_tool", collector.tools)
        self.assertEqual(collector.tools["test_tool"].success_count, 1)

        # Cleanup
        collector.enabled = False
        collector.reset()

    def test_decorator_records_failure(self) -> None:
        collector = get_collector()
        collector.enabled = True
        collector.reset()

        class FakeServer:
            @telemetry_tool
            def tools_call(self, name: str, arguments: dict) -> dict:
                return {"content": [], "isError": True}

        server = FakeServer()
        server.tools_call("fail_tool", {})
        self.assertEqual(collector.tools["fail_tool"].failure_count, 1)

        collector.enabled = False
        collector.reset()


if __name__ == "__main__":
    unittest.main()
