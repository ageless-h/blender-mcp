# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class CapabilityMeta:
    name: str
    description: str
    scopes: List[str] = field(default_factory=list)
    min_version: str | None = None
    max_version: str | None = None


class CapabilityCatalog:
    def __init__(self) -> None:
        self._capabilities: Dict[str, CapabilityMeta] = {}

    def register(self, capability: CapabilityMeta) -> None:
        self._capabilities[capability.name] = capability

    def list(self) -> Iterable[CapabilityMeta]:
        return list(self._capabilities.values())

    def get(self, name: str) -> CapabilityMeta | None:
        return self._capabilities.get(name)
