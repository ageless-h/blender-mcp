# -*- coding: utf-8 -*-
"""Optional anonymous telemetry for Blender MCP.

Collects tool call success/failure counts and timing. No personal data is collected.
Telemetry is disabled by default and can be controlled via:
- Environment variable: DISABLE_TELEMETRY=true (disables)
- Environment variable: MCP_TELEMETRY=true (enables)

Data is stored locally in SQLite — no network transmission in this implementation.
A future version may add opt-in remote reporting.
"""

from __future__ import annotations

import functools
import logging
import os
import sqlite3
import threading
import time
import uuid
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

logger = logging.getLogger(__name__)

_DB_PATH = Path.home() / ".blender_mcp" / "telemetry.db"


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
    _session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    _seq_index: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        if self.enabled:
            self._init_db()

    def _init_db(self) -> None:
        try:
            _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(_DB_PATH) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tool_calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tool_name TEXT NOT NULL,
                        success BOOLEAN NOT NULL,
                        elapsed_ms REAL NOT NULL,
                        session_id TEXT,
                        seq_index INTEGER,
                        timestamp REAL NOT NULL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_tool_name ON tool_calls(tool_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON tool_calls(session_id)")
        except (sqlite3.Error, OSError) as exc:
            logger.warning("Failed to initialize telemetry DB: %s", exc)
            self.enabled = False

    def record(self, tool_name: str, success: bool, elapsed_ms: float) -> None:
        """Record a tool call metric."""
        if not self.enabled:
            return
        with self._lock:
            if tool_name not in self.tools:
                self.tools[tool_name] = ToolMetrics()
            self.tools[tool_name].record(success, elapsed_ms)
            seq = self._seq_index
            self._seq_index += 1
        logger.debug(
            "Telemetry: %s %s in %.1fms",
            tool_name,
            "ok" if success else "fail",
            elapsed_ms,
        )
        self._persist(tool_name, success, elapsed_ms, seq)

    def _persist(self, tool_name: str, success: bool, elapsed_ms: float, seq_index: int) -> None:
        try:
            with sqlite3.connect(_DB_PATH) as conn:
                conn.execute(
                    """
                    INSERT INTO tool_calls (tool_name, success, elapsed_ms, session_id, seq_index, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (tool_name, success, elapsed_ms, self._session_id, seq_index, time.time()),
                )
        except sqlite3.Error as exc:
            logger.warning("Failed to persist telemetry: %s", exc)

    def summary(self) -> Dict[str, Any]:
        """Return a summary of all collected metrics from memory."""
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

    def summary_from_db(self) -> Dict[str, Any]:
        """Return a summary from persisted SQLite data."""
        if not _DB_PATH.exists():
            return {"total_calls": 0, "tools": {}}
        try:
            with sqlite3.connect(_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT tool_name,
                           COUNT(*) as calls,
                           SUM(CASE WHEN success THEN 1 ELSE 0 END) as success,
                           SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as failures,
                           AVG(elapsed_ms) as avg_ms,
                           MIN(elapsed_ms) as min_ms,
                           MAX(elapsed_ms) as max_ms
                    FROM tool_calls
                    GROUP BY tool_name
                    ORDER BY calls DESC
                    """
                ).fetchall()
                total = sum(r["calls"] for r in rows)
                return {
                    "total_calls": total,
                    "tools": {
                        r["tool_name"]: {
                            "calls": r["calls"],
                            "success": r["success"],
                            "failures": r["failures"],
                            "avg_ms": round(r["avg_ms"], 1) if r["avg_ms"] else 0,
                            "min_ms": round(r["min_ms"], 1) if r["min_ms"] else 0,
                            "max_ms": round(r["max_ms"], 1) if r["max_ms"] else 0,
                        }
                        for r in rows
                    },
                }
        except sqlite3.Error as exc:
            logger.warning("Failed to read telemetry DB: %s", exc)
            return {"total_calls": 0, "tools": {}}

    def frequent_sequences(
        self, min_length: int = 2, max_length: int = 5, min_count: int = 3
    ) -> List[Tuple[Tuple[str, ...], int]]:
        """Find frequent tool call sequences from persisted data."""
        if not _DB_PATH.exists():
            return []
        try:
            with sqlite3.connect(_DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT session_id, seq_index, tool_name
                    FROM tool_calls
                    ORDER BY session_id, seq_index
                    """
                ).fetchall()

            sessions: Dict[str, List[str]] = {}
            for row in rows:
                sid = row["session_id"]
                if sid not in sessions:
                    sessions[sid] = []
                sessions[sid].append(row["tool_name"])

            ngram_counts: Counter = Counter()
            for session_tools in sessions.values():
                for n in range(min_length, max_length + 1):
                    for i in range(len(session_tools) - n + 1):
                        ngram = tuple(session_tools[i : i + n])
                        ngram_counts[ngram] += 1

            return [(seq, count) for seq, count in ngram_counts.most_common(20) if count >= min_count]
        except sqlite3.Error as exc:
            logger.warning("Failed to analyze sequences: %s", exc)
            return []

    def recommend_next_tool(self, recent_tools: List[str], top_n: int = 3) -> List[Tuple[str, int]]:
        """Recommend next tool based on historical sequences."""
        if len(recent_tools) < 1 or not _DB_PATH.exists():
            return []
        try:
            sequences = self.frequent_sequences(min_length=2, max_length=5, min_count=2)
            candidates: Counter = Counter()
            for seq, count in sequences:
                for i in range(len(seq) - 1):
                    if seq[i] == recent_tools[-1]:
                        candidates[seq[i + 1]] += count
                    if len(recent_tools) >= 2 and i < len(seq) - 2:
                        if seq[i] == recent_tools[-2] and seq[i + 1] == recent_tools[-1]:
                            candidates[seq[i + 2]] += count * 2
            return candidates.most_common(top_n)
        except Exception as exc:
            logger.warning("Failed to recommend: %s", exc)
            return []

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
