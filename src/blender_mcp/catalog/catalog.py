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


def capability_scope_map(
    capabilities: Iterable[CapabilityMeta],
) -> dict[str, set[str]]:
    return {
        capability.name: set(capability.scopes)
        for capability in capabilities
        if capability.scopes
    }


def _parse_version(version: str) -> tuple[int, ...] | None:
    parts: list[int] = []
    for raw in version.split("."):
        digits = "".join(ch for ch in raw if ch.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    if not parts:
        return None
    return tuple(parts)


def _lt(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    width = max(len(a), len(b))
    aa = a + (0,) * (width - len(a))
    bb = b + (0,) * (width - len(b))
    return aa < bb


def capability_availability(
    capability: CapabilityMeta, version: str | None
) -> tuple[bool, str | None]:
    if version is None:
        return True, None
    target = _parse_version(version)
    if target is None:
        return True, None
    if capability.min_version is not None:
        min_v = _parse_version(capability.min_version)
        if min_v is not None and _lt(target, min_v):
            return False, "version_below_min"
    if capability.max_version is not None:
        max_v = _parse_version(capability.max_version)
        if max_v is not None and not _lt(target, max_v):
            return False, "version_at_or_above_max"
    return True, None


def capability_to_dict(capability: CapabilityMeta, version: str | None = None) -> dict[str, object]:
    available, reason = capability_availability(capability, version)
    data: dict[str, object] = {
        "name": capability.name,
        "description": capability.description,
        "scopes": list(capability.scopes),
        "min_version": capability.min_version,
        "max_version": capability.max_version,
    }
    if version is not None:
        data["available"] = available
        if not available:
            data["unavailable_reason"] = reason
    return data


def minimal_capability_set() -> list[CapabilityMeta]:
    return [
        CapabilityMeta(
            name="scene.read",
            description="Read scene",
            scopes=["scene:read"],
        ),
        CapabilityMeta(
            name="object.read",
            description="Read object",
            scopes=["object:read"],
        ),
        CapabilityMeta(
            name="scene.write",
            description="Write scene",
            scopes=["scene:write"],
        ),
    ]
