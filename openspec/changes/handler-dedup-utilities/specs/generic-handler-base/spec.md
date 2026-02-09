## ADDED Requirements

### Requirement: _filter_item hook for filtered list_items
GenericCollectionHandler SHALL define a `_filter_item(self, item, filter_params) -> bool` method with a default implementation that returns `True`. The default `list_items()` method SHALL call `_filter_item()` for each item when `filter_params` is non-empty, excluding items where the method returns `False`. Subclasses MAY override `_filter_item()` to implement type-specific filtering without overriding the entire `list_items()` method.

#### Scenario: Default _filter_item includes all items
- **WHEN** `list_items({"some_filter": "value"})` is called on a subclass that does not override `_filter_item()`
- **THEN** all items in the collection are included in the result (default returns `True`)

#### Scenario: Subclass filters by custom field
- **WHEN** a subclass overrides `_filter_item()` to check `filter_params.get("light_type")` against `item.type`
- **AND** `list_items({"light_type": "POINT"})` is called
- **THEN** only items where `item.type == "POINT"` are included

#### Scenario: Empty or None filter_params skips filtering
- **WHEN** `list_items(None)` or `list_items({})` is called
- **THEN** `_filter_item()` is still called for each item but the default implementation returns `True`, so all items are included

#### Scenario: Filter does not affect count consistency
- **WHEN** `list_items(filter_params)` is called and `_filter_item()` excludes some items
- **THEN** the returned `count` matches the length of the returned `items` list

### Requirement: _custom_write hook for special property handling
GenericCollectionHandler SHALL define a `_custom_write(self, item, prop_path, value) -> bool` method with a default implementation that returns `False`. The default `write()` method SHALL call `_custom_write()` for each property before falling back to `_set_nested_attr()`. If `_custom_write()` returns `True`, the property is considered handled and `_set_nested_attr()` is skipped for that property. Subclasses MAY override `_custom_write()` to handle special properties (e.g., color tuples, node-tree-backed values) without overriding the entire `write()` method.

#### Scenario: Default _custom_write defers to _set_nested_attr
- **WHEN** `write(name, {"energy": 100}, {})` is called on a subclass that does not override `_custom_write()`
- **THEN** `_custom_write()` returns `False` and `_set_nested_attr(item, "energy", 100)` is called

#### Scenario: Subclass handles color property via _custom_write
- **WHEN** a subclass overrides `_custom_write()` to handle `prop_path == "color"` by calling `item.color = tuple(value[:3])`
- **AND** `write(name, {"color": [1.0, 0.5, 0.0]}, {})` is called
- **THEN** `_custom_write()` returns `True` and `_set_nested_attr()` is NOT called for "color"
- **AND** the property "color" appears in the returned `modified` list

#### Scenario: Mixed custom and standard properties in single write
- **WHEN** `write(name, {"color": [1, 0, 0], "energy": 500}, {})` is called and `_custom_write()` handles "color" but not "energy"
- **THEN** "color" is handled by `_custom_write()` and "energy" is handled by `_set_nested_attr()`
- **AND** both appear in the returned `modified` list

## MODIFIED Requirements

### Requirement: GenericCollectionHandler provides default write implementation
GenericCollectionHandler SHALL provide a default `write()` method that iterates the `properties` dict. For each property, it SHALL first call `_custom_write(item, prop_path, value)`. If `_custom_write()` returns `True`, the property is considered handled. Otherwise, it SHALL call `_set_nested_attr()` for the key-value pair on the looked-up item. The method SHALL return `{"name": name, "modified": [list of modified property paths]}`.

#### Scenario: Write properties to a data block using generic handler
- **WHEN** `write(name, properties, params)` is called on a GenericCollectionHandler subclass
- **THEN** system looks up the item via `get_item(name)`, calls `_custom_write()` then optionally `_set_nested_attr()` for each property, and returns `{"name": name, "modified": [keys]}`

#### Scenario: Write raises KeyError for missing data block
- **WHEN** `write(name, properties, params)` is called and `get_item(name)` returns None
- **THEN** system raises `KeyError` with a message containing the item name

### Requirement: GenericCollectionHandler provides default list_items implementation
GenericCollectionHandler SHALL provide a default `list_items()` method that iterates the bpy.data collection, calls `_filter_item(item, filter_params)` for each item to determine inclusion, then calls `_list_fields(item)` for included items, and returns `{"items": [...], "count": N}`.

#### Scenario: List all data blocks using generic handler
- **WHEN** `list_items(filter_params)` is called on a GenericCollectionHandler subclass
- **THEN** system iterates `get_collection()`, filters via `_filter_item()`, builds a list via `_list_fields()` per included item, and returns `{"items": [...], "count": len(items)}`

#### Scenario: List returns empty when collection has no items
- **WHEN** `list_items(filter_params)` is called and the bpy.data collection is empty
- **THEN** system returns `{"items": [], "count": 0}`

#### Scenario: List returns empty when all items filtered out
- **WHEN** `list_items(filter_params)` is called and `_filter_item()` returns `False` for every item
- **THEN** system returns `{"items": [], "count": 0}`
