# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
MAX_LOG_FILES = 5
MAX_MEMORY_EVENTS = 1000
BUFFER_FLUSH_COUNT = 10


@dataclass(frozen=True)
class AuditEvent:
    capability: str
    ok: bool
    error: str | None = None
    data: Dict[str, Any] | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AuditLogger:
    def record(self, event: AuditEvent) -> None:
        raise NotImplementedError


class MemoryAuditLogger(AuditLogger):
    def __init__(self, max_events: int = MAX_MEMORY_EVENTS) -> None:
        self._events: deque[AuditEvent] = deque(maxlen=max_events)
        self._lock = threading.Lock()

    @property
    def events(self) -> list[AuditEvent]:
        with self._lock:
            return list(self._events)

    def record(self, event: AuditEvent) -> None:
        with self._lock:
            self._events.append(event)

    def export_json(self, file_path: str) -> None:
        import json

        with self._lock:
            snapshot = list(self._events)
        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(
                [event.__dict__ for event in snapshot],
                handle,
                ensure_ascii=False,
                indent=2,
            )


class JsonFileAuditLogger(AuditLogger):
    def __init__(self, file_path: str, buffer_size: int = BUFFER_FLUSH_COUNT) -> None:
        self._file_path = file_path
        self._lock = threading.Lock()
        self._buffer: list[AuditEvent] = []
        self._buffer_size = buffer_size

    def record(self, event: AuditEvent) -> None:
        with self._lock:
            self._buffer.append(event)
            if len(self._buffer) >= self._buffer_size:
                self._flush_buffer()

    def _flush_buffer(self) -> None:
        if not self._buffer:
            return
        import json

        self._rotate_if_needed()
        with open(self._file_path, "a", encoding="utf-8") as handle:
            for event in self._buffer:
                handle.write(json.dumps(event.__dict__, ensure_ascii=False))
                handle.write("\n")
        self._buffer.clear()

    def flush(self) -> None:
        with self._lock:
            self._flush_buffer()

    def _rotate_if_needed(self) -> None:
        try:
            size = os.path.getsize(self._file_path)
        except OSError:
            return

        if size < MAX_LOG_SIZE:
            return

        if os.path.exists(f"{self._file_path}.{MAX_LOG_FILES}"):
            try:
                os.remove(f"{self._file_path}.{MAX_LOG_FILES}")
            except OSError:
                pass

        for i in range(MAX_LOG_FILES - 1, 0, -1):
            old_path = f"{self._file_path}.{i}"
            new_path = f"{self._file_path}.{i + 1}"
            if os.path.exists(old_path):
                try:
                    os.rename(old_path, new_path)
                except OSError:
                    pass

        try:
            os.rename(self._file_path, f"{self._file_path}.1")
        except OSError:
            pass
