# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol, runtime_checkable

from blender_mcp.adapters.plugin_contract import PluginContract
from blender_mcp.adapters.types import AdapterResult


class BlenderAdapterBase(ABC):
    @abstractmethod
    def contract(self) -> PluginContract:
        raise NotImplementedError

    @abstractmethod
    def invoke(self, capability: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


@runtime_checkable
class BlenderAdapter(Protocol):
    """Protocol for adapters that execute capabilities in Blender."""

    def execute(self, capability: str, payload: Dict[str, Any]) -> AdapterResult:
        """Execute a capability and return the result."""
        ...
