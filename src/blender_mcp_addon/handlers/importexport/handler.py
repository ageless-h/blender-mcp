# -*- coding: utf-8 -*-
"""Import/export handler — maps format enum to specific Blender operators."""
from __future__ import annotations

from typing import Any

from ..response import _ok, _error, check_bpy_available, bpy_unavailable_error


_IMPORT_OPERATORS = {
    "FBX": "import_scene.fbx",
    "OBJ": "wm.obj_import",
    "GLTF": "import_scene.gltf",
    "GLB": "import_scene.gltf",
    "USD": "wm.usd_import",
    "USDC": "wm.usd_import",
    "USDA": "wm.usd_import",
    "ALEMBIC": "wm.alembic_import",
    "STL": "wm.stl_import",
    "PLY": "wm.ply_import",
    "SVG": "import_curve.svg",
    "DAE": "wm.collada_import",
    "X3D": "import_scene.x3d",
}

_EXPORT_OPERATORS = {
    "FBX": "export_scene.fbx",
    "OBJ": "wm.obj_export",
    "GLTF": "export_scene.gltf",
    "GLB": "export_scene.gltf",
    "USD": "wm.usd_export",
    "USDC": "wm.usd_export",
    "USDA": "wm.usd_export",
    "ALEMBIC": "wm.alembic_export",
    "STL": "wm.stl_export",
    "PLY": "wm.ply_export",
    "SVG": "export_curve.svg",
    "DAE": "wm.collada_export",
    "X3D": "export_scene.x3d",
}


def _validate_filepath(filepath: str) -> str | None:
    """Validate and normalize a file path, rejecting path traversal attempts.
    
    Returns the resolved absolute path, or None if the path is invalid.
    """
    import os
    
    if not filepath or not isinstance(filepath, str):
        return None
    
    # Reject null bytes
    if "\x00" in filepath:
        return None
    
    # Resolve to absolute path
    resolved = os.path.realpath(filepath)
    return resolved


def import_export(payload: dict[str, Any], *, started: float) -> dict[str, Any]:
    """Import or export files using Blender operators."""
    available, bpy = check_bpy_available()
    if not available:
        return bpy_unavailable_error(started)

    action = payload.get("action", "")
    fmt = payload.get("format", "")
    filepath = payload.get("filepath", "")

    if action not in ("import", "export"):
        return _error(code="invalid_params", message="action must be 'import' or 'export'", started=started)
    if not fmt:
        return _error(code="invalid_params", message="format is required", started=started)
    if not filepath:
        return _error(code="invalid_params", message="filepath is required", started=started)

    validated_path = _validate_filepath(filepath)
    if validated_path is None:
        return _error(code="invalid_params", message="Invalid or unsafe file path", started=started)
    filepath = validated_path

    op_map = _IMPORT_OPERATORS if action == "import" else _EXPORT_OPERATORS
    operator_id = op_map.get(fmt)
    if not operator_id:
        return _error(code="invalid_params", message=f"Unsupported format: {fmt}", started=started)

    # Build operator params
    params: dict[str, Any] = {"filepath": filepath}
    settings = payload.get("settings", {})
    params.update(settings)

    # Handle GLB export format
    if fmt == "GLB" and action == "export":
        params.setdefault("export_format", "GLB")

    try:
        # Resolve operator
        parts = operator_id.split(".")
        op_module = getattr(bpy.ops, parts[0])
        op_func = getattr(op_module, parts[1])
        result = op_func(**params)
        status = "FINISHED" if result == {"FINISHED"} else str(result)
    except Exception as exc:
        return _error(code="operation_failed", message=f"{action} {fmt} failed: {exc}", started=started)

    return _ok(result={
        "action": action,
        "format": fmt,
        "filepath": filepath,
        "operator": operator_id,
        "status": status,
    }, started=started)
