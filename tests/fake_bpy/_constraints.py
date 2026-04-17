# -*- coding: utf-8 -*-
"""Fake constraint data structures."""

from __future__ import annotations

from typing import Any


class FakeConstraint:
    def __init__(self, name: str, constraint_type: str = "COPY_LOCATION") -> None:
        self.name = name
        self.type = constraint_type
        self.owner: Any = None
        self.is_valid = True
        self.is_proxy_local = False
        self.show_expanded = True
        self.use_custom_tolerance = False
        self.influence = 1.0
        self.enabled = True

        # Target properties
        self.target: Any = None
        self.subtarget = ""
        self.owner_space = "WORLD"
        self.target_space = "WORLD"

        # Copy Location
        self.use_x = True
        self.use_y = True
        self.use_z = True
        self.invert_x = False
        self.invert_y = False
        self.invert_z = False
        self.offset = [0.0, 0.0, 0.0]

        # Copy Rotation
        self.rotation_mode = "EULER"
        self.euler_order = "AUTO"
        self.invert_x = False
        self.invert_y = False
        self.invert_z = False

        # Track To
        self.track_axis = "TRACK_NEGATIVE_Z"
        self.up_axis = "UP_Y"
        self.use_target_z = False

        # IK
        self.chain_count = 2
        self.use_tail = False
        self.use_rotation = False
        self.use_stretch = True
        self.pole_target: Any = None
        self.pole_subtarget = ""
        self.pole_angle = 0.0
        self.iterations = 500
        self.dist = 0.0

        # Limit Distance
        self.distance = 0.0
        self.limit_mode = "LIMITDIST_ONSURFACE"
        self.target: Any = None

        # Follow Path
        self.use_curve_follow = False
        self.use_curve_radius = True
        self.use_fixed_location = True
        self.offset_factor = 0.0
        self.offset = 0
        self.forward_axis = "FORWARD_X"
        self.up_axis = "UP_Z"

        # Stretch To
        self.volume = "VOLUME_XZ"
        self.volume_variation = 1.0
        self.rest_length = 0.0
        self.bulge = 0.0
        self.bulge_min = 0.0
        self.bulge_max = 0.0
        self.use_bulge_min = False
        self.use_bulge_max = False

    def __repr__(self) -> str:
        return f"<FakeConstraint '{self.name}' ({self.type})>"


class FakeConstraintCollection:
    def __init__(self, owner: Any = None) -> None:
        self._constraints: list[FakeConstraint] = []
        self._owner = owner

    def new(self, name: str, constraint_type: str) -> FakeConstraint:
        con = FakeConstraint(name, constraint_type)
        con.owner = self._owner
        self._constraints.append(con)
        return con

    def get(self, name: str) -> FakeConstraint | None:
        for con in self._constraints:
            if con.name == name:
                return con
        return None

    def remove(self, constraint: FakeConstraint) -> None:
        if constraint in self._constraints:
            self._constraints.remove(constraint)

    def move(self, from_index: int, to_index: int) -> None:
        if 0 <= from_index < len(self._constraints) and 0 <= to_index < len(self._constraints):
            con = self._constraints.pop(from_index)
            self._constraints.insert(to_index, con)

    def __iter__(self):
        return iter(self._constraints)

    def __len__(self) -> int:
        return len(self._constraints)

    def __getitem__(self, index: int) -> FakeConstraint:
        return self._constraints[index]
