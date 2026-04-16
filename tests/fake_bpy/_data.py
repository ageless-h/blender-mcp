# -*- coding: utf-8 -*-
"""Fake bpy.data — simulated Blender data collections."""

from __future__ import annotations

from typing import Any


class _FakeDataBlock:
    """A single named data block (e.g., an object, mesh, material)."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.users = 1
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return f"<_FakeDataBlock '{self.name}'>"


class _FakeCollection:
    """A named collection of data blocks (e.g., bpy.data.objects)."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._items: dict[str, _FakeDataBlock] = {}

    def new(self, name: str, **kwargs: Any) -> _FakeDataBlock:
        item = _FakeDataBlock(name, **kwargs)
        self._items[name] = item
        return item

    def get(self, name: str) -> _FakeDataBlock | None:
        return self._items.get(name)

    def remove(self, item: _FakeDataBlock) -> None:
        self._items.pop(item.name, None)

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, name: str) -> bool:
        return name in self._items

    def __repr__(self) -> str:
        return f"<_FakeCollection '{self._name}' [{len(self._items)} items]>"


class _FakeCurvesCollection(_FakeCollection):
    """Blender 5.0+ curves collection. Only present when simulated version >= 5.0."""

    def __init__(self, name: str = "curves") -> None:
        super().__init__(name)


class FakeData:
    """Fake bpy.data with standard Blender data collections."""

    def __init__(self, blender_version: tuple[int, ...] = (4, 2, 0)) -> None:
        self._blender_version = blender_version
        self.objects = _FakeCollection("objects")
        self.meshes = _FakeCollection("meshes")
        self.curves = _FakeCollection("curves")
        self.materials = _FakeCollection("materials")
        self.textures = _FakeCollection("textures")
        self.images = _FakeCollection("images")
        self.lights = _FakeCollection("lights")
        self.cameras = _FakeCollection("cameras")
        self.armatures = _FakeCollection("armatures")
        self.actions = _FakeCollection("actions")
        self.node_groups = _FakeCollection("node_groups")
        self.collections = _FakeCollection("collections")
        self.scenes = _FakeCollection("scenes")
        self.worlds = _FakeCollection("worlds")
        self.sounds = _FakeCollection("sounds")
        self.texts = _FakeCollection("texts")
        self.fonts = _FakeCollection("fonts")
        self.lattices = _FakeCollection("lattices")
        self.metaballs = _FakeCollection("metaballs")
        self.grease_pencils = _FakeCollection("grease_pencils")
        self.movieclips = _FakeCollection("movieclips")
        self.masks = _FakeCollection("masks")
        self.brushes = _FakeCollection("brushes")
        self.palettes = _FakeCollection("palettes")
        self.paintcurves = _FakeCollection("paintcurves")
        self.workspaces = _FakeCollection("workspaces")
        self.libraries = _FakeCollection("libraries")
        self.shape_keys = _FakeCollection("shape_keys")
        self.lights_probe = _FakeCollection("light_probes")
        self.speakers = _FakeCollection("speakers")
        self.volumes = _FakeCollection("volumes")
        self.cachefiles = _FakeCollection("cachefiles")

        self._curves_new: _FakeCurvesCollection | None = None
        if blender_version >= (5, 0):
            self._curves_new = _FakeCurvesCollection()
            self.curves_new = self._curves_new

    @property
    def version(self) -> tuple[int, ...]:
        return self._blender_version
