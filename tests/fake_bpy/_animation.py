# -*- coding: utf-8 -*-
"""Fake animation data structures with version-aware API."""

from __future__ import annotations

from typing import Any


class FakeKeyframePoint:
    def __init__(self, co: tuple[float, float] = (0.0, 0.0)) -> None:
        self.co = list(co)
        self.interpolation = "BEZIER"
        self.handle_left = [co[0] - 1.0, co[1]]
        self.handle_right = [co[0] + 1.0, co[1]]


class FakeKeyframePoints:
    def __init__(self) -> None:
        self._points: list[FakeKeyframePoint] = []

    def add(self, count: int) -> None:
        for _ in range(count):
            self._points.append(FakeKeyframePoint())

    def insert(self, frame: float, value: float) -> FakeKeyframePoint:
        kp = FakeKeyframePoint((frame, value))
        self._points.append(kp)
        return kp

    def remove(self, point: FakeKeyframePoint) -> None:
        if point in self._points:
            self._points.remove(point)

    def __iter__(self):
        return iter(self._points)

    def __len__(self) -> int:
        return len(self._points)

    def __getitem__(self, index: int) -> FakeKeyframePoint:
        return self._points[index]


class FakeFCurve:
    def __init__(self, data_path: str = "", array_index: int = 0) -> None:
        self.data_path = data_path
        self.array_index = array_index
        self.keyframe_points = FakeKeyframePoints()
        self.group = None
        self.color = [0.0, 0.0, 0.0]
        self.lock = False
        self.mute = False
        self.hide = False
        self.driver = None
        self.is_valid = True

    def evaluate(self, frame: float) -> float:
        if len(self.keyframe_points) == 0:
            return 0.0
        return self.keyframe_points[-1].co[1]


class FakeFCurveCollection:
    """Collection of FCurves with find() method support."""

    def __init__(self) -> None:
        self._curves: list[FakeFCurve] = []

    def new(self, data_path: str, index: int = 0) -> FakeFCurve:
        fc = FakeFCurve(data_path, index)
        self._curves.append(fc)
        return fc

    def find(self, data_path: str, index: int = -1) -> FakeFCurve | None:
        for fc in self._curves:
            if fc.data_path == data_path:
                if index == -1 or fc.array_index == index:
                    return fc
        return None

    def remove(self, fcurve: FakeFCurve) -> None:
        if fcurve in self._curves:
            self._curves.remove(fcurve)

    def __iter__(self):
        return iter(self._curves)

    def __len__(self) -> int:
        return len(self._curves)

    def __getitem__(self, index: int) -> FakeFCurve:
        return self._curves[index]


class FakeAnimationChannelbag:
    """Blender 5.0+ channelbag containing FCurves."""

    def __init__(self) -> None:
        self.fcurves = FakeFCurveCollection()


class FakeAnimationStrip:
    """Blender 5.0+ animation strip."""

    def __init__(self) -> None:
        self.channelbags: list[FakeAnimationChannelbag] = [FakeAnimationChannelbag()]
        self.name = "Strip"
        self.frame_start = 0
        self.frame_end = 100


class FakeAnimationLayer:
    """Blender 5.0+ animation layer."""

    def __init__(self) -> None:
        self.strips: list[FakeAnimationStrip] = [FakeAnimationStrip()]
        self.name = "Layer"


class FakeAction:
    """Fake action with version-aware API (legacy vs layered)."""

    def __init__(self, name: str = "Action", version: tuple[int, ...] = (4, 2, 0)) -> None:
        self.name = name
        self._version = version
        self.users = 1
        self.use_fake_user = False

        if version >= (5, 0):
            self.layers: list[FakeAnimationLayer] = [FakeAnimationLayer()]
        else:
            self.fcurves = FakeFCurveCollection()

    def __repr__(self) -> str:
        return f"<FakeAction '{self.name}'>"


class FakeDriver:
    def __init__(self) -> None:
        self.expression = ""
        self.type = "AVERAGE"
        self.variables: list[Any] = []

    def evaluate(self) -> float:
        return 0.0


class FakeNlaStrip:
    def __init__(self, name: str = "Strip") -> None:
        self.name = name
        self.frame_start = 0
        self.frame_end = 100
        self.action = None
        self.blend_in = 0.0
        self.blend_out = 0.0
        self.influence = 1.0
        self.mute = False


class FakeNlaTrack:
    def __init__(self, name: str = "Track") -> None:
        self.name = name
        self.strips: list[FakeNlaStrip] = []
        self.mute = False
        self.lock = False
        self.is_solo = False

    def strips_new(self, name: str, start: int, action: FakeAction) -> FakeNlaStrip:
        strip = FakeNlaStrip(name)
        strip.frame_start = start
        strip.action = action
        self.strips.append(strip)
        return strip


class FakeAnimationData:
    def __init__(self, version: tuple[int, ...] = (4, 2, 0)) -> None:
        self.action: FakeAction | None = None
        self.nla_tracks: list[FakeNlaTrack] = []
        self.drivers: list[FakeDriver] = []
        self._version = version

    def nla_tracks_new(self) -> FakeNlaTrack:
        track = FakeNlaTrack()
        self.nla_tracks.append(track)
        return track

    def action_create(self) -> FakeAction:
        self.action = FakeAction(version=self._version)
        return self.action
