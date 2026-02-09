# -*- coding: utf-8 -*-
"""Extended tests for security guardrails."""
from __future__ import annotations

import unittest

from blender_mcp.security.guardrails import Guardrails


class TestGuardrailsExtended(unittest.TestCase):
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
