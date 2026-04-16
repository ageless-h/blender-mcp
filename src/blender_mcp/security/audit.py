# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
MAX_LOG_FILES = 5


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
    def __init__(self) -> None:
        self.events: List[AuditEvent] = []
        self._lock = threading.Lock()

    def record(self, event: AuditEvent) -> None:
        with self._lock:
            self.events.append(event)

    def export_json(self, file_path: str) -> None:
        import json

        with self._lock:
            snapshot = list(self.events)
        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(
                [event.__dict__ for event in snapshot],
                handle,
                ensure_ascii=False,
                indent=2,
            )


class JsonFileAuditLogger(AuditLogger):
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self._lock = threading.Lock()

    def record(self, event: AuditEvent) -> None:
        import json

        with self._lock:
            self._rotate_if_needed()
            with open(self._file_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(event.__dict__, ensure_ascii=False))
                handle.write("\n")

    def _rotate_if_needed(self) -> None:
        """Rotate log file if it exceeds MAX_LOG_SIZE."""
        try:
            size = os.path.getsize(self._file_path)
        except OSError:
            return

        if size < MAX_LOG_SIZE:
            return

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
