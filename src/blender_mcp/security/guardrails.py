# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Set


@dataclass
class Guardrails:
    max_payload_bytes: int = 65536
    max_payload_keys: int = 128
    max_nesting_depth: int = 10
    blocked_capabilities: Set[str] = field(default_factory=set)

    def allow(self, capability: str, payload: Dict[str, Any]) -> bool:
        if capability in self.blocked_capabilities:
            return False
        payload_size = self._estimate_size(payload)
        if payload_size > self.max_payload_bytes:
            return False
        if len(payload) > self.max_payload_keys:
            return False
        if not self._check_depth(payload, self.max_nesting_depth):
            return False
        return True

    @staticmethod
    def _estimate_size(obj: Any) -> int:
        """Estimate JSON size without full serialization."""
        if obj is None:
            return 4
        if isinstance(obj, bool):
            return 5
        if isinstance(obj, int):
            return len(str(obj))
        if isinstance(obj, float):
            return len(str(obj))
        if isinstance(obj, str):
            return len(obj.encode("utf-8")) + 2
        if isinstance(obj, dict):
            size = 2
            for key, value in obj.items():
                size += len(key.encode("utf-8")) + 4
                size += Guardrails._estimate_size(value)
            return size
        if isinstance(obj, (list, tuple)):
            size = 2
            for item in obj:
                size += Guardrails._estimate_size(item) + 2
            return size
        return len(str(obj))

    @staticmethod
    def _check_depth(obj: Any, max_depth: int, current: int = 0) -> bool:
        """Check that nested structure doesn't exceed max depth."""
        if current > max_depth:
            return False
        if isinstance(obj, dict):
            return all(Guardrails._check_depth(v, max_depth, current + 1) for v in obj.values())
        if isinstance(obj, (list, tuple)):
            return all(Guardrails._check_depth(v, max_depth, current + 1) for v in obj)
        return True

    @classmethod
    def from_limits(
        cls,
        max_payload_bytes: int | None = None,
        max_payload_keys: int | None = None,
        blocked_capabilities: Iterable[str] | None = None,
    ) -> "Guardrails":
        return cls(
            max_payload_bytes=65536 if max_payload_bytes is None else max_payload_bytes,
            max_payload_keys=128 if max_payload_keys is None else max_payload_keys,
            blocked_capabilities=set(blocked_capabilities or []),
        )

    @classmethod
    def from_env(cls) -> "Guardrails":
        max_payload_bytes = int(os.getenv("MCP_MAX_PAYLOAD_BYTES", "65536"))
        max_payload_keys = int(os.getenv("MCP_MAX_PAYLOAD_KEYS", "128"))
        blocked = os.getenv("MCP_BLOCKED_CAPABILITIES", "")
        blocked_caps = [cap.strip() for cap in blocked.split(",") if cap.strip()]
        return cls.from_limits(
            max_payload_bytes=max_payload_bytes,
            max_payload_keys=max_payload_keys,
            blocked_capabilities=blocked_caps,
        )
