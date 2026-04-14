# -*- coding: utf-8 -*-
"""Tests for security guardrails — payload limits, nesting, serialization."""

from __future__ import annotations

import unittest

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

    def test_nesting_depth_rejected(self):
        g = Guardrails(max_nesting_depth=2)
        deep = {"a": {"b": {"c": {"d": 1}}}}
        self.assertFalse(g.allow("x", deep))

    def test_nesting_depth_ok(self):
        g = Guardrails(max_nesting_depth=5)
        shallow = {"a": {"b": 1}}
        self.assertTrue(g.allow("x", shallow))

    def test_unserializable_rejected(self):
        g = Guardrails()
        self.assertFalse(g.allow("x", {"bad": object()}))

    def test_from_env_defaults(self):
        g = Guardrails.from_env()
        self.assertEqual(g.max_payload_bytes, 65536)
        self.assertEqual(g.max_payload_keys, 128)

    def test_empty_payload_allowed(self):
        g = Guardrails()
        self.assertTrue(g.allow("blender.get_object_data", {}))


if __name__ == "__main__":
    unittest.main()
