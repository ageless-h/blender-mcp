# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Set


@dataclass
class Allowlist:
    allowed: Set[str] = field(default_factory=set)

    def is_allowed(self, capability: str) -> bool:
        return capability in self.allowed

    def replace(self, capabilities: Iterable[str]) -> None:
        self.allowed = set(capabilities)
