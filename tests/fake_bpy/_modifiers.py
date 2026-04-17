# -*- coding: utf-8 -*-
"""Fake modifier data structures."""

from __future__ import annotations

from typing import Any


class FakeModifier:
    def __init__(self, name: str, modifier_type: str = "SUBSURF") -> None:
        self.name = name
        self.type = modifier_type
        self.show_viewport = True
        self.show_render = True
        self.show_in_editmode = False
        self.show_on_cage = False
        self.show_expanded = True
        self.is_active = True

        # Common modifier properties
        self.vertex_group = ""
        self.invert_vertex_group = False

        # Subdivision Surface
        self.levels = 1
        self.render_levels = 2
        self.quality = 3
        self.subdivision_type = "CATMULL_CLARK"
        self.use_limit_surface = True
        self.limit_surface = 5

        # Mirror
        self.use_x = True
        self.use_y = False
        self.use_z = False
        self.use_mirror_vertex_groups = True
        self.use_clip = False
        self.mirror_object = None
        self.offset_u = 0.0
        self.offset_v = 0.0
        self.use_axis = [True, False, False]
        self.use_bisect_axis = [False, False, False]
        self.use_bisect_flip_axis = [False, False, False]

        # Array
        self.count = 3
        self.fit_type = "FIXED_COUNT"
        self.use_constant_offset = False
        self.constant_offset_displace = [1.0, 0.0, 0.0]
        self.use_relative_offset = True
        self.relative_offset_displace = [1.0, 0.0, 0.0]
        self.use_object_offset = False
        self.offset_object = None
        self.start_cap = None
        self.end_cap = None

        # Boolean
        self.operation = "DIFFERENCE"
        self.solver = "FAST"
        self.object = None
        self.double_threshold = 0.001
        self.use_self = False
        self.use_hole_tolerant = False

        # Bevel
        self.width = 0.1
        self.segments = 2
        self.profile = 0.5
        self.material = -1
        self.limit_method = "NONE"
        self.edge_weight_method = "EVEN"
        self.miter_outer = "SHARP"
        self.miter_inner = "SHARP"
        self.spread = 0.1
        self.use_clamp_overlap = True
        self.vertex_group = ""

        # Solidify
        self.thickness = 0.01
        self.offset = -1.0
        self.thickness_vertex_group = 1.0
        self.invert_vertex_group = False
        self.use_even_offset = False
        self.use_quality_normals = True
        self.use_rim = True
        self.rim_thickness = 0.01

        # Cloth
        self.settings: Any = None
        self.collision_settings: Any = None

        # Soft Body
        self.point_cache: Any = None

        # Decimate
        self.decimate_type = "COLLAPSE"
        self.ratio = 1.0
        self.use_collapse_triangulate = False
        self.iterations = 0

    def __repr__(self) -> str:
        return f"<FakeModifier '{self.name}' ({self.type})>"


class FakeModifierCollection:
    def __init__(self) -> None:
        self._modifiers: list[FakeModifier] = []

    def new(self, name: str, modifier_type: str) -> FakeModifier:
        mod = FakeModifier(name, modifier_type)
        self._modifiers.append(mod)
        return mod

    def get(self, name: str) -> FakeModifier | None:
        for mod in self._modifiers:
            if mod.name == name:
                return mod
        return None

    def remove(self, modifier: FakeModifier) -> None:
        if modifier in self._modifiers:
            self._modifiers.remove(modifier)

    def __iter__(self):
        return iter(self._modifiers)

    def __len__(self) -> int:
        return len(self._modifiers)

    def __getitem__(self, index: int) -> FakeModifier:
        return self._modifiers[index]
