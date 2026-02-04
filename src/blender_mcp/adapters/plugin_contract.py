# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PluginContract:
    version: str
    entrypoints: tuple[str, ...]


def validate_contract(
    contract: PluginContract, required_entrypoints: Iterable[str]
) -> bool:
    required = set(required_entrypoints)
    return required.issubset(set(contract.entrypoints))
