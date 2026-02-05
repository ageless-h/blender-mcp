# -*- coding: utf-8 -*-
"""Operator execution with context override support."""
from __future__ import annotations

import time
from typing import Any

from ..response import (
    _ok, _error, check_bpy_available, bpy_unavailable_error,
    invalid_params_error, operation_failed_error,
)


OPERATOR_SCOPE_MAP: dict[str, list[str]] = {
    "mesh": ["mesh:execute"],
    "object": ["object:execute"],
    "render": ["render:execute"],
    "export_scene": ["export:execute"],
    "import_scene": ["import:execute"],
    "export_mesh": ["export:execute"],
    "import_mesh": ["import:execute"],
    "wm": ["wm:execute"],
    "ed": ["edit:execute"],
    "transform": ["transform:execute"],
    "view3d": ["view3d:execute"],
    "uv": ["uv:execute"],
    "node": ["node:execute"],
    "anim": ["animation:execute"],
    "action": ["animation:execute"],
    "nla": ["animation:execute"],
    "pose": ["pose:execute"],
    "armature": ["armature:execute"],
    "sculpt": ["sculpt:execute"],
    "paint": ["paint:execute"],
    "gpencil": ["gpencil:execute"],
    "curve": ["curve:execute"],
    "surface": ["surface:execute"],
    "font": ["font:execute"],
    "lattice": ["lattice:execute"],
    "outliner": ["outliner:execute"],
    "sequencer": ["sequencer:execute"],
    "clip": ["clip:execute"],
    "image": ["image:execute"],
    "file": ["file:execute"],
    "preferences": ["preferences:execute"],
    "screen": ["screen:execute"],
    "workspace": ["workspace:execute"],
    "scene": ["scene:execute"],
    "material": ["material:execute"],
    "texture": ["texture:execute"],
    "world": ["world:execute"],
    "particle": ["particle:execute"],
    "physics": ["physics:execute"],
    "constraint": ["constraint:execute"],
    "marker": ["marker:execute"],
    "text": ["text:execute"],
    "script": ["script:execute"],
    "sound": ["sound:execute"],
    "rigidbody": ["rigidbody:execute"],
    "fluid": ["fluid:execute"],
    "cloth": ["cloth:execute"],
    "boid": ["boid:execute"],
    "brush": ["brush:execute"],
    "palette": ["palette:execute"],
    "mask": ["mask:execute"],
    "graph": ["graph:execute"],
    "dpaint": ["dpaint:execute"],
    "safe_areas": ["safe_areas:execute"],
    "buttons": ["buttons:execute"],
    "console": ["console:execute"],
    "info": ["info:execute"],
}


def get_operator_scopes(operator_id: str) -> list[str]:
    """Get required scopes for an operator.
    
    Args:
        operator_id: Operator identifier (e.g., "mesh.primitive_cube_add")
        
    Returns:
        List of required scope strings
    """
    if "." not in operator_id:
        return ["operator:execute"]
    
    category = operator_id.split(".")[0]
    return OPERATOR_SCOPE_MAP.get(category, ["operator:execute"])


