# -*- coding: utf-8 -*-
"""Data type handlers for unified CRUD operations."""

from __future__ import annotations

from .annotation_handler import AnnotationHandler
from .brush_handler import BrushHandler
from .cachefile_handler import CacheFileHandler
from .collection_handler import CollectionHandler
from .context_handler import ContextHandler
from .core_handlers import (
    ArmatureHandler,
    CameraHandler,
    CurveHandler,
    FontHandler,
    GreasePencilHandler,
    LightHandler,
    MetaBallHandler,
    TextHandler,
    WorldHandler,
)
from .curves_new_handler import CurvesNewHandler
from .image_handler import ImageHandler
from .key_handler import KeyHandler
from .lattice_handler import LatticeHandler
from .library_handler import LibraryHandler
from .light_probe_handler import LightProbeHandler
from .mask_handler import MaskHandler
from .material_handler import MaterialHandler
from .mesh_handler import MeshHandler
from .modifier_handler import ModifierHandler
from .movieclip_handler import MovieClipHandler
from .node_tree_handler import NodeTreeHandler
from .object_handler import ObjectHandler
from .paintcurve_handler import PaintCurveHandler
from .palette_handler import PaletteHandler
from .scene_handler import SceneHandler
from .sound_handler import SoundHandler
from .speaker_handler import SpeakerHandler
from .surface_handler import SurfaceHandler
from .texture_handler import TextureHandler
from .volume_handler import VolumeHandler
from .workspace_handler import WorkspaceHandler

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
    "TextureHandler",
    "BrushHandler",
    "WorkspaceHandler",
    "SoundHandler",
    "VolumeHandler",
    "MovieClipHandler",
    "MaskHandler",
    "LightProbeHandler",
    "LatticeHandler",
    "SurfaceHandler",
    "SpeakerHandler",
    "CacheFileHandler",
    "PaletteHandler",
    "PaintCurveHandler",
    "AnnotationHandler",
    "CurvesNewHandler",
    "KeyHandler",
    "LibraryHandler",
]
