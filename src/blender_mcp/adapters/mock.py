# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable, Dict

from blender_mcp.adapters.types import AdapterResult


class MockAdapter:
    """Mock adapter for testing without requiring Blender."""

    def __init__(self) -> None:
        self._responses: Dict[str, AdapterResult] = {}

    def set_response(self, capability: str, response: AdapterResult) -> None:
        """Configure a response for a specific capability."""
        self._responses[capability] = response

    def execute(
        self,
        capability: str,
        payload: Dict[str, Any],
        progress_callback: Callable[[float, float | None, str | None], None] | None = None,
    ) -> AdapterResult:
        """Execute a capability and return the configured or default response."""
        if capability in self._responses:
            return self._responses[capability]
        return AdapterResult(ok=True, result={})
