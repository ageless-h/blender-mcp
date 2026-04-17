# -*- coding: utf-8 -*-
"""MCP Prompt registry for Blender MCP.

This module provides an empty prompt registry. All prompts have been removed
as they were rarely used (user-controlled via /slash-commands) while tools
(model-controlled) provide sufficient functionality for the model to work.

For workflow guidance, see the blender-skills repository or tool descriptions.
"""

from __future__ import annotations

from typing import Any

# Empty prompt registry - all prompts removed
BLENDER_PROMPTS: dict[str, dict[str, Any]] = {}


def get_prompt(name: str) -> dict[str, Any] | None:
    """Get a prompt definition by name.

    Returns None as no prompts are defined.
    """
    return None


def list_prompts() -> list[dict[str, Any]]:
    """Return all prompt definitions.

    Returns empty list as no prompts are defined.
    """
    return []


def get_prompt_messages(name: str, arguments: dict[str, str] | None = None) -> dict[str, Any] | None:
    """Generate prompt messages for a given prompt name and arguments.

    Returns None as no prompts are defined.
    """
    return None
