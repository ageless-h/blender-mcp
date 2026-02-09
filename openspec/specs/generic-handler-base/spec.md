## ADDED Requirements

### Requirement: GenericCollectionHandler provides default write implementation
GenericCollectionHandler SHALL provide a default `write()` method that iterates the `properties` dict. For each property, it SHALL first call `_custom_write(item, prop_path, value)`. If `_custom_write()` returns `True`, the property is considered handled. Otherwise, it SHALL call `_set_nested_attr()` for the key-value pair on the looked-up item. The method SHALL return `{"name": name, "modified": [list of modified property paths]}`.

#### Scenario: Write properties to a data block using generic handler
- **WHEN** `write(name, properties, params)` is called on a GenericCollectionHandler subclass
- **THEN** system looks up the item via `get_item(name)`, calls `_custom_write()` then optionally `_set_nested_attr()` for each property, and returns `{"name": name, "modified": [keys]}`

#### Scenario: Write raises KeyError for missing data block
- **WHEN** `write(name, properties, params)` is called and `get_item(name)` returns None
- **THEN** system raises `KeyError` with a message containing the item name

### Requirement: GenericCollectionHandler provides default delete implementation
GenericCollectionHandler SHALL provide a default `delete()` method that looks up the item by name, removes it from the bpy.data collection, and returns `{"deleted": name}`.

#### Scenario: Delete a data block using generic handler
- **WHEN** `delete(name, params)` is called on a GenericCollectionHandler subclass
- **THEN** system looks up the item via `get_item(name)`, calls `get_collection().remove(item)`, and returns `{"deleted": name}`

#### Scenario: Delete raises KeyError for missing data block
- **WHEN** `delete(name, params)` is called and `get_item(name)` returns None
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

### Requirement: GenericCollectionHandler provides default read with path delegation
GenericCollectionHandler SHALL provide a default `read()` method that, when a `path` argument is given, delegates to `_get_nested_attr()` and returns `{"name": name, "path": path, "value": value}`. When no path is given, it SHALL call `_read_summary(item)`.

#### Scenario: Read specific property path
- **WHEN** `read(name, path, params)` is called with a non-None path
- **THEN** system looks up the item, calls `_get_nested_attr(item, path)`, and returns `{"name": name, "path": path, "value": value}`

#### Scenario: Read full summary without path
- **WHEN** `read(name, None, params)` is called
- **THEN** system looks up the item and returns the dict from `_read_summary(item)`

#### Scenario: Read raises KeyError for missing data block
- **WHEN** `read(name, path, params)` is called and `get_item(name)` returns None
- **THEN** system raises `KeyError` with a message containing the item name

### Requirement: Subclasses MUST override _read_summary
GenericCollectionHandler SHALL define `_read_summary(item)` as a method that raises `NotImplementedError`. Every subclass MUST override it to return a dict of fields for a full read.

#### Scenario: Unoverridden _read_summary raises error
- **WHEN** a subclass does not override `_read_summary()` and `read()` is called without a path
- **THEN** system raises `NotImplementedError`

#### Scenario: Subclass provides custom read summary
- **WHEN** a subclass overrides `_read_summary(item)` to return `{"name": item.name, "filepath": item.filepath}`
- **THEN** `read(name, None, {})` returns that dict

### Requirement: _list_fields has a sensible default
GenericCollectionHandler SHALL define `_list_fields(item)` with a default implementation returning `{"name": item.name}`. Subclasses MAY override to include additional fields.

#### Scenario: Default list fields returns name only
- **WHEN** a subclass does not override `_list_fields()`
- **THEN** `list_items()` returns items with only `{"name": ...}` per entry

#### Scenario: Subclass provides custom list fields
- **WHEN** a subclass overrides `_list_fields(item)` to return `{"name": item.name, "volume": item.volume}`
- **THEN** `list_items()` returns items with both name and volume fields

### Requirement: _type_label provides human-readable name for errors
GenericCollectionHandler SHALL define `_type_label()` with a default returning `self.data_type.value` (capitalized). Subclasses MAY override for custom labels (e.g., "Light probe" instead of "probe").

#### Scenario: Default type label used in KeyError
- **WHEN** a handler with `data_type = DataType.VOLUME` fails to find an item
- **THEN** the raised KeyError message contains "Volume" (derived from `data_type.value`)

