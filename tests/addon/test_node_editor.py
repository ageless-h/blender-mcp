# -*- coding: utf-8 -*-
"""Unit tests for node editor helpers, including localization fallback."""

from __future__ import annotations

import unittest


class _MockNode:
    """Minimal mock for a Blender node."""

    def __init__(self, name: str, bl_idname: str):
        self.name = name
        self.bl_idname = bl_idname
        self.label = name


class _MockNodeCollection:
    """Minimal mock for node_tree.nodes."""

    def __init__(self, nodes: list[_MockNode] | None = None):
        self._nodes = {n.name: n for n in (nodes or [])}

    def get(self, name: str) -> _MockNode | None:
        return self._nodes.get(name)

    def __iter__(self):
        return iter(self._nodes.values())


class _MockNodeTree:
    """Minimal mock for a Blender node tree."""

    def __init__(self, nodes: list[_MockNode] | None = None):
        self.nodes = _MockNodeCollection(nodes)


class TestGetNode(unittest.TestCase):
    """Tests for _get_node helper in nodes/editor.py."""

    def _get_node(self, node_tree, name_or_identifier):
        from blender_mcp_addon.handlers.nodes.editor import _get_node

        return _get_node(node_tree, name_or_identifier)

    def test_exact_name_match(self):
        """Exact name lookup returns the node."""
        node = _MockNode("Principled BSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Principled BSDF"), node)

    def test_bl_idname_fallback(self):
        """When name doesn't match, bl_idname fallback finds the node."""
        # Chinese-localized node name ("Principled BSDF" in Chinese)
        # Tests that bl_idname lookup works when display name is localized
        node = _MockNode("原理化 BSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        result = self._get_node(tree, "ShaderNodeBsdfPrincipled")
        self.assertIs(result, node)

    def test_bl_idname_fallback_japanese(self):
        """bl_idname fallback works for Japanese-localized names."""
        # Japanese-localized node name ("Principled BSDF" in Japanese)
        node = _MockNode("プリンシプルBSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        result = self._get_node(tree, "ShaderNodeBsdfPrincipled")
        self.assertIs(result, node)

    def test_not_found_returns_none(self):
        """Returns None when neither name nor bl_idname match."""
        # Chinese-localized node name for testing not-found scenario
        node = _MockNode("原理化 BSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        self.assertIsNone(self._get_node(tree, "NonexistentNode"))

    def test_exact_name_takes_priority_over_bl_idname(self):
        """Exact name match is preferred over bl_idname match."""
        node_a = _MockNode("ShaderNodeBsdfPrincipled", "ShaderNodeCustom")
        # Chinese-localized node name
        node_b = _MockNode("原理化 BSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node_a, node_b])
        # Should match node_a by exact name, not node_b by bl_idname
        result = self._get_node(tree, "ShaderNodeBsdfPrincipled")
        self.assertIs(result, node_a)

    def test_empty_tree_returns_none(self):
        """Returns None for an empty node tree."""
        tree = _MockNodeTree([])
        self.assertIsNone(self._get_node(tree, "Anything"))

    def test_first_bl_idname_match_returned(self):
        """When multiple nodes share a bl_idname, the first match is returned."""
        node_a = _MockNode("OutputA", "ShaderNodeOutputMaterial")
        node_b = _MockNode("OutputB", "ShaderNodeOutputMaterial")
        tree = _MockNodeTree([node_a, node_b])
        result = self._get_node(tree, "ShaderNodeOutputMaterial")
        # Should get one of them (first encountered)
        self.assertIn(result, [node_a, node_b])


class TestGetNodeEnglishFallback(unittest.TestCase):
    """Tests for English display-name fallback in _get_node."""

    def _get_node(self, node_tree, name_or_identifier):
        from blender_mcp_addon.handlers.nodes.editor import _get_node

        return _get_node(node_tree, name_or_identifier)

    def test_principled_bsdf_english_name_in_chinese_blender(self):
        """LLM passes 'Principled BSDF' → finds localized node."""
        node = _MockNode("原理化 BSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Principled BSDF"), node)

    def test_material_output_english_name_in_chinese_blender(self):
        """LLM passes 'Material Output' → finds localized node."""
        node = _MockNode("材质输出", "ShaderNodeOutputMaterial")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Material Output"), node)

    def test_group_input_english_name_in_chinese_blender(self):
        """LLM passes 'Group Input' → finds localized node."""
        node = _MockNode("组输入", "NodeGroupInput")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Group Input"), node)

    def test_group_output_english_name_in_chinese_blender(self):
        """LLM passes 'Group Output' → finds localized node."""
        node = _MockNode("组输出", "NodeGroupOutput")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Group Output"), node)

    def test_noise_texture_english_name_in_chinese_blender(self):
        """LLM passes 'Noise Texture' → finds localized node."""
        node = _MockNode("噪波纹理", "ShaderNodeTexNoise")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Noise Texture"), node)

    def test_image_texture_english_name_in_japanese_blender(self):
        """LLM passes 'Image Texture' → finds Japanese-localized node."""
        node = _MockNode("画像テクスチャ", "ShaderNodeTexImage")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Image Texture"), node)

    def test_subdivision_surface_english_name_in_chinese_blender(self):
        """LLM passes 'Subdivision Surface' → finds localized geo node."""
        node = _MockNode("细分表面", "GeometryNodeSubdivisionSurface")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Subdivision Surface"), node)

    def test_render_layers_english_name_in_chinese_blender(self):
        """LLM passes 'Render Layers' → finds localized compositor node."""
        node = _MockNode("渲染层", "CompositorNodeRLayers")
        tree = _MockNodeTree([node])
        self.assertIs(self._get_node(tree, "Render Layers"), node)

    def test_exact_name_still_takes_priority(self):
        """If a custom node is literally named 'Principled BSDF', it wins."""
        custom = _MockNode("Principled BSDF", "ShaderNodeCustomType")
        localized = _MockNode("原理化 BSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([custom, localized])
        self.assertIs(self._get_node(tree, "Principled BSDF"), custom)

    def test_bl_idname_still_takes_priority_over_english_name(self):
        """bl_idname match is preferred over English name mapping."""
        node = _MockNode("SomeOtherName", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        # "ShaderNodeBsdfPrincipled" matches by bl_idname directly
        self.assertIs(self._get_node(tree, "ShaderNodeBsdfPrincipled"), node)

    def test_unknown_english_name_returns_none(self):
        """English name not in mapping still returns None."""
        node = _MockNode("SomeNode", "SomeType")
        tree = _MockNodeTree([node])
        self.assertIsNone(self._get_node(tree, "Nonexistent Display Name"))


if __name__ == "__main__":
    unittest.main()
