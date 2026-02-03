# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Set


@dataclass
class PermissionPolicy:
    capability_scopes: Dict[str, Set[str]] = field(default_factory=dict)

    def is_authorized(self, capability: str, scopes: Iterable[str]) -> bool:
        required = self.capability_scopes.get(capability, set())
        provided = set(scopes)
        return required.issubset(provided)
