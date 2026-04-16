# -*- coding: utf-8 -*-
"""Declarative write layer handlers — 3 tools for node/animation/sequencer editing."""

from __future__ import annotations

from typing import Any


def _handle_edit_nodes(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.nodes.editor import node_tree_edit

    return node_tree_edit(payload, started=started)


def _handle_edit_animation(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.animation.editor import animation_edit

    return animation_edit(payload, started=started)


def _handle_edit_sequencer(payload: dict[str, Any], started: float) -> dict[str, Any]:
    from ..handlers.sequencer.editor import sequencer_edit

    return sequencer_edit(payload, started=started)


DECLARATIVE_HANDLERS = {
    "blender.edit_nodes": _handle_edit_nodes,
    "blender.edit_animation": _handle_edit_animation,
    "blender.edit_sequencer": _handle_edit_sequencer,
}
