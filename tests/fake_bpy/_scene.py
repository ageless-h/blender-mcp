# -*- coding: utf-8 -*-
"""Fake scene and render settings for testing."""

from __future__ import annotations

from typing import Any

from ._sequencer import FakeSequenceEditor


class FakeImageSettings:
    def __init__(self) -> None:
        self.file_format = "PNG"
        self.color_mode = "RGBA"
        self.color_depth = "8"
        self.compression = 15


class FakeRenderSettings:
    def __init__(self) -> None:
        self.engine = "BLENDER_EEVEE"
        self.fps = 24
        self.fps_base = 1.0
        self.resolution_x = 1920
        self.resolution_y = 1080
        self.resolution_percentage = 100
        self.pixel_aspect_x = 1.0
        self.pixel_aspect_y = 1.0
        self.filepath = "/tmp/render"
        self.film_transparent = False
        self.image_settings = FakeImageSettings()
        self.use_sequencer = True
        self.use_compositing = True


class FakeRigidBodyWorld:
    def __init__(self) -> None:
        self.time_scale = 1.0
        self.use_split_impulse = False
        self.collection = None
        self.point_cache = None


class FakeDependencyGraph:
    def __init__(self) -> None:
        pass

    def update(self, *args, **kwargs) -> None:
        pass


class FakeCollection:
    def __init__(self, name: str = "Collection") -> None:
        self.name = name
        self.objects: list[Any] = []
        self.children: list[Any] = []

    def link(self, obj: Any) -> None:
        if obj not in self.objects:
            self.objects.append(obj)

    def unlink(self, obj: Any) -> None:
        if obj in self.objects:
            self.objects.remove(obj)


class FakeScene:
    def __init__(self, name: str = "Scene") -> None:
        self.name = name
        self.frame_start = 1
        self.frame_end = 250
        self.frame_current = 1
        self.render = FakeRenderSettings()
        self.world = None
        self.sequence_editor = None
        self.collection = FakeCollection()
        self.rigidbody_world: FakeRigidBodyWorld | None = None
        self.use_nodes = False
        self.camera = None
        self.tool_settings = None
        self.view_layers: list[Any] = []
        self.depsgraph = FakeDependencyGraph()

    def frame_set(self, frame: int, subframe: float = 0.0) -> None:
        self.frame_current = frame

    def update(self, *args, **kwargs) -> None:
        pass

    def sequence_editor_create(self) -> Any:
        if self.sequence_editor is None:
            self.sequence_editor = FakeSequenceEditor()
        return self.sequence_editor