#### Scenario: Custom type label used in KeyError
- **WHEN** a handler overrides `_type_label()` to return "Light probe"
- **THEN** the raised KeyError message contains "Light probe"

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

### Requirement: GenericCollectionHandler preserves BaseHandler interface
GenericCollectionHandler SHALL extend `BaseHandler` and SHALL NOT add any new abstract methods. The `create()` method SHALL remain abstract (inherited from BaseHandler) — each subclass MUST still implement its own `create()`.

#### Scenario: Handler registered via decorator works identically
- **WHEN** a handler subclassing GenericCollectionHandler is decorated with `@HandlerRegistry.register`
- **THEN** it is registered and dispatched identically to handlers subclassing BaseHandler directly

#### Scenario: create() remains required
- **WHEN** a subclass of GenericCollectionHandler does not implement `create()`
- **THEN** instantiation raises `TypeError` (ABC enforcement)

### Requirement: Behavioral equivalence after migration
Every handler migrated from BaseHandler to GenericCollectionHandler SHALL produce identical return values for all CRUD operations given the same inputs, compared to the pre-migration implementation.

#### Scenario: Migrated handler write returns same result
- **WHEN** `SurfaceHandler.write("Surf", {"resolution_u": 12}, {})` is called after migration
- **THEN** the return value is identical to the pre-migration return value: `{"name": "Surf", "modified": ["resolution_u"]}`

#### Scenario: Migrated handler delete returns same result
- **WHEN** `VolumeHandler.delete("Vol", {})` is called after migration
- **THEN** the return value is `{"deleted": "Vol"}`, identical to pre-migration

#### Scenario: Migrated handler list_items returns same structure
- **WHEN** `SoundHandler.list_items(None)` is called after migration
- **THEN** the return value has the same `{"items": [...], "count": N}` structure and field set as pre-migration

### Requirement: Dispatcher _resolve_handler extracts common preamble
The data dispatcher SHALL provide a `_resolve_handler()` helper that performs bpy availability check, type string extraction, type parsing, and handler lookup. All dispatcher functions (`data_create`, `data_read`, `data_write`, `data_delete`, `data_list`) SHALL use this helper.

#### Scenario: Resolve handler returns handler on valid type
- **WHEN** `_resolve_handler({"type": "material"}, started)` is called
- **THEN** it returns `(MaterialHandler_instance, "material", None)`

#### Scenario: Resolve handler returns error on missing type
- **WHEN** `_resolve_handler({}, started)` is called
- **THEN** it returns `(None, None, error_response)` with code "invalid_params"

#### Scenario: Resolve handler returns error on unknown type
- **WHEN** `_resolve_handler({"type": "nonexistent"}, started)` is called
- **THEN** it returns `(None, None, error_response)` with code "unsupported_type"

### Requirement: Shared VIEW_3D context override utility
The handler system SHALL provide a shared `get_view3d_override(bpy)` function that builds a context override dict containing the window, VIEW_3D area, and WINDOW region. All handler modules requiring a VIEW_3D context override SHALL use this shared function.

#### Scenario: Context override dict contains required keys
- **WHEN** `get_view3d_override(bpy)` is called in a GUI session with a VIEW_3D area
- **THEN** the returned dict contains "window", "area", and "region" keys

#### Scenario: Context override returns empty dict when no VIEW_3D area
- **WHEN** `get_view3d_override(bpy)` is called and no VIEW_3D area exists
- **THEN** the returned dict is empty or contains only "window"

### Requirement: TextHandler delegates to FontHandler implementation
TextHandler and FontHandler SHALL share a single implementation for all CRUD methods. TextHandler SHALL NOT duplicate any method body from FontHandler.

#### Scenario: TextHandler and FontHandler share create logic
- **WHEN** `TextHandler.create("MyText", {"body": "Hello"})` is called
- **THEN** it produces the same bpy.data.curves FONT entry as `FontHandler.create("MyText", {"body": "Hello"})`

#### Scenario: Both handlers registered with distinct DataTypes
- **WHEN** the handler system initializes
- **THEN** `HandlerRegistry.get(DataType.TEXT)` and `HandlerRegistry.get(DataType.FONT)` return distinct handler instances that share method implementations
