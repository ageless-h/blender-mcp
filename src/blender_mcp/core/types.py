# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class Capability:
    name: str
    description: str
    scopes: List[str] = field(default_factory=list)
    min_version: str | None = None
    max_version: str | None = None


@dataclass(frozen=True)
class Request:
    capability: str
    payload: Dict[str, Any]
    scopes: Iterable[str] = field(default_factory=list)


@dataclass(frozen=True)
class Response:
    ok: bool
    result: Dict[str, Any] = field(default_factory=dict)
    error: str | None = None
