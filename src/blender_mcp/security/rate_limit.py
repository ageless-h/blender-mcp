# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RateLimiter:
    limits: Dict[str, int] = field(default_factory=dict)
    counts: Dict[str, int] = field(default_factory=dict)

    def allow(self, capability: str) -> bool:
        limit = self.limits.get(capability)
        if limit is None:
            return True
        current = self.counts.get(capability, 0)
        if current >= limit:
            return False
        self.counts[capability] = current + 1
        return True
