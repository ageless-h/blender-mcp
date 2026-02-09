# -*- coding: utf-8 -*-
"""Unit tests for GenericCollectionHandler default methods."""
from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import patch

from blender_mcp_addon.handlers.base import GenericCollectionHandler
from blender_mcp_addon.handlers.types import DataType


class _MockItem:
    """Minimal mock for a bpy data block."""

    def __init__(self, name: str, **kwargs: Any):
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)


class _MockCollection:
    """Minimal mock for a bpy.data collection."""

    def __init__(self, items: list[_MockItem] | None = None):
        self._items = {item.name: item for item in (items or [])}

    def get(self, name: str) -> _MockItem | None:
        return self._items.get(name)

    def remove(self, item: _MockItem) -> None:
        self._items.pop(item.name, None)

    def __iter__(self):
        return iter(self._items.values())

    def __len__(self):
        return len(self._items)


class ConcreteHandler(GenericCollectionHandler):
    """Concrete test subclass with _read_summary implemented."""

    data_type = DataType.VOLUME

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        return {"name": name, "type": "volume"}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "filepath": getattr(item, "filepath", "")}


class BareHandler(GenericCollectionHandler):
    """Subclass that does NOT override _read_summary."""

    data_type = DataType.SURFACE

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        return {"name": name, "type": "surface"}


class CustomListHandler(GenericCollectionHandler):
    """Subclass with custom _list_fields and _type_label."""

    data_type = DataType.SPEAKER

    def create(self, name: str, params: dict[str, Any]) -> dict[str, Any]:
        return {"name": name, "type": "speaker"}

    def _read_summary(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "volume": getattr(item, "volume", 1.0)}

    def _list_fields(self, item: Any) -> dict[str, Any]:
        return {"name": item.name, "volume": getattr(item, "volume", 1.0)}

    def _type_label(self) -> str:
        return "Speaker"


class TestGenericCollectionHandlerRead(unittest.TestCase):
    """Tests for GenericCollectionHandler.read()."""

    def setUp(self):
        self.handler = ConcreteHandler()
        self.item = _MockItem("Vol1", filepath="/tmp/vol.vdb")
        self.collection = _MockCollection([self.item])

    def test_read_summary(self):
        """read() without path calls _read_summary."""
        with patch.object(self.handler, "get_item", return_value=self.item):
            result = self.handler.read("Vol1", None, {})
        self.assertEqual(result, {"name": "Vol1", "filepath": "/tmp/vol.vdb"})

    def test_read_with_path(self):
        """read() with path delegates to _get_nested_attr."""
        with patch.object(self.handler, "get_item", return_value=self.item):
            result = self.handler.read("Vol1", "filepath", {})
        self.assertEqual(result, {"name": "Vol1", "path": "filepath", "value": "/tmp/vol.vdb"})

    def test_read_missing_raises_key_error(self):
        """read() raises KeyError when item not found."""
        with patch.object(self.handler, "get_item", return_value=None):
            with self.assertRaises(KeyError) as ctx:
                self.handler.read("Missing", None, {})
            self.assertIn("Missing", str(ctx.exception))

    def test_read_summary_not_implemented(self):
        """read() raises NotImplementedError if _read_summary not overridden."""
        handler = BareHandler()
        item = _MockItem("Surf1")
        with patch.object(handler, "get_item", return_value=item):
            with self.assertRaises(NotImplementedError):
                handler.read("Surf1", None, {})


