# -*- coding: utf-8 -*-
from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from time import monotonic
from typing import Deque, Dict


@dataclass
class RateLimiter:
    limits: Dict[str, int] = field(default_factory=dict)
    window_seconds: float = 60.0
    default_limit: int = 120
    events: Dict[str, Deque[float]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def allow(self, capability: str) -> bool:
        limit = self.limits.get(capability, self.default_limit)
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

    def cleanup_expired(self) -> int:
        """Remove expired events from all buckets. Returns count of removed events."""
        removed = 0
        with self._lock:
            now = monotonic()
            cutoff = now - self.window_seconds
            for capability, bucket in list(self.events.items()):
                before = len(bucket)
                while bucket and bucket[0] < cutoff:
                    bucket.popleft()
                removed += before - len(bucket)
                if not bucket:
                    del self.events[capability]
        return removed
