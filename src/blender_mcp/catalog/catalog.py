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


def capability_to_dict(capability: CapabilityMeta, version: str | None = None) -> dict[str, object]:
    data: dict[str, object] = {
        "name": capability.name,
        "description": capability.description,
        "scopes": list(capability.scopes),
        "min_version": capability.min_version,
        "max_version": capability.max_version,
    }
    if version is not None:
        data["available"] = True
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
