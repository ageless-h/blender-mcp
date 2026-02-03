# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass(frozen=True)
class AuditEvent:
    capability: str
    ok: bool
    error: str | None = None
    timestamp: str = datetime.now(timezone.utc).isoformat()


class AuditLogger:
    def record(self, event: AuditEvent) -> None:
        raise NotImplementedError


class MemoryAuditLogger(AuditLogger):
    def __init__(self) -> None:
        self.events: List[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self.events.append(event)
