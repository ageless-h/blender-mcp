# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass(frozen=True)
class AuditEvent:
    capability: str
    ok: bool
    error: str | None = None
    data: Dict[str, Any] | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class AuditLogger:
    def record(self, event: AuditEvent) -> None:
        raise NotImplementedError


class MemoryAuditLogger(AuditLogger):
    def __init__(self) -> None:
        self.events: List[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self.events.append(event)

    def export_json(self, file_path: str) -> None:
        import json

        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(
                [event.__dict__ for event in self.events],
                handle,
                ensure_ascii=False,
                indent=2,
            )


class JsonFileAuditLogger(AuditLogger):
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path

    def record(self, event: AuditEvent) -> None:
        import json

        with open(self._file_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.__dict__, ensure_ascii=False))
            handle.write("\n")
