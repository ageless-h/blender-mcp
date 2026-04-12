# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class CapabilityMeta:
    name: str
    description: str
    scopes: List[str] = field(default_factory=list)
    min_version: str | None = None
    max_version: str | None = None


class CapabilityCatalog:
    def __init__(self) -> None:
        self._capabilities: Dict[str, CapabilityMeta] = {}

    def register(self, capability: CapabilityMeta) -> None:
        self._capabilities[capability.name] = capability

    def list(self) -> Iterable[CapabilityMeta]:
        return list(self._capabilities.values())

    def get(self, name: str) -> CapabilityMeta | None:
        return self._capabilities.get(name)


def capability_scope_map(
    capabilities: Iterable[CapabilityMeta],
) -> dict[str, set[str]]:
    return {
        capability.name: set(capability.scopes)
        for capability in capabilities
        if capability.scopes
    }


def _parse_version(version: str) -> tuple[int, ...] | None:
    parts: list[int] = []
    for raw in version.split("."):
        digits = "".join(ch for ch in raw if ch.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    if not parts:
        return None
    return tuple(parts)


def _lt(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    width = max(len(a), len(b))
    aa = a + (0,) * (width - len(a))
    bb = b + (0,) * (width - len(b))
    return aa < bb


def capability_availability(
    capability: CapabilityMeta, version: str | None
) -> tuple[bool, str | None]:
    if version is None:
        return True, None
    target = _parse_version(version)
    if target is None:
        return True, None
    if capability.min_version is not None:
        min_v = _parse_version(capability.min_version)
        if min_v is not None and _lt(target, min_v):
            return False, "version_below_min"
    if capability.max_version is not None:
        max_v = _parse_version(capability.max_version)
        if max_v is not None and not _lt(target, max_v):
            return False, "version_at_or_above_max"
    return True, None


def capability_to_dict(capability: CapabilityMeta, version: str | None = None) -> dict[str, object]:
    available, reason = capability_availability(capability, version)
    data: dict[str, object] = {
        "name": capability.name,
        "description": capability.description,
        "scopes": list(capability.scopes),
        "min_version": capability.min_version,
        "max_version": capability.max_version,
    }
    if version is not None:
        data["available"] = available
        if not available:
            data["unavailable_reason"] = reason
    return data


def minimal_capability_set() -> list[CapabilityMeta]:
    """Return the 26-tool capability set.

    Four layers:
    - Perception (11): read-only queries
    - Declarative Write (3): node/animation/VSE batch edits
    - Imperative Write (9): object/material/modifier etc.
    - Fallback (3): operator/script/import-export
    """
    return [
        # Perception layer (11)
        CapabilityMeta(name="blender.get_objects", description="List/filter scene objects", scopes=["data:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_object_data", description="Deep object data (12 include sections)", scopes=["data:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_node_tree", description="Read node tree (6 contexts)", scopes=["data:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_animation_data", description="Keyframes/NLA/drivers/shape keys", scopes=["data:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_materials", description="Material asset list", scopes=["data:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_scene", description="Scene stats/render/world/version/memory", scopes=["info:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_collections", description="Collection hierarchy tree", scopes=["data:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_armature_data", description="Armature/bone hierarchy/constraints/poses", scopes=["data:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_images", description="Texture/image asset list", scopes=["data:read"], min_version="4.2"),
        CapabilityMeta(name="blender.capture_viewport", description="Viewport screenshot", scopes=["info:read"], min_version="4.2"),
        CapabilityMeta(name="blender.get_selection", description="Current selection/mode/active object", scopes=["info:read"], min_version="4.2"),
        # Declarative write layer (3)
        CapabilityMeta(name="blender.edit_nodes", description="Edit any node tree", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.edit_animation", description="Keyframe/NLA/driver/shape key edits", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.edit_sequencer", description="VSE strip/transition/effect edits", scopes=["data:write"], min_version="4.2"),
        # Imperative write layer (9)
        CapabilityMeta(name="blender.create_object", description="Create objects (MESH/LIGHT/CAMERA/...)", scopes=["data:create"], min_version="4.2"),
        CapabilityMeta(name="blender.modify_object", description="Transform/parent/visibility/rename/delete", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.manage_material", description="Material CRUD + PBR + assign", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.manage_modifier", description="Modifier add/configure/apply/remove/move", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.manage_collection", description="Collection CRUD + object linking", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.manage_uv", description="UV unwrap/seam/pack/layers", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.manage_constraints", description="Object/bone constraint management", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.manage_physics", description="Physics simulation management", scopes=["data:write"], min_version="4.2"),
        CapabilityMeta(name="blender.setup_scene", description="Render engine/output/world/timeline", scopes=["data:write"], min_version="4.2"),
        # Fallback layer (3)
        CapabilityMeta(name="blender.execute_operator", description="Execute any bpy.ops.*", scopes=["operator:execute"], min_version="4.2"),
        CapabilityMeta(name="blender.execute_script", description="Execute Python code (dangerous, disabled by default)", scopes=["script:execute"], min_version="4.2"),
        CapabilityMeta(name="blender.import_export", description="Import/export FBX/OBJ/GLTF/GLB/USD/STL", scopes=["data:write", "operator:execute"], min_version="4.2"),
    ]


def new_tool_scope_map() -> dict[str, set[str]]:
    """Return scope mappings for the 26-tool architecture.

    Maps internal capability names to required scopes.
    """
    return {
        "blender.get_objects": {"data:read"},
        "blender.get_object_data": {"data:read"},
        "blender.get_node_tree": {"data:read"},
        "blender.get_animation_data": {"data:read"},
        "blender.get_materials": {"data:read"},
        "blender.get_scene": {"info:read"},
        "blender.get_collections": {"data:read"},
        "blender.get_armature_data": {"data:read"},
        "blender.get_images": {"data:read"},
        "blender.capture_viewport": {"info:read"},
        "blender.get_selection": {"info:read"},
        "blender.edit_nodes": {"data:write"},
        "blender.edit_animation": {"data:write"},
        "blender.edit_sequencer": {"data:write"},
        "blender.create_object": {"data:create"},
        "blender.modify_object": {"data:write"},
        "blender.manage_material": {"data:write"},
        "blender.manage_modifier": {"data:write"},
        "blender.manage_collection": {"data:write"},
        "blender.manage_uv": {"data:write"},
        "blender.manage_constraints": {"data:write"},
        "blender.manage_physics": {"data:write"},
        "blender.setup_scene": {"data:write"},
        "blender.execute_operator": {"operator:execute"},
        "blender.execute_script": {"script:execute"},
        "blender.import_export": {"data:write", "operator:execute"},
    }


def get_dynamic_scopes(capability: str, payload: dict) -> set[str]:
    """Get dynamic scopes based on capability and payload.

    For blender.execute_operator, the scope depends on the operator category.
    For other capabilities, falls back to the static scope map.

    Args:
        capability: The capability name (blender.* format)
        payload: The request payload

    Returns:
        Set of required scope strings
    """
    if capability == "blender.execute_operator":
        operator_id = payload.get("operator", "")
        if "." in operator_id:
            category = operator_id.split(".")[0]
            return {f"{category}:execute"}
        return {"operator:execute"}

    if capability == "blender.execute_script":
        return {"script:execute"}

    # Fall back to static scope map
    scope_map = new_tool_scope_map()
    return scope_map.get(capability, set())
