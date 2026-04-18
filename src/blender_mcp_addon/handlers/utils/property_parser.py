# -*- coding: utf-8 -*-
"""Coerce values from JSON/MCP requests into the types Blender expects.

When AI sends a value through MCP it arrives as a JSON primitive — string,
number, boolean, or array.  Blender properties (vectors, colours, enums,
etc.) often need conversion.  This module centralises that logic.
"""

from __future__ import annotations

import re
from typing import Any


def coerce_value(value: Any, target: Any = None) -> Any:
    """Coerce *value* to match the type of *target*.

    *target* is an existing Blender property value (read before writing).
    If *target* is ``None`` or unrecognised, the value is returned as-is
    after basic string parsing.

    Supported conversions:
      - list/tuple → Vector / Color / Euler / tuple depending on length
      - str "Vector3(x,y,z)" → tuple
      - str "#rrggbb" / "#rrggbbaa" → Color-compatible tuple
      - str "Color(r,g,b,a)" → tuple
      - str "true"/"false"/"yes"/"no" → bool
      - numeric strings → float / int
      - str → NodeTree reference (by name lookup in bpy.data.node_groups)
    """
    if value is None:
        return None

    if isinstance(value, str):
        value = _parse_string(value)
        if not isinstance(value, str):
            return value

    # Handle NodeTree references — resolve string names to bpy.data.node_groups objects.
    # Must come before the None check so that non-None NodeTree targets are handled.
    if _is_node_tree_target(target):
        return _to_node_tree(value, target)

    if target is None:
        return value

    target_type = type(target).__name__

    if target_type == "Color" or _is_color_target(target):
        return _to_color(value)

    if target_type in ("Vector", "Euler") or _is_vector_target(target):
        return _to_vector(value)

    if isinstance(target, bool):
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value)

    if isinstance(target, float):
        return float(value)

    if isinstance(target, int) and not isinstance(target, bool):
        return int(value)

    if isinstance(target, (list, tuple)):
        if isinstance(value, (list, tuple)):
            return type(target)(value)
        return value

    return value


def _parse_string(s: str) -> Any:
    stripped = s.strip()

    low = stripped.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False

    if stripped.startswith("#"):
        return _parse_hex_color(stripped)

    if stripped.startswith("Vector2(") or stripped.startswith("vector2("):
        inner = stripped[stripped.index("(") + 1 :].rstrip(")")
        nums = _extract_numbers(inner)
        if len(nums) == 2:
            return tuple(nums)

    if stripped.startswith("Vector3(") or stripped.startswith("vector3("):
        inner = stripped[stripped.index("(") + 1 :].rstrip(")")
        nums = _extract_numbers(inner)
        if len(nums) == 3:
            return tuple(nums)

    if stripped.startswith("Vector(") or stripped.startswith("vector("):
        inner = stripped[stripped.index("(") + 1 :].rstrip(")")
        nums = _extract_numbers(inner)
        if len(nums) >= 2:
            return tuple(nums[:3])

    if stripped.startswith("Color(") or stripped.startswith("color("):
        inner = stripped[stripped.index("(") + 1 :].rstrip(")")
        nums = _extract_numbers(inner)
        if len(nums) >= 3:
            return tuple(nums[:4]) if len(nums) >= 4 else tuple(nums[:3]) + (1.0,)

    if stripped.startswith("Euler(") or stripped.startswith("euler("):
        inner = stripped[stripped.index("(") + 1 :].rstrip(")")
        nums = _extract_numbers(inner)
        if len(nums) == 3:
            return tuple(nums)

    try:
        if "." in stripped or "e" in stripped.lower():
            return float(stripped)
        return int(stripped)
    except ValueError:
        return s


def _parse_hex_color(s: str) -> tuple[float, ...]:
    hex_str = s.lstrip("#")
    if len(hex_str) == 6:
        r, g, b = (int(hex_str[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        return (r, g, b, 1.0)
    if len(hex_str) == 8:
        r, g, b, a = (int(hex_str[i : i + 2], 16) / 255.0 for i in (0, 2, 4, 6))
        return (r, g, b, a)
    return s


_NUM_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _extract_numbers(s: str) -> list[float]:
    return [float(m) for m in _NUM_RE.findall(s)]


def _is_color_target(target: Any) -> bool:
    tname = type(target).__name__
    if tname == "Color":
        return True
    if isinstance(target, (list, tuple)) and len(target) in (3, 4):
        return all(isinstance(v, float) and 0.0 <= v <= 1.0 for v in target)
    return False


def _is_vector_target(target: Any) -> bool:
    tname = type(target).__name__
    return tname in ("Vector", "Euler")


def _is_node_tree_target(target: Any) -> bool:
    """Check if target is a NodeTree type."""
    if target is None:
        return False
    tname = type(target).__name__
    return tname in ("NodeTree", "ShaderNodeTree", "CompositorNodeTree", "GeometryNodeTree")


def _to_node_tree(value: Any, target: Any) -> Any:
    """Convert string value to NodeTree reference by name lookup."""
    if not isinstance(value, str):
        return value
    try:
        import bpy
        tree = bpy.data.node_groups.get(value)
        if tree is not None:
            return tree
    except ImportError:
        pass
    return value


def _to_color(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        vals = list(value)
        while len(vals) < 4:
            vals.append(1.0)
        return tuple(vals[:4])
    return value


def _to_vector(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return value
