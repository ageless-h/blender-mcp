# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, Protocol, runtime_checkable

from blender_mcp.adapters.types import AdapterResult


@runtime_checkable
class BlenderAdapter(Protocol):
    """Protocol for adapters that execute capabilities in Blender."""

    def execute(self, capability: str, payload: Dict[str, Any]) -> AdapterResult:
        """Execute a capability and return the result."""
        ...
