# -*- coding: utf-8 -*-
"""Constraint handler — add/configure/remove/enable/disable constraints on objects and bones."""
from __future__ import annotations

import logging
from typing import Any

from ..response import _error, _ok, bpy_unavailable_error, check_bpy_available

logger = logging.getLogger(__name__)


def _resolve_target(bpy: Any, payload: dict[str, Any], started: float):
    """Resolve target object and optional bone for constraint operations."""
    target_type = payload.get("target_type", "OBJECT")
    target_name = payload.get("target_name", "")

    if not target_name:
        return None, None, _error(code="invalid_params", message="target_name is required", started=started)

    if target_type == "BONE" and "/" in target_name:
        armature_name, bone_name = target_name.split("/", 1)
        obj = bpy.data.objects.get(armature_name)
        if obj is None or obj.type != "ARMATURE":
            return None, None, _error(code="not_found", message=f"Armature '{armature_name}' not found", started=started)
        bone = obj.pose.bones.get(bone_name) if obj.pose else None
        if bone is None:
            return None, None, _error(code="not_found", message=f"Bone '{bone_name}' not found", started=started)
        return obj, bone, None
    else:
        obj = bpy.data.objects.get(target_name)
        if obj is None:
            return None, None, _error(code="not_found", message=f"Object '{target_name}' not found", started=started)
        return obj, None, None


def constraints_manage(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Manage constraints on objects or bones."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    action = payload.get("action", "")
    if not action:
        return _error(code="invalid_params", message="action is required", started=started)

    obj, bone, err = _resolve_target(bpy, payload, started)
    if err:
        return err
    assert obj is not None  # guaranteed by _resolve_target when err is None

    constraints = bone.constraints if bone else obj.constraints

    try:
        if action == "add":
            constraint_type = payload.get("constraint_type", "")
            if not constraint_type:
                return _error(code="invalid_params", message="constraint_type is required for add", started=started)
            constraint_name = payload.get("constraint_name", constraint_type)
            c = constraints.new(type=constraint_type)
            c.name = constraint_name
            settings = payload.get("settings", {})
            for key, value in settings.items():
                if key == "target":
                    target_obj = bpy.data.objects.get(value)
                    if target_obj:
                        c.target = target_obj
                elif key == "subtarget":
                    c.subtarget = value
                elif hasattr(c, key):
                    setattr(c, key, value)
            return _ok(result={"action": "add", "name": c.name, "type": constraint_type}, started=started)

        elif action == "configure":
            constraint_name = payload.get("constraint_name", "")
            c = constraints.get(constraint_name)
            if not c:
                return _error(code="not_found", message=f"Constraint '{constraint_name}' not found", started=started)
            settings = payload.get("settings", {})
            for key, value in settings.items():
                if key == "target":
                    target_obj = bpy.data.objects.get(value)
                    if target_obj:
                        c.target = target_obj
                elif hasattr(c, key):
                    setattr(c, key, value)
            return _ok(result={"action": "configure", "name": c.name}, started=started)

        elif action == "remove":
            constraint_name = payload.get("constraint_name", "")
            c = constraints.get(constraint_name)
            if not c:
                return _error(code="not_found", message=f"Constraint '{constraint_name}' not found", started=started)
            constraints.remove(c)
            return _ok(result={"action": "remove", "removed": constraint_name}, started=started)

        elif action in ("enable", "disable"):
            constraint_name = payload.get("constraint_name", "")
            c = constraints.get(constraint_name)
            if not c:
                return _error(code="not_found", message=f"Constraint '{constraint_name}' not found", started=started)
            c.mute = (action == "disable")
            return _ok(result={"action": action, "name": c.name, "muted": c.mute}, started=started)

        elif action in ("move_up", "move_down"):
            constraint_name = payload.get("constraint_name", "")
            bpy.context.view_layer.objects.active = obj
            if bone:
                bpy.ops.object.mode_set(mode="POSE")
                bone.bone.select = True
            override = {"constraint": constraint_name}
            if action == "move_up":
                bpy.ops.constraint.move_up(override, constraint=constraint_name)
            else:
                bpy.ops.constraint.move_down(override, constraint=constraint_name)
            return _ok(result={"action": action, "name": constraint_name}, started=started)

        else:
            return _error(code="invalid_params", message=f"Unknown action: {action}", started=started)

    except Exception as exc:
        return _error(code="operation_failed", message=f"Constraint {action} failed: {exc}", started=started)
