# -*- coding: utf-8 -*-
"""MCP Prompt definitions for Blender MCP workflow guidance.

Prompts are user-controlled workflow templates triggered via /slash-commands.
They inject step-by-step tool usage guidance into the conversation.
"""
from __future__ import annotations

from typing import Any


BLENDER_PROMPTS: dict[str, dict[str, Any]] = {
    "blender-scene-setup": {
        "name": "blender-scene-setup",
        "title": "Set Up Blender Scene",
        "description": "Guide through creating a new scene with camera, lighting, and world setup.",
        "arguments": [
            {"name": "style", "description": "Rendering style: realistic, stylized, or architectural", "required": True},
            {"name": "resolution", "description": "Output resolution: 1080p, 4K, or square", "required": False},
        ],
    },
    "blender-material-create": {
        "name": "blender-material-create",
        "title": "Create Material",
        "description": "Guide through creating and assigning a PBR material.",
        "arguments": [
            {"name": "material_type", "description": "Material type: metal, glass, wood, fabric, emissive, custom", "required": True},
            {"name": "target_object", "description": "Object to assign the material to", "required": True},
        ],
    },
    "blender-model-asset": {
        "name": "blender-model-asset",
        "title": "Create Model Asset",
        "description": "Guide through creating a mesh asset with modifiers and organization.",
        "arguments": [
            {"name": "description", "description": "What to model", "required": True},
            {"name": "complexity", "description": "Complexity level: simple, moderate, or complex", "required": False},
        ],
    },
    "blender-animate": {
        "name": "blender-animate",
        "title": "Create Animation",
        "description": "Guide through creating animation on objects.",
        "arguments": [
            {"name": "animation_type", "description": "Animation type: transform, camera, character, or physics", "required": True},
            {"name": "target", "description": "Object to animate", "required": True},
        ],
    },
    "blender-composite": {
        "name": "blender-composite",
        "title": "Set Up Compositing",
        "description": "Guide through compositor post-processing effects.",
        "arguments": [
            {"name": "effects", "description": "Effect type: glow, color-grade, vignette, depth-of-field, or custom", "required": True},
        ],
    },
    "blender-render-output": {
        "name": "blender-render-output",
        "title": "Render Output",
        "description": "Guide through configuring and executing a final render.",
        "arguments": [
            {"name": "output_type", "description": "Output type: still, animation, or turntable", "required": True},
        ],
    },
    "blender-diagnose": {
        "name": "blender-diagnose",
        "title": "Diagnose Scene Issues",
        "description": "Systematically diagnose issues in a Blender scene.",
        "arguments": [],
    },
}


def _scene_setup_messages(args: dict[str, str]) -> list[dict[str, Any]]:
    style = args.get("style", "realistic")
    resolution = args.get("resolution", "1080p")
    return [{"role": "user", "content": {"type": "text", "text": (
        f"Set up a Blender scene for {style} rendering at {resolution}.\n\n"
        "Follow this workflow using the available tools:\n\n"
        "1. **Survey** — Call `blender_get_scene` to understand the current state.\n"
        "2. **Configure render** — Use `blender_setup_scene` to set engine "
        "(Cycles for realistic, Eevee for stylized), resolution, and samples.\n"
        "3. **Set up camera** — Use `blender_create_object` with object_type=CAMERA.\n"
        "4. **Set up lighting** — Use `blender_create_object` with object_type=LIGHT. "
        "For realistic: 3-point lighting with AREA lights. For stylized: single SUN light.\n"
        "5. **Set up world** — Use `blender_edit_nodes` with tree_type=SHADER, context=WORLD.\n"
        "6. **Verify** — Call `blender_capture_viewport` with shading=RENDERED.\n\n"
        "Always call read tools before making changes to avoid overwriting existing work."
    )}}]


def _material_create_messages(args: dict[str, str]) -> list[dict[str, Any]]:
    mat_type = args.get("material_type", "custom")
    target = args.get("target_object", "")
    return [{"role": "user", "content": {"type": "text", "text": (
        f"Create a {mat_type} material and assign it to '{target}'.\n\n"
        "Workflow:\n"
        "1. **Check existing** — Call `blender_get_materials` to see if a similar material exists.\n"
        "2. **Create material** — Use `blender_manage_material` with action=create and PBR values.\n"
        "3. **Add complexity** — Use `blender_edit_nodes` with tree_type=SHADER, context=OBJECT.\n"
        f"4. **Assign** — Use `blender_manage_material` with action=assign, object_name='{target}'.\n"
        "5. **Preview** — Call `blender_capture_viewport` with shading=MATERIAL."
    )}}]


