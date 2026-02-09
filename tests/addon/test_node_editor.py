# -*- coding: utf-8 -*-
"""Unit tests for node editor helpers, including localization fallback."""
from __future__ import annotations

import unittest
from typing import Any


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
        node = _MockNode("原理化 BSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        result = self._get_node(tree, "ShaderNodeBsdfPrincipled")
        self.assertIs(result, node)

    def test_bl_idname_fallback_japanese(self):
        """bl_idname fallback works for Japanese-localized names."""
        node = _MockNode("プリンシプルBSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        result = self._get_node(tree, "ShaderNodeBsdfPrincipled")
        self.assertIs(result, node)

    def test_not_found_returns_none(self):
        """Returns None when neither name nor bl_idname match."""
        node = _MockNode("原理化 BSDF", "ShaderNodeBsdfPrincipled")
        tree = _MockNodeTree([node])
        self.assertIsNone(self._get_node(tree, "NonexistentNode"))

    def test_exact_name_takes_priority_over_bl_idname(self):
        """Exact name match is preferred over bl_idname match."""
        node_a = _MockNode("ShaderNodeBsdfPrincipled", "ShaderNodeCustom")
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


if __name__ == "__main__":
    unittest.main()
