# -*- coding: utf-8 -*-
"""Capability-specific timeout configuration.

Timeouts are tiered by expected operation duration:
  fast (10s)    — read-only queries, scene inspection
  standard (60s) — mutations, node edits, constraint changes
  slow (300s)   — rendering, import/export, arbitrary operator/script

The MCP server side (adapters/socket.py) has its own connection-level
timeout (default 30s) which should be higher than the addon-side timeout
for the capability being invoked.  The server adapter does not currently
read this file; the timeout is enforced on the addon dispatch side.
"""

from __future__ import annotations

# ── Timeout tiers (seconds) ──────────────────────────────────────────

FAST_TIMEOUT = 10.0
STANDARD_TIMEOUT = 60.0
SLOW_TIMEOUT = 300.0
DEFAULT_TIMEOUT = 120.0


# ── Per-capability timeout map ───────────────────────────────────────

_CAPABILITY_TIMEOUTS: dict[str, float] = {
    # Perception layer — fast read-only queries
    "blender.get_objects": FAST_TIMEOUT,
    "blender.get_object_data": FAST_TIMEOUT,
    "blender.get_node_tree": FAST_TIMEOUT,
    "blender.get_animation_data": FAST_TIMEOUT,
    "blender.get_materials": FAST_TIMEOUT,
    "blender.get_scene": FAST_TIMEOUT,
    "blender.get_collections": FAST_TIMEOUT,
    "blender.get_armature_data": FAST_TIMEOUT,
    "blender.get_images": FAST_TIMEOUT,
    "blender.capture_viewport": FAST_TIMEOUT,
    "blender.get_selection": FAST_TIMEOUT,
    # Declarative write layer
    "blender.edit_nodes": STANDARD_TIMEOUT,
    "blender.edit_animation": STANDARD_TIMEOUT,
    "blender.edit_sequencer": STANDARD_TIMEOUT,
    # Imperative write layer
    "blender.create_object": STANDARD_TIMEOUT,
    "blender.modify_object": STANDARD_TIMEOUT,
    "blender.manage_material": STANDARD_TIMEOUT,
    "blender.manage_modifier": STANDARD_TIMEOUT,
    "blender.manage_collection": STANDARD_TIMEOUT,
    "blender.manage_uv": STANDARD_TIMEOUT,
    "blender.manage_constraints": STANDARD_TIMEOUT,
    "blender.manage_physics": STANDARD_TIMEOUT,
    "blender.setup_scene": STANDARD_TIMEOUT,
    # Fallback layer — potentially long-running
    "blender.execute_operator": SLOW_TIMEOUT,
    "blender.execute_script": SLOW_TIMEOUT,
    "blender.import_export": SLOW_TIMEOUT,
}


def get_timeout(capability: str) -> float:
    """Return the timeout in seconds for the given capability."""
    return _CAPABILITY_TIMEOUTS.get(capability, DEFAULT_TIMEOUT)
