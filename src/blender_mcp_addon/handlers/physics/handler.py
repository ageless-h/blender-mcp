# -*- coding: utf-8 -*-
"""Physics simulation handler — rigid body, cloth, soft body, fluid, particle, force field."""

from __future__ import annotations

import logging
from typing import Any

from ..context_utils import get_view3d_override
from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available

logger = logging.getLogger(__name__)


def physics_manage(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Manage physics simulations on objects."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    action = payload.get("action", "")
    object_name = payload.get("object_name", "")

    if not action:
        return _error(code="invalid_params", message="action is required", started=started)
    if not object_name:
        return _error(code="invalid_params", message="object_name is required", started=started)

    obj = bpy.data.objects.get(object_name)
    if obj is None:
        return _error(code="not_found", message=f"Object '{object_name}' not found", started=started)

    # Make active for operator calls
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    try:
        if action == "add":
            return _add_physics(bpy, obj, payload, started)
        elif action == "configure":
            return _configure_physics(obj, payload, started)
        elif action == "remove":
            return _remove_physics(bpy, obj, payload, started)
        elif action == "bake":
            return _bake_physics(bpy, payload, started)
        elif action == "free_bake":
            return _free_bake(bpy, payload, started)
        else:
            return _error(code="invalid_params", message=f"Unknown action: {action}", started=started)
    except (AttributeError, RuntimeError, TypeError) as exc:
        return _error(code="operation_failed", message=f"Physics {action} failed: {exc}", started=started)


def _add_physics(bpy: Any, obj: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    physics_type = payload.get("physics_type", "")
    if not physics_type:
        return _error(code="invalid_params", message="physics_type is required for add", started=started)

    ctx = get_view3d_override(bpy, obj)

    if physics_type in ("RIGID_BODY", "RIGID_BODY_PASSIVE"):
        # Ensure scene has a Rigid Body World
        if bpy.context.scene.rigidbody_world is None:
            bpy.ops.rigidbody.world_add()
        rb_type = "PASSIVE" if physics_type == "RIGID_BODY_PASSIVE" else "ACTIVE"
        with bpy.context.temp_override(**ctx):
            bpy.ops.rigidbody.object_add(type=rb_type)
    elif physics_type == "CLOTH":
        with bpy.context.temp_override(**ctx):
            bpy.ops.object.modifier_add(type="CLOTH")
    elif physics_type == "SOFT_BODY":
        with bpy.context.temp_override(**ctx):
            bpy.ops.object.modifier_add(type="SOFT_BODY")
    elif physics_type == "FLUID_DOMAIN":
        with bpy.context.temp_override(**ctx):
            bpy.ops.object.modifier_add(type="FLUID")
        if obj.modifiers and obj.modifiers[-1].type == "FLUID":
            obj.modifiers[-1].fluid_type = "DOMAIN"
    elif physics_type == "FLUID_FLOW":
        with bpy.context.temp_override(**ctx):
            bpy.ops.object.modifier_add(type="FLUID")
        if obj.modifiers and obj.modifiers[-1].type == "FLUID":
            obj.modifiers[-1].fluid_type = "FLOW"
    elif physics_type == "PARTICLE":
        with bpy.context.temp_override(**ctx):
            bpy.ops.object.particle_system_add()
    elif physics_type == "FORCE_FIELD":
        ff_type = payload.get("force_field_type", "FORCE")
        obj.field.type = ff_type
    else:
        return _error(code="invalid_params", message=f"Unknown physics_type: {physics_type}", started=started)

    # Apply initial settings
    settings = payload.get("settings", {})
    if settings:
        _apply_settings(obj, physics_type, settings)

    return _ok(result={"action": "add", "object": obj.name, "physics_type": physics_type}, started=started)


def _configure_physics(obj: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    physics_type = payload.get("physics_type", "")
    settings = payload.get("settings", {})

    if not settings:
        return _error(code="invalid_params", message="settings are required for configure", started=started)

    _apply_settings(obj, physics_type, settings)
    return _ok(
        result={"action": "configure", "object": obj.name, "settings_applied": list(settings.keys())}, started=started
    )


def _apply_settings(obj: Any, physics_type: str, settings: dict[str, Any]) -> None:
    """Apply physics settings to the appropriate physics data."""
    target = None
    if physics_type in ("RIGID_BODY", "RIGID_BODY_PASSIVE") and obj.rigid_body:
        target = obj.rigid_body
    elif physics_type == "CLOTH":
        for mod in obj.modifiers:
            if mod.type == "CLOTH":
                target = mod.settings
                break
    elif physics_type == "SOFT_BODY":
        for mod in obj.modifiers:
            if mod.type == "SOFT_BODY":
                target = mod.settings
                break
    elif physics_type == "PARTICLE" and obj.particle_systems:
        target = obj.particle_systems[-1].settings
    elif physics_type == "FORCE_FIELD" and obj.field:
        target = obj.field

    if target:
        for key, value in settings.items():
            if hasattr(target, key):
                setattr(target, key, value)


def _remove_physics(bpy: Any, obj: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    physics_type = payload.get("physics_type", "")

    if physics_type in ("RIGID_BODY", "RIGID_BODY_PASSIVE"):
        bpy.ops.rigidbody.object_remove()
    elif physics_type in ("CLOTH", "SOFT_BODY", "FLUID_DOMAIN", "FLUID_FLOW"):
        mod_type = {"CLOTH": "CLOTH", "SOFT_BODY": "SOFT_BODY", "FLUID_DOMAIN": "FLUID", "FLUID_FLOW": "FLUID"}.get(
            physics_type
        )
        for mod in obj.modifiers:
            if mod.type == mod_type:
                obj.modifiers.remove(mod)
                break
    elif physics_type == "PARTICLE":
        if obj.particle_systems:
            bpy.ops.object.particle_system_remove()
    elif physics_type == "FORCE_FIELD":
        obj.field.type = "NONE"
    else:
        return _error(code="invalid_params", message=f"Unknown physics_type: {physics_type}", started=started)

    return _ok(result={"action": "remove", "object": obj.name, "physics_type": physics_type}, started=started)


def _bake_physics(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    frame_start = payload.get("frame_start")
    frame_end = payload.get("frame_end")
    if frame_start is not None:
        bpy.context.scene.frame_start = frame_start
    if frame_end is not None:
        bpy.context.scene.frame_end = frame_end
    bpy.ops.ptcache.bake_all(bake=True)
    return _ok(result={"action": "bake", "message": "Physics baked"}, started=started)


def _free_bake(bpy: Any, payload: dict[str, Any], started: float) -> dict[str, Any]:
    bpy.ops.ptcache.free_bake_all()
    return _ok(result={"action": "free_bake", "message": "Physics bake freed"}, started=started)
