# -*- coding: utf-8 -*-
from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass

_MAX_LOG_ENTRIES = 200
_MAX_PREVIEW_CHARS = 500


@dataclass
class LogEntry:
    capability: str
    ok: bool
    duration_ms: float
    timestamp: float
    preview: str = ""


class OperationLog:
    def __init__(self, max_entries: int = _MAX_LOG_ENTRIES) -> None:
        self._entries: deque[LogEntry] = deque(maxlen=max_entries)
        self._lock = threading.Lock()
        self._max_entries = max_entries
        self._total_requests = 0
        self._total_errors = 0

    def record(self, capability: str, ok: bool, duration_ms: float, response: dict | None = None) -> None:
        preview = ""
        if response is not None:
            raw = str(response)
            preview = raw[:_MAX_PREVIEW_CHARS] + "…" if len(raw) > _MAX_PREVIEW_CHARS else raw

        entry = LogEntry(
            capability=capability,
            ok=ok,
            duration_ms=duration_ms,
            timestamp=time.time(),
            preview=preview,
        )
        with self._lock:
            self._entries.append(entry)
            self._total_requests += 1
            if not ok:
                self._total_errors += 1

    @property
    def entries(self) -> list[LogEntry]:
        with self._lock:
            return list(self._entries)

    def recent(self, count: int = 20) -> list[LogEntry]:
        with self._lock:
            return list(list(self._entries)[-count:])

    @property
    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                "total": self._total_requests,
                "errors": self._total_errors,
            }

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._total_requests = 0
            self._total_errors = 0


operation_log = OperationLog()
