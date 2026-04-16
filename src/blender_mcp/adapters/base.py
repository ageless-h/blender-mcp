# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Callable, Dict, Protocol, runtime_checkable

from blender_mcp.adapters.types import AdapterResult


@runtime_checkable
class BlenderAdapter(Protocol):
    """Protocol for adapters that execute capabilities in Blender."""

    def execute(
        self,
        capability: str,
        payload: Dict[str, Any],
        progress_callback: Callable[[float, float | None, str | None], None] | None = None,
    ) -> AdapterResult:
        """Execute a capability and return the result.

        Args:
            capability: The capability to execute
            payload: The payload for the capability
            progress_callback: Optional callback for progress updates.
                Signature: (progress, total, message) -> None
        """
        ...