def operator_execute(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Execute a Blender operator (bpy.ops.*).
    
    Args:
        payload: Execution parameters:
            - operator: Operator identifier (e.g., "mesh.primitive_cube_add")
            - params: Operator parameters
            - context: Context override settings
        started: Start time for timing
        
    Returns:
        Response dict with execution result
    """
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)
    
    operator_id = payload.get("operator")
    if not operator_id:
        return invalid_params_error("'operator' parameter is required", started)
    
    if not isinstance(operator_id, str) or "." not in operator_id:
        return invalid_params_error(
            f"Invalid operator identifier: {operator_id}. "
            "Expected format: 'category.operator_name' (e.g., 'mesh.primitive_cube_add')",
            started,
        )
    
    params = payload.get("params", {})
    context_override = payload.get("context", {})
    
    try:
        category, op_name = operator_id.split(".", 1)
        
        if not hasattr(bpy.ops, category):
            return _error(
                code="invalid_operator",
                message=f"Operator category '{category}' not found",
                data={"operator": operator_id},
                started=started,
            )
        
        op_category = getattr(bpy.ops, category)
        if not hasattr(op_category, op_name):
            return _error(
                code="invalid_operator",
                message=f"Operator '{op_name}' not found in category '{category}'",
                data={"operator": operator_id},
                started=started,
            )
        
        op_func = getattr(op_category, op_name)
        
        override_dict, cleanup_func = _build_context_override(bpy, context_override)
        
        exec_start = time.perf_counter()
        
        try:
            reports_before = _get_reports_snapshot(bpy)
            
            if override_dict:
                with bpy.context.temp_override(**override_dict):
                    result = op_func(**params)
            else:
                result = op_func(**params)
            
            reports_after = _get_reports_snapshot(bpy)
            new_reports = _extract_new_reports(reports_before, reports_after)
            
            exec_duration = (time.perf_counter() - exec_start) * 1000.0
            
            result_str = _result_to_string(result)
            success = result_str in ("FINISHED", "FINISHED_MODAL")
            
            return _ok(
                result={
                    "success": success,
                    "operator": operator_id,
                    "result": result_str,
                    "reports": new_reports,
                    "duration_ms": exec_duration,
                    "scopes": get_operator_scopes(operator_id),
                },
                started=started,
            )
        finally:
            if cleanup_func:
                cleanup_func()
                
    except TypeError as exc:
        return _error(
            code="invalid_params",
            message=f"Invalid operator parameters: {str(exc)}",
            data={"operator": operator_id, "params": params},
            started=started,
        )
    except RuntimeError as exc:
        return _error(
            code="operator_error",
            message=f"Operator execution error: {str(exc)}",
            data={"operator": operator_id},
            started=started,
        )
    except Exception as exc:
        return operation_failed_error("operator.execute", exc, started)


def _build_context_override(bpy: Any, context_override: dict[str, Any]) -> tuple[dict[str, Any], Any]:
    """Build context override dictionary for temp_override.
    
    Args:
        bpy: The bpy module
        context_override: User-specified context overrides
        
    Returns:
        Tuple of (override_dict, cleanup_function)
    """
    if not context_override:
        return {}, None
    
    override = {}
    cleanup_actions = []
    original_mode = None
    original_active = None
    original_selected = None
    
    if "active_object" in context_override:
        obj_name = context_override["active_object"]
        obj = bpy.data.objects.get(obj_name)
        if obj:
            original_active = bpy.context.view_layer.objects.active
            bpy.context.view_layer.objects.active = obj
            cleanup_actions.append(("active", original_active))
    
    if "selected_objects" in context_override:
        obj_names = context_override["selected_objects"]
        original_selected = [o for o in bpy.context.selected_objects]
        bpy.ops.object.select_all(action='DESELECT')
        for obj_name in obj_names:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                obj.select_set(True)
        cleanup_actions.append(("selected", original_selected))
    
    if "mode" in context_override:
        target_mode = context_override["mode"].upper()
        original_mode = bpy.context.mode
        if original_mode != target_mode:
            try:
                if target_mode == "OBJECT":
                    bpy.ops.object.mode_set(mode='OBJECT')
                elif target_mode in ("EDIT", "EDIT_MESH"):
                    bpy.ops.object.mode_set(mode='EDIT')
                elif target_mode == "SCULPT":
                    bpy.ops.object.mode_set(mode='SCULPT')
                elif target_mode == "POSE":
                    bpy.ops.object.mode_set(mode='POSE')
                cleanup_actions.append(("mode", original_mode))
            except RuntimeError:
                pass
    
    if "area_type" in context_override:
        for area in bpy.context.screen.areas:
            if area.type == context_override["area_type"]:
                override["area"] = area
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override["region"] = region
                        break
                break
    
    if "scene" in context_override:
        scene = bpy.data.scenes.get(context_override["scene"])
        if scene:
            override["scene"] = scene
    
    if "window" in context_override:
        override["window"] = bpy.context.window
    
    def cleanup():
        for action_type, original_value in reversed(cleanup_actions):
            try:
                if action_type == "mode" and original_value:
                    mode_str = original_value.replace("_MESH", "")
                    if mode_str in ("OBJECT", "EDIT", "SCULPT", "POSE"):
                        bpy.ops.object.mode_set(mode=mode_str)
                elif action_type == "active":
                    bpy.context.view_layer.objects.active = original_value
                elif action_type == "selected":
                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in original_value:
                        if obj:
                            obj.select_set(True)
            except Exception:
                pass
    
    return override, cleanup if cleanup_actions else None


def _get_reports_snapshot(bpy: Any) -> list[tuple[str, str]]:
    """Get a snapshot of current reports.
    
    Args:
        bpy: The bpy module
        
    Returns:
        List of (type, message) tuples
    """
    try:
        wm = bpy.context.window_manager
        if hasattr(wm, "reports"):
            return [(r.type, r.message) for r in wm.reports]
    except Exception:
        pass
    return []


def _extract_new_reports(
    before: list[tuple[str, str]],
    after: list[tuple[str, str]],
) -> list[dict[str, str]]:
    """Extract new reports added after an operation.
    
    Args:
        before: Reports snapshot before operation
        after: Reports snapshot after operation
        
    Returns:
        List of new report dicts with 'type' and 'message'
    """
    before_set = set(before)
    new_reports = []
    for report_type, message in after:
        if (report_type, message) not in before_set:
            new_reports.append({"type": report_type, "message": message})
    return new_reports


def _result_to_string(result: Any) -> str:
    """Convert operator result to string.
    
    Args:
        result: Operator return value (usually a set)
        
    Returns:
        Result status string
    """
    if isinstance(result, set):
        if "FINISHED" in result:
            return "FINISHED"
        elif "CANCELLED" in result:
            return "CANCELLED"
        elif "RUNNING_MODAL" in result:
            return "RUNNING_MODAL"
        elif "PASS_THROUGH" in result:
            return "PASS_THROUGH"
        elif "INTERFACE" in result:
            return "INTERFACE"
        return str(result)
    return str(result)
