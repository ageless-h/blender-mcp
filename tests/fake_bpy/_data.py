# -*- coding: utf-8 -*-
"""Fake bpy.data — simulated Blender data collections."""

from __future__ import annotations

from typing import Any


class _FakeDataBlock:
    """A single named data block (e.g., an object, mesh, material)."""

    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name
        self.users = 1
        self.type = kwargs.get("type", "MESH")
        self.mode = kwargs.get("mode", "OBJECT")
        self.constraints: list[_FakeConstraint] = []
        self.modifiers: list[_FakeModifier] = []
        self.rigid_body: _FakeRigidBody | None = None
        self.particle_systems: list[Any] = []
        self.field: _FakeField | None = None
        self.pose: Any = None
        self.data: Any = kwargs.get("data")
        for k, v in kwargs.items():
            if k not in ("type", "mode", "data"):
                setattr(self, k, v)

    def __repr__(self) -> str:
        return f"<_FakeDataBlock '{self.name}'>"


class _FakeConstraint:
    """A fake constraint for testing."""

    def __init__(self, constraint_type: str, name: str) -> None:
        self.type = constraint_type
        self.name = name
        self.mute = False
        self.target: Any = None
        self.subtarget = ""
        self.influence = 1.0
        self.use_x = True
        self.use_y = True
        self.use_z = True
        self.use_offset = False
        self.invert_x = False
        self.invert_y = False
        self.invert_z = False
        self.track_axis = "TRACK_NEGATIVE_Z"
        self.up_axis = "UP_Y"
        self.use_target_z = False
        self.pole_target: Any = None
        self.pole_subtarget = ""
        self.pole_angle = 0.0
        self.chain_count = 2
        self.use_tail = False
        self.use_stretch = True
        self.iterations = 500


class _FakeConstraintsCollection:
    """A collection of constraints on an object."""

    def __init__(self) -> None:
        self._items: list[_FakeConstraint] = []

    def new(self, type: str) -> _FakeConstraint:
        c = _FakeConstraint(type, type)
        self._items.append(c)
        return c

    def get(self, name: str) -> _FakeConstraint | None:
        for c in self._items:
            if c.name == name:
                return c
        return None

    def remove(self, constraint: _FakeConstraint) -> None:
        self._items = [c for c in self._items if c is not constraint]

    def __iter__(self):
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)


class _FakeModifier:
    """A fake modifier for testing."""

    def __init__(self, modifier_type: str, name: str) -> None:
        self.type = modifier_type
        self.name = name
        self.show_viewport = True
        self.show_render = True
        self.show_in_editmode = False
        self.levels = 1
        self.render_levels = 2
        self.count = 1
        self.use_relative_offset = True
        self.use_axis = [True, False, False]
        self.operation = "DIFFERENCE"
        self.object: Any = None
        self.thickness = 0.01
        self.offset = -1.0
        self.width = 0.1
        self.segments = 1
        self.settings: Any = None


class _FakeModifiersCollection:
    """A collection of modifiers on an object."""

    def __init__(self) -> None:
        self._items: list[_FakeModifier] = []

    def new(self, name: str, type: str) -> _FakeModifier:
        m = _FakeModifier(type, name)
        self._items.append(m)
        return m

    def get(self, name: str) -> _FakeModifier | None:
        for m in self._items:
            if m.name == name:
                return m
        return None

    def remove(self, modifier: _FakeModifier) -> None:
        self._items = [m for m in self._items if m is not modifier]

    def __iter__(self):
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    @property
    def active(self) -> _FakeModifier | None:
        return self._items[0] if self._items else None


class _FakeRigidBody:
    """A fake rigid body for testing."""

    def __init__(self) -> None:
        self.type = "ACTIVE"
        self.mass = 1.0
        self.friction = 0.5
        self.restitution = 0.0
        self.use_margin = False
        self.collision_margin = 0.0
        self.collision_shape = "BOX"
        self.use_deactivation = True
        self.angular_damping = 0.1
        self.linear_damping = 0.04


class _FakeField:
    """A fake force field for testing."""

    def __init__(self) -> None:
        self.type = "NONE"
        self.strength = 1.0
        self.falloff_type = "SPHERE"
        self.falloff_power = 2.0
        self.use_max_distance = False
        self.distance_max = 0.0
        self.use_min_distance = False
        self.distance_min = 0.0
        self.flow = 0.0
        self.noise_amount = 0.0


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


class _FakeObjectsCollection(_FakeCollection):
    """Objects collection with automatic constraints/modifiers setup."""

    def __init__(self) -> None:
        super().__init__("objects")

    def new(self, name: str, **kwargs: Any) -> _FakeDataBlock:
        obj = _FakeDataBlock(name, **kwargs)
        obj.constraints = _FakeConstraintsCollection()
        obj.modifiers = _FakeModifiersCollection()
        obj.rigid_body = None
        obj.particle_systems = []
        obj.field = _FakeField()
        obj.pose = None
        obj.select_set = lambda v: None
        self._items[name] = obj
        return obj


class _FakeCurvesCollection(_FakeCollection):
    """Blender 5.0+ curves collection. Only present when simulated version >= 5.0."""

    def __init__(self, name: str = "curves") -> None:
        super().__init__(name)


class FakeData:
    """Fake bpy.data with standard Blender data collections."""

    def __init__(self, blender_version: tuple[int, ...] = (4, 2, 0)) -> None:
        self._blender_version = blender_version
        self.objects = _FakeObjectsCollection()
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
