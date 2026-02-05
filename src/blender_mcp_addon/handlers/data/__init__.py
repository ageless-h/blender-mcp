# -*- coding: utf-8 -*-
"""Data type handlers for unified CRUD operations."""
from __future__ import annotations

from .object_handler import ObjectHandler
from .mesh_handler import MeshHandler
from .material_handler import MaterialHandler
from .collection_handler import CollectionHandler
from .scene_handler import SceneHandler
from .node_tree_handler import NodeTreeHandler
from .image_handler import ImageHandler
from .context_handler import ContextHandler
from .modifier_handler import ModifierHandler
from .core_handlers import (
    CameraHandler,
    LightHandler,
    ArmatureHandler,
    CurveHandler,
    WorldHandler,
    FontHandler,
    TextHandler,
    MetaBallHandler,
    GreasePencilHandler,
)

__all__ = [
    "ObjectHandler",
    "MeshHandler",
    "MaterialHandler",
    "CollectionHandler",
    "SceneHandler",
    "NodeTreeHandler",
    "ImageHandler",
    "ContextHandler",
    "ModifierHandler",
    "CameraHandler",
    "LightHandler",
    "ArmatureHandler",
    "CurveHandler",
    "WorldHandler",
    "FontHandler",
    "TextHandler",
    "MetaBallHandler",
    "GreasePencilHandler",
]
