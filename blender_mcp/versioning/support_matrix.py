# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SupportMatrix:
    lts_versions: List[str] = field(default_factory=list)
    latest_version: str | None = None
    deprecated_versions: List[str] = field(default_factory=list)

    def is_supported(self, version: str) -> bool:
        if version == self.latest_version:
            return True
        return version in self.lts_versions
