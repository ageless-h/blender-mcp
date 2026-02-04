# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Set


@dataclass
class Guardrails:
    max_payload_bytes: int = 65536
    max_payload_keys: int = 128
    blocked_capabilities: Set[str] = field(default_factory=set)

    def allow(self, capability: str, payload: Dict[str, Any]) -> bool:
        if capability in self.blocked_capabilities:
            return False
        payload_size = len(json.dumps(payload).encode("utf-8"))
        if payload_size > self.max_payload_bytes:
            return False
        if len(payload) > self.max_payload_keys:
            return False
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
