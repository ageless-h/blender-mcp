# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Set

from blender_mcp.security.audit import AuditEvent, AuditLogger


@dataclass
class Allowlist:
    allowed: Set[str] = field(default_factory=set)
    audit_logger: AuditLogger | None = None

    def is_allowed(self, capability: str) -> bool:
        return capability in self.allowed

    def replace(self, capabilities: Iterable[str]) -> None:
        previous = self.allowed
        self.allowed = set(capabilities)
        added = sorted(self.allowed - previous)
        removed = sorted(previous - self.allowed)
        if self.audit_logger is not None:
            self.audit_logger.record(
                AuditEvent(
                    capability="allowlist.update",
                    ok=True,
                    data={
                        "count": len(self.allowed),
                        "added": added,
                        "removed": removed,
                    },
                )
            )
