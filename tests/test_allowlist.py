# -*- coding: utf-8 -*-
"""Tests for security allowlist."""
from __future__ import annotations

import unittest

from blender_mcp.security.allowlist import Allowlist, DEFAULT_ALLOWED_TOOLS


class TestAllowlist(unittest.TestCase):
    def test_default_allowed(self):
        al = Allowlist()
        for t in DEFAULT_ALLOWED_TOOLS:
            self.assertTrue(al.is_allowed(t))

    def test_script_blocked(self):
        self.assertFalse(Allowlist().is_allowed("blender.execute_script"))

    def test_enable_script(self):
        al = Allowlist()
        al.enable_script_execute()
        self.assertTrue(al.is_allowed("blender.execute_script"))
        al.disable_script_execute()
        self.assertFalse(al.is_allowed("blender.execute_script"))

    def test_add_remove(self):
        al = Allowlist()
        al.add_tool("custom.x")
        self.assertTrue(al.is_allowed("custom.x"))
        al.remove_tool("custom.x")
        self.assertFalse(al.is_allowed("custom.x"))

    def test_add_dangerous_rejected(self):
        self.assertFalse(Allowlist().add_tool("blender.execute_script"))

    def test_replace_filters_dangerous(self):
        al = Allowlist()
        al.replace(["blender.get_objects", "blender.execute_script"])
        self.assertTrue(al.is_allowed("blender.get_objects"))
        self.assertFalse(al.is_allowed("blender.execute_script"))


if __name__ == "__main__":
    unittest.main()