def _model_asset_messages(args: dict[str, str]) -> list[dict[str, Any]]:
    desc = args.get("description", "an object")
    complexity = args.get("complexity", "moderate")
    return [{"role": "user", "content": {"type": "text", "text": (
        f"Create a {complexity} complexity model asset: {desc}.\n\n"
        "Workflow:\n"
        "1. **Survey** — Call `blender_get_objects` to check existing scene.\n"
        "2. **Create base** — Use `blender_create_object` with appropriate primitive.\n"
        "3. **Add modifiers** — Use `blender_manage_modifier` (mirror, subsurf, bevel).\n"
        "4. **Organize** — Use `blender_manage_collection` to place in a collection.\n"
        "5. **Material** — Use `blender_manage_material` to assign material.\n"
        "6. **UV unwrap** — Use `blender_manage_uv` with smart_project.\n"
        "7. **Verify** — Call `blender_capture_viewport` with shading=SOLID."
    )}}]


def _animate_messages(args: dict[str, str]) -> list[dict[str, Any]]:
    anim_type = args.get("animation_type", "transform")
    target = args.get("target", "")
    return [{"role": "user", "content": {"type": "text", "text": (
        f"Create {anim_type} animation on '{target}'.\n\n"
        "Workflow:\n"
        "1. **Check existing** — Call `blender_get_animation_data` for current animation.\n"
        "2. **Set timeline** — Use `blender_setup_scene` for frame range and FPS.\n"
        "3. **Insert keyframes** — Use `blender_edit_animation` with insert_keyframe.\n"
        "4. **Adjust curves** — Use `blender_edit_animation` with modify_keyframe.\n"
        "5. **(Optional) NLA** — Use `blender_edit_animation` with add_nla_strip.\n"
        "6. **Preview** — Call `blender_capture_viewport` at key frames."
    )}}]


def _composite_messages(args: dict[str, str]) -> list[dict[str, Any]]:
    effects = args.get("effects", "custom")
    return [{"role": "user", "content": {"type": "text", "text": (
        f"Set up compositor post-processing with {effects} effects.\n\n"
        "Workflow:\n"
        "1. **Read** — Call `blender_get_node_tree` with tree_type=COMPOSITOR, context=SCENE.\n"
        "2. **Edit** — Use `blender_edit_nodes` with tree_type=COMPOSITOR, context=SCENE.\n"
        "3. **Preview** — Call `blender_capture_viewport` with shading=RENDERED."
    )}}]


def _render_output_messages(args: dict[str, str]) -> list[dict[str, Any]]:
    output_type = args.get("output_type", "still")
    return [{"role": "user", "content": {"type": "text", "text": (
        f"Configure and execute a {output_type} render.\n\n"
        "Workflow:\n"
        "1. **Check settings** — Call `blender_get_scene` with include=['render','timeline'].\n"
        "2. **Adjust** — Use `blender_setup_scene` to set render settings.\n"
        "3. **Preview** — Call `blender_capture_viewport` with camera_view=true, shading=RENDERED.\n"
        "4. **Render** — Use `blender_execute_operator` with operator='render.render'."
    )}}]


def _diagnose_messages(args: dict[str, str]) -> list[dict[str, Any]]:
    return [{"role": "user", "content": {"type": "text", "text": (
        "Help me diagnose issues in my Blender scene.\n\n"
        "Diagnostic workflow:\n"
        "1. **Scene overview** — Call `blender_get_scene` with include=['stats','render','world','version'].\n"
        "2. **Object check** — Call `blender_get_objects` to list all objects.\n"
        "3. **Selection state** — Call `blender_get_selection`.\n"
        "4. **Visual check** — Call `blender_capture_viewport` with shading=RENDERED.\n"
        "5. **Material audit** — Call `blender_get_materials` with filter='all'.\n"
        "6. **Image check** — Call `blender_get_images` with filter='missing'.\n\n"
        "Report findings with severity (critical/warning/info) and recommended fixes."
    )}}]


_PROMPT_HANDLERS = {
    "blender-scene-setup": _scene_setup_messages,
    "blender-material-create": _material_create_messages,
    "blender-model-asset": _model_asset_messages,
    "blender-animate": _animate_messages,
    "blender-composite": _composite_messages,
    "blender-render-output": _render_output_messages,
    "blender-diagnose": _diagnose_messages,
}


def get_prompt(name: str) -> dict[str, Any] | None:
    """Get a prompt definition by name."""
    return BLENDER_PROMPTS.get(name)


def list_prompts() -> list[dict[str, Any]]:
    """Return all prompt definitions."""
    return list(BLENDER_PROMPTS.values())


def get_prompt_messages(name: str, arguments: dict[str, str] | None = None) -> dict[str, Any] | None:
    """Generate prompt messages for a given prompt name and arguments.
    
    Returns a GetPromptResult-compatible dict with 'messages' list,
    or None if prompt not found.
    """
    handler = _PROMPT_HANDLERS.get(name)
    if handler is None:
        return None
    prompt_def = BLENDER_PROMPTS.get(name)
    if prompt_def is None:
        return None
    return {
        "description": prompt_def.get("description", ""),
        "messages": handler(arguments or {}),
    }
