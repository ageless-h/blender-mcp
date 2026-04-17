# -*- coding: utf-8 -*-
"""Tests for prompts/registry.py."""

from __future__ import annotations

import unittest

from blender_mcp.prompts.registry import (
    BLENDER_PROMPTS,
    get_prompt,
    get_prompt_messages,
    list_prompts,
)


class TestPromptsRegistry(unittest.TestCase):
    def test_blender_prompts_is_empty(self):
        self.assertEqual(len(BLENDER_PROMPTS), 0)

    def test_get_prompt_returns_none(self):
        self.assertIsNone(get_prompt("blender-scene-setup"))
        self.assertIsNone(get_prompt("nonexistent-prompt"))

    def test_list_prompts_returns_empty(self):
        prompts = list_prompts()
        self.assertEqual(len(prompts), 0)

    def test_get_prompt_messages_returns_none(self):
        self.assertIsNone(get_prompt_messages("blender-scene-setup", {"style": "realistic"}))
        self.assertIsNone(get_prompt_messages("unknown-prompt", {}))
        self.assertIsNone(get_prompt_messages("blender-diagnose", None))


if __name__ == "__main__":
    unittest.main()
