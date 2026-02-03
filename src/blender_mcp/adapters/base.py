# -*- coding: utf-8 -*-
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from blender_mcp.adapters.plugin_contract import PluginContract


class BlenderAdapterBase(ABC):
    @abstractmethod
    def contract(self) -> PluginContract:
        raise NotImplementedError

    @abstractmethod
    def invoke(self, capability: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