class TestGenericCollectionHandlerWrite(unittest.TestCase):
    """Tests for GenericCollectionHandler.write()."""

    def setUp(self):
        self.handler = ConcreteHandler()
        self.item = _MockItem("Vol1", filepath="/tmp/vol.vdb")

    def test_write_modifies_properties(self):
        """write() applies properties and returns modified list."""
        with patch.object(self.handler, "get_item", return_value=self.item):
            result = self.handler.write("Vol1", {"filepath": "/new/path.vdb"}, {})
        self.assertEqual(result, {"name": "Vol1", "modified": ["filepath"]})
        self.assertEqual(self.item.filepath, "/new/path.vdb")

    def test_write_multiple_properties(self):
        """write() handles multiple properties."""
        self.item.name = "Vol1"
        with patch.object(self.handler, "get_item", return_value=self.item):
            result = self.handler.write("Vol1", {"filepath": "/a", "name": "Vol2"}, {})
        self.assertEqual(len(result["modified"]), 2)
        self.assertIn("filepath", result["modified"])
        self.assertIn("name", result["modified"])

    def test_write_missing_raises_key_error(self):
        """write() raises KeyError when item not found."""
        with patch.object(self.handler, "get_item", return_value=None):
            with self.assertRaises(KeyError) as ctx:
                self.handler.write("Missing", {"filepath": "/x"}, {})
            self.assertIn("Missing", str(ctx.exception))


class TestGenericCollectionHandlerDelete(unittest.TestCase):
    """Tests for GenericCollectionHandler.delete()."""

    def setUp(self):
        self.handler = ConcreteHandler()
        self.item = _MockItem("Vol1")
        self.collection = _MockCollection([self.item])

    def test_delete_removes_item(self):
        """delete() removes item from collection."""
        with patch.object(self.handler, "get_item", return_value=self.item), \
             patch.object(self.handler, "get_collection", return_value=self.collection):
            result = self.handler.delete("Vol1", {})
        self.assertEqual(result, {"deleted": "Vol1"})
        self.assertIsNone(self.collection.get("Vol1"))

    def test_delete_missing_raises_key_error(self):
        """delete() raises KeyError when item not found."""
        with patch.object(self.handler, "get_item", return_value=None):
            with self.assertRaises(KeyError) as ctx:
                self.handler.delete("Missing", {})
            self.assertIn("Missing", str(ctx.exception))


class TestGenericCollectionHandlerListItems(unittest.TestCase):
    """Tests for GenericCollectionHandler.list_items()."""

    def test_list_items_default_fields(self):
        """list_items() uses default _list_fields returning name."""
        handler = ConcreteHandler()
        items = [_MockItem("A"), _MockItem("B"), _MockItem("C")]
        collection = _MockCollection(items)
        with patch.object(handler, "get_collection", return_value=collection):
            result = handler.list_items(None)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["items"], [{"name": "A"}, {"name": "B"}, {"name": "C"}])

    def test_list_items_custom_fields(self):
        """list_items() uses custom _list_fields when overridden."""
        handler = CustomListHandler()
        items = [_MockItem("Spk1", volume=0.5), _MockItem("Spk2", volume=0.8)]
        collection = _MockCollection(items)
        with patch.object(handler, "get_collection", return_value=collection):
            result = handler.list_items(None)
        self.assertEqual(result["count"], 2)
        self.assertEqual(result["items"][0], {"name": "Spk1", "volume": 0.5})

    def test_list_items_empty_collection(self):
        """list_items() returns empty when collection is empty."""
        handler = ConcreteHandler()
        collection = _MockCollection([])
        with patch.object(handler, "get_collection", return_value=collection):
            result = handler.list_items(None)
        self.assertEqual(result, {"items": [], "count": 0})

    def test_list_items_none_collection(self):
        """list_items() returns empty when collection is None."""
        handler = ConcreteHandler()
        with patch.object(handler, "get_collection", return_value=None):
            result = handler.list_items(None)
        self.assertEqual(result, {"items": [], "count": 0})


class TestGenericCollectionHandlerTypeLabel(unittest.TestCase):
    """Tests for _type_label()."""

    def test_default_type_label(self):
        """Default _type_label capitalises data_type.value."""
        handler = ConcreteHandler()
        self.assertEqual(handler._type_label(), "Volume")

    def test_custom_type_label(self):
        """Custom _type_label returns overridden value."""
        handler = CustomListHandler()
        self.assertEqual(handler._type_label(), "Speaker")

    def test_type_label_in_error_message(self):
        """_type_label is used in KeyError messages."""
        handler = ConcreteHandler()
        with patch.object(handler, "get_item", return_value=None):
            with self.assertRaises(KeyError) as ctx:
                handler.read("X", None, {})
            self.assertIn("Volume", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
