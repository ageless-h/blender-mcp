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
    """Return the minimal capability set using the new unified tool architecture.
    
    The 8 core tools cover 99.9% of Blender functionality:
    - data.create/read/write/delete/list/link: Unified data CRUD
    - operator.execute: Universal operator execution
    - info.query: Status and metadata queries
    
    Optional (disabled by default):
    - script.execute: Arbitrary Python execution
    
    NOTE: This function is kept for backward compatibility.
    The new 26-tool architecture is defined in blender_mcp.schemas.tools.
    """
    return [
        # Data layer tools (CRUD for all Blender data types)
        CapabilityMeta(
            name="data.create",
            description="[LEGACY] Create new Blender data blocks — use blender_create_object instead",
            scopes=["data:create"],
            min_version="4.2",
        ),
        CapabilityMeta(
            name="data.read",
            description="[LEGACY] Read properties — use blender_get_object_data instead",
            scopes=["data:read"],
            min_version="4.2",
        ),
        CapabilityMeta(
            name="data.write",
            description="[LEGACY] Write properties — use blender_modify_object instead",
            scopes=["data:write"],
            min_version="4.2",
        ),
        CapabilityMeta(
            name="data.delete",
            description="[LEGACY] Delete data blocks — use blender_modify_object with delete=true instead",
            scopes=["data:delete"],
            min_version="4.2",
        ),
        CapabilityMeta(
            name="data.list",
            description="[LEGACY] List data blocks — use blender_get_objects instead",
            scopes=["data:read"],
            min_version="4.2",
        ),
        CapabilityMeta(
            name="data.link",
            description="[LEGACY] Link data blocks — use blender_manage_collection instead",
            scopes=["data:write"],
            min_version="4.2",
        ),
        # Operator layer tool
        CapabilityMeta(
            name="operator.execute",
            description="[LEGACY] Execute operator — use blender_execute_operator instead",
            scopes=["operator:execute"],
            min_version="4.2",
        ),
        # Info layer tool
        CapabilityMeta(
            name="info.query",
            description="[LEGACY] Query info — use blender_get_scene instead",
            scopes=["info:read"],
            min_version="4.2",
        ),
        # Optional dangerous tool (disabled by default)
        CapabilityMeta(
            name="script.execute",
            description="[LEGACY] Execute script — use blender_execute_script instead",
            scopes=["script:execute"],
            min_version="4.2",
        ),
        # Legacy capabilities (deprecated, for backward compatibility)
        CapabilityMeta(
            name="scene.read",
            description="[DEPRECATED] Read scene - use blender_get_scene instead",
            scopes=["scene:read"],
            min_version="4.2",
        ),
        CapabilityMeta(
            name="scene.write",
            description="[DEPRECATED] Write to scene - use blender_setup_scene instead",
            scopes=["scene:write"],
            min_version="4.2",
        ),
    ]


def new_tool_scope_map() -> dict[str, set[str]]:
    """Return scope mappings for new 26-tool architecture.
    
    Maps internal capability names to required scopes.
    """
    return {
        # Legacy mappings (kept for backward compatibility)
        "data.create": {"data:create"},
        "data.read": {"data:read"},
        "data.write": {"data:write"},
        "data.delete": {"data:delete"},
        "data.list": {"data:read"},
        "data.link": {"data:write"},
        "operator.execute": {"operator:execute"},
        "info.query": {"info:read"},
        "script.execute": {"script:execute"},
        # New tool internal capabilities
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
    
    For data.* tools, the required scope depends on the data type.
    For operator.execute, the scope depends on the operator category.
    
    Args:
        capability: The capability name
        payload: The request payload
        
    Returns:
        Set of required scope strings
    """
    if capability.startswith("data."):
        data_type = payload.get("type", "")
        action = capability.split(".")[-1]
        if action in ("read", "list"):
            return {f"{data_type}:read"} if data_type else {"data:read"}
        elif action == "create":
            return {f"{data_type}:create"} if data_type else {"data:create"}
        elif action in ("write", "link"):
            return {f"{data_type}:write"} if data_type else {"data:write"}
        elif action == "delete":
            return {f"{data_type}:delete"} if data_type else {"data:delete"}
    
    elif capability == "operator.execute":
        operator_id = payload.get("operator", "")
        if "." in operator_id:
            category = operator_id.split(".")[0]
            return {f"{category}:execute"}
        return {"operator:execute"}
    
    elif capability == "info.query":
        return {"info:read"}
    
    elif capability == "script.execute":
        return {"script:execute"}
    
    return set()
