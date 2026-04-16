# -*- coding: utf-8 -*-
"""Tests for prompts/registry.py."""

from __future__ import annotations

import unittest

from blender_mcp.prompts.registry import (
    _PROMPT_HANDLERS,
    BLENDER_PROMPTS,
    get_prompt,
    get_prompt_messages,
    list_prompts,
)


class TestPromptsRegistry(unittest.TestCase):
    def test_blender_prompts_has_10_prompts(self):
        self.assertEqual(len(BLENDER_PROMPTS), 10)

    def test_all_prompts_have_required_fields(self):
        for name, prompt in BLENDER_PROMPTS.items():
            self.assertIn("name", prompt)
            self.assertIn("title", prompt)
            self.assertIn("description", prompt)
            self.assertIn("arguments", prompt)
            self.assertEqual(prompt["name"], name)

    def test_get_prompt_existing(self):
        prompt = get_prompt("blender-scene-setup")
        self.assertIsNotNone(prompt)
        self.assertEqual(prompt["name"], "blender-scene-setup")
        self.assertEqual(prompt["title"], "Set Up Blender Scene")

    def test_get_prompt_not_found(self):
        prompt = get_prompt("nonexistent-prompt")
        self.assertIsNone(prompt)

    def test_list_prompts_returns_all(self):
        prompts = list_prompts()
        self.assertEqual(len(prompts), 10)
        names = {p["name"] for p in prompts}
        expected = {
            "blender-scene-setup",
            "blender-material-create",
            "blender-model-asset",
            "blender-animate",
            "blender-composite",
            "blender-render-output",
            "blender-diagnose",
            "blender-usage-strategy",
            "blender-resource-strategy",
            "blender-debugging-strategy",
        }
        self.assertEqual(names, expected)

    def test_prompt_handlers_exist_for_all_prompts(self):
        for name in BLENDER_PROMPTS:
            self.assertIn(name, _PROMPT_HANDLERS, f"Missing handler for {name}")

    def test_get_prompt_messages_existing(self):
        result = get_prompt_messages("blender-scene-setup", {"style": "realistic"})
        self.assertIsNotNone(result)
        self.assertIn("messages", result)
        self.assertIn("description", result)
        self.assertEqual(len(result["messages"]), 1)
        self.assertEqual(result["messages"][0]["role"], "user")

    def test_get_prompt_messages_with_arguments(self):
        result = get_prompt_messages(
            "blender-material-create",
            {"material_type": "metal", "target_object": "Cube"},
        )
        self.assertIsNotNone(result)
        content = result["messages"][0]["content"]["text"]
        self.assertIn("metal", content)
        self.assertIn("Cube", content)

    def test_get_prompt_messages_no_arguments(self):
        result = get_prompt_messages("blender-diagnose", None)
        self.assertIsNotNone(result)
        self.assertIn("messages", result)

    def test_get_prompt_messages_empty_arguments(self):
        result = get_prompt_messages("blender-diagnose", {})
        self.assertIsNotNone(result)
        self.assertIn("messages", result)

    def test_get_prompt_messages_unknown_prompt(self):
        result = get_prompt_messages("unknown-prompt", {})
        self.assertIsNone(result)

    def test_scene_setup_uses_args(self):
        result = get_prompt_messages(
            "blender-scene-setup",
            {"style": "stylized", "resolution": "4K"},
        )
        content = result["messages"][0]["content"]["text"]
        self.assertIn("stylized", content)
        self.assertIn("4K", content)

    def test_scene_setup_defaults(self):
        result = get_prompt_messages("blender-scene-setup", {})
        content = result["messages"][0]["content"]["text"]
        self.assertIn("realistic", content)
        self.assertIn("1080p", content)

    def test_material_create_defaults(self):
        result = get_prompt_messages("blender-material-create", {})
        content = result["messages"][0]["content"]["text"]
        self.assertIn("custom", content)

    def test_model_asset_uses_args(self):
        result = get_prompt_messages(
            "blender-model-asset",
            {"description": "a chair", "complexity": "simple"},
        )
        content = result["messages"][0]["content"]["text"]
        self.assertIn("simple", content)
        self.assertIn("a chair", content)

    def test_animate_uses_args(self):
        result = get_prompt_messages(
            "blender-animate",
            {"animation_type": "camera", "target": "Camera.001"},
        )
        content = result["messages"][0]["content"]["text"]
        self.assertIn("camera", content)
        self.assertIn("Camera.001", content)

    def test_composite_uses_args(self):
        result = get_prompt_messages("blender-composite", {"effects": "glow"})
        content = result["messages"][0]["content"]["text"]
        self.assertIn("glow", content)

    def test_render_output_uses_args(self):
        result = get_prompt_messages("blender-render-output", {"output_type": "animation"})
        content = result["messages"][0]["content"]["text"]
        self.assertIn("animation", content)

    def test_strategy_prompts_no_args(self):
        for name in [
            "blender-usage-strategy",
            "blender-resource-strategy",
            "blender-debugging-strategy",
        ]:
            result = get_prompt_messages(name, {})
            self.assertIsNotNone(result)
            self.assertIn("messages", result)
            self.assertEqual(len(result["messages"]), 1)


if __name__ == "__main__":
    unittest.main()
