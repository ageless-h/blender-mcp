# -*- coding: utf-8 -*-
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from blender_mcp.security.allowlist import Allowlist, DEFAULT_ALLOWED_TOOLS


class TestAllowlist(unittest.TestCase):
    def test_default_allowed(self):
        al = Allowlist()
        for t in DEFAULT_ALLOWED_TOOLS:
            self.assertTrue(al.is_allowed(t))

    def test_script_blocked(self):
        self.assertFalse(Allowlist().is_allowed("script.execute"))

    def test_enable_script(self):
        al = Allowlist()
        al.enable_script_execute()
        self.assertTrue(al.is_allowed("script.execute"))
        al.disable_script_execute()
        self.assertFalse(al.is_allowed("script.execute"))

    def test_add_remove(self):
        al = Allowlist()
        al.add_tool("custom.x")
        self.assertTrue(al.is_allowed("custom.x"))
        al.remove_tool("custom.x")
        self.assertFalse(al.is_allowed("custom.x"))

    def test_add_dangerous_rejected(self):
        self.assertFalse(Allowlist().add_tool("script.execute"))

    def test_replace_filters_dangerous(self):
        al = Allowlist()
        al.replace(["data.read", "script.execute"])
        self.assertTrue(al.is_allowed("data.read"))
        self.assertFalse(al.is_allowed("script.execute"))


if __name__ == "__main__":
    unittest.main()
