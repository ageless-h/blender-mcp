# -*- coding: utf-8 -*-
"""Optional anonymous telemetry for Blender MCP.

Collects tool call success/failure counts and timing. No personal data is collected.
Telemetry is disabled by default and can be controlled via:
- Environment variable: DISABLE_TELEMETRY=true (disables)
- Environment variable: MCP_TELEMETRY=true (enables)

Data is stored locally only — no network transmission in this implementation.
A future version may add opt-in remote reporting.
"""
from __future__ import annotations

import functools
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)


def _is_telemetry_enabled() -> bool:
    """Check if telemetry is enabled.

    Disabled by default. Enable with MCP_TELEMETRY=true.
    Always disabled if DISABLE_TELEMETRY=true is set.
    """
    if os.environ.get("DISABLE_TELEMETRY", "").lower() in ("true", "1", "yes"):
        return False
    return os.environ.get("MCP_TELEMETRY", "").lower() in ("true", "1", "yes")


@dataclass
class ToolMetrics:
    """Aggregated metrics for a single tool."""

    call_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_ms: float = 0.0
    min_ms: float = float("inf")
    max_ms: float = 0.0

    @property
    def avg_ms(self) -> float:
        return self.total_ms / self.call_count if self.call_count > 0 else 0.0

    def record(self, success: bool, elapsed_ms: float) -> None:
        self.call_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.total_ms += elapsed_ms
        self.min_ms = min(self.min_ms, elapsed_ms)
        self.max_ms = max(self.max_ms, elapsed_ms)


@dataclass
class TelemetryCollector:
    """Collects and stores anonymous tool usage metrics locally."""

    enabled: bool = field(default_factory=_is_telemetry_enabled)
    tools: Dict[str, ToolMetrics] = field(default_factory=dict)

    def record(self, tool_name: str, success: bool, elapsed_ms: float) -> None:
        """Record a tool call metric."""
        if not self.enabled:
            return
        if tool_name not in self.tools:
            self.tools[tool_name] = ToolMetrics()
        self.tools[tool_name].record(success, elapsed_ms)
        logger.debug(
            "Telemetry: %s %s in %.1fms",
            tool_name,
            "ok" if success else "fail",
            elapsed_ms,
        )

    def summary(self) -> Dict[str, Any]:
        """Return a summary of all collected metrics."""
        if not self.tools:
            return {"total_calls": 0, "tools": {}}
        total = sum(m.call_count for m in self.tools.values())
        return {
            "total_calls": total,
            "tools": {
                name: {
                    "calls": m.call_count,
                    "success": m.success_count,
                    "failures": m.failure_count,
                    "avg_ms": round(m.avg_ms, 1),
                    "min_ms": round(m.min_ms, 1) if m.min_ms != float("inf") else 0,
                    "max_ms": round(m.max_ms, 1),
                }
                for name, m in sorted(self.tools.items())
            },
        }

    def reset(self) -> None:
        """Reset all collected metrics."""
        self.tools.clear()


# Module-level singleton
_collector = TelemetryCollector()


def get_collector() -> TelemetryCollector:
    """Return the global telemetry collector."""
    return _collector


def telemetry_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that records tool call metrics to telemetry.

    Expects the decorated function to accept (self, name, arguments)
    and return a dict with optional "isError" key.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Extract tool name: args[1] for method(self, name, arguments)
        tool_name = args[1] if len(args) > 1 else kwargs.get("name", "unknown")
        started = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        is_error = result.get("isError", False) if isinstance(result, dict) else False
        _collector.record(str(tool_name), success=not is_error, elapsed_ms=elapsed_ms)
        return result

    return wrapper
