# -*- coding: utf-8 -*-
from __future__ import annotations

import unittest

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_mcp.security.guardrails import Guardrails


class TestGuardrails(unittest.TestCase):
    def test_blocks_payload_size(self) -> None:
        guardrails = Guardrails.from_limits(max_payload_bytes=1)
        self.assertFalse(guardrails.allow("blender.get_scene", {"data": "xx"}))

    def test_blocks_payload_keys(self) -> None:
        guardrails = Guardrails.from_limits(max_payload_keys=0)
        self.assertFalse(guardrails.allow("blender.get_scene", {"a": 1}))

    def test_blocks_capability(self) -> None:
        guardrails = Guardrails.from_limits(blocked_capabilities=["blender.modify_object"])
        self.assertFalse(guardrails.allow("blender.modify_object", {}))


if __name__ == "__main__":
    unittest.main()
