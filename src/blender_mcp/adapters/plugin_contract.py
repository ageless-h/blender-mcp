# -*- coding: utf-8 -*-
"""Plugin boundary contract definition and validation utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass
class PluginContract:
    """Describes the contract surface exposed by a Blender addon plugin.

    Attributes:
        version: Semantic version of the contract (e.g. ``"0.1.0"``).
        entrypoints: Names of callable entrypoints the plugin exposes.
    """

    version: str
    entrypoints: Sequence[str]


def validate_contract(
    contract: PluginContract,
    required_entrypoints: Sequence[str],
) -> bool:
    """Return ``True`` if *contract* satisfies all *required_entrypoints*.

    Validation rules:
    1. Every name in *required_entrypoints* must appear in
       ``contract.entrypoints``.
    2. ``contract.version`` must be a non-empty string.
    """
    if not contract.version:
        return False

    available = set(contract.entrypoints)
    return all(ep in available for ep in required_entrypoints)

