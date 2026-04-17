# -*- coding: utf-8 -*-
"""Fake VSE (Video Sequence Editor) data structures."""

from __future__ import annotations

from typing import Any


class FakeStrip:
    def __init__(self, name: str = "Strip") -> None:
        self.name = name
        self.channel = 1
        self.frame_start = 0
        self.frame_final_start = 0
        self.frame_final_end = 100
        self.frame_duration = 100
        self.type = "MOVIE"
        self.mute = False
        self.lock = False
        self.select = False
        self.blend_type = "REPLACE"
        self.blend_alpha = 1.0
        self.color = [1.0, 1.0, 1.0, 1.0]
        self.color_saturation = 1.0
        self.color_multiply = 1.0
        self.strobe = 0.0
        self.use_translation = False
        self.transform: dict[str, Any] = {"offset_x": 0, "offset_y": 0, "scale_x": 1.0, "scale_y": 1.0, "rotation": 0.0}


class FakeSequenceCollection:
    def __init__(self) -> None:
        self._strips: dict[str, FakeStrip] = {}

    def new_movie(self, name: str, filepath: str, channel: int, frame_start: int) -> FakeStrip:
        strip = FakeStrip(name)
        strip.type = "MOVIE"
        strip.channel = channel
        strip.frame_start = frame_start
        strip.frame_final_start = frame_start
        strip.frame_final_end = frame_start + 100
        self._strips[name] = strip
        return strip

    def new_image(self, name: str, filepath: str, channel: int, frame_start: int) -> FakeStrip:
        strip = FakeStrip(name)
        strip.type = "IMAGE"
        strip.channel = channel
        strip.frame_start = frame_start
        self._strips[name] = strip
        return strip

    def new_sound(self, name: str, filepath: str, channel: int, frame_start: int) -> FakeStrip:
        strip = FakeStrip(name)
        strip.type = "SOUND"
        strip.channel = channel
        strip.frame_start = frame_start
        self._strips[name] = strip
        return strip

    def new_effect(
        self, name: str, type: str, channel: int, frame_start: int, frame_end: int = None, **kwargs
    ) -> FakeStrip:
        strip = FakeStrip(name)
        strip.type = type
        strip.channel = channel
        strip.frame_start = frame_start
        if frame_end:
            strip.frame_final_end = frame_end
        for k, v in kwargs.items():
            setattr(strip, k, v)
        self._strips[name] = strip
        return strip

    def get(self, name: str) -> FakeStrip | None:
        return self._strips.get(name)

    def remove(self, strip: FakeStrip) -> None:
        self._strips.pop(strip.name, None)

    def __iter__(self):
        return iter(self._strips.values())

    def __len__(self) -> int:
        return len(self._strips)

    def __getitem__(self, name: str) -> FakeStrip:
        return self._strips[name]


class FakeSequenceEditor:
    def __init__(self) -> None:
        self.sequences = FakeSequenceCollection()
        self.sequences_all = self.sequences
        self.meta_stack: list[Any] = []
        self.display_stack: list[Any] = []
        self.overlay_frame = 0
        self.show_overlay = False
        self.use_overlay_lock = False
        self.cache_raw = True
        self.cache_preprocessed = True
        self.cache_composite = True
        self.cache_final = True

    def __repr__(self) -> str:
        return f"<FakeSequenceEditor [{len(self.sequences)} strips]>"
