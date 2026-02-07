# -*- coding: utf-8 -*-
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from time import monotonic
from typing import Deque, Dict

from collections import deque


@dataclass
class RateLimiter:
    limits: Dict[str, int] = field(default_factory=dict)
    window_seconds: float = 60.0
    events: Dict[str, Deque[float]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def allow(self, capability: str) -> bool:
        limit = self.limits.get(capability)
        if limit is None:
            return True
        with self._lock:
            now = monotonic()
            bucket = self.events.setdefault(capability, deque())
            cutoff = now - self.window_seconds
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True
