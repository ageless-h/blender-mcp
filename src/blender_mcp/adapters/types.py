# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AdapterResult:
    ok: bool
    result: Dict[str, Any] | None = None
    error: str | None = None
    error_message: str | None = None
    error_suggestion: str | None = None
    timing_ms: float | None = None
