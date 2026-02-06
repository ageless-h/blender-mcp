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
from .texture_handler import TextureHandler
from .brush_handler import BrushHandler
from .workspace_handler import WorkspaceHandler
from .sound_handler import SoundHandler
from .volume_handler import VolumeHandler
from .movieclip_handler import MovieClipHandler
from .mask_handler import MaskHandler
from .light_probe_handler import LightProbeHandler
from .lattice_handler import LatticeHandler
from .surface_handler import SurfaceHandler
from .speaker_handler import SpeakerHandler
from .cachefile_handler import CacheFileHandler
from .palette_handler import PaletteHandler
from .paintcurve_handler import PaintCurveHandler
from .annotation_handler import AnnotationHandler
from .curves_new_handler import CurvesNewHandler
from .key_handler import KeyHandler
from .library_handler import LibraryHandler

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
