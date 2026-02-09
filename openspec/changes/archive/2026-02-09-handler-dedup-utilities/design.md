## Context

The handler system in `src/blender_mcp_addon/handlers/` implements CRUD operations for ~32 Blender data types via a two-tier class hierarchy: `BaseHandler` (ABC with 5 abstract methods) and `GenericCollectionHandler` (provides default read/write/delete/list_items, subclass only implements `create()` + `_read_summary()`).

18 handlers already use `GenericCollectionHandler` successfully. However, 14 handlers still extend `BaseHandler` directly. Of these, at least 4 (`LightHandler`, `TextureHandler`, `WorldHandler`, `SceneHandler`) only do so because `GenericCollectionHandler` lacks two capabilities: filtered listing and custom property write handling.

Additionally, three distinct code patterns are copy-pasted across multiple handlers:
- bmesh primitive creation (~50 lines, verbatim in `MeshHandler` and `ObjectHandler`)
- Object-to-scene linking (~12 lines, in 7 handlers)
- "Find objects referencing data block" scan (~15 lines, in Camera and Light reads)

## Goals / Non-Goals

**Goals:**
- Eliminate ~460 lines of duplicated handler code via utility extraction and handler migration
- Add two optional hooks to `GenericCollectionHandler` so more handlers can use it without overriding entire methods
- Maintain 100% behavioral equivalence — all CRUD operations return identical results before and after
- Keep the change purely internal; no external API surface changes

**Non-Goals:**
- Introducing new abstractions (no `DeclarativeHandler`, no `HandlerConfig` dataclass, no property converter registry)
- Changing the `import bpy` pattern inside methods — this is standard Blender addon convention
- Migrating complex handlers (`ObjectHandler`, `MaterialHandler`, `CollectionHandler`, `MeshHandler`) to `GenericCollectionHandler` — they have legitimate custom logic
- Adding lint rules or `__init_subclass__` warnings to enforce handler base class choices

## Decisions

### D1: New module `handlers/shared.py` for utility functions

**Decision**: Create a single `shared.py` module in the handlers package containing all three utility functions.

**Alternatives considered**:
- **Separate modules** (`mesh_utils.py`, `link_utils.py`, `scan_utils.py`) — rejected because these are small functions (10-50 lines each) and splitting them across files adds navigation overhead for 3 functions
- **Methods on BaseHandler** — rejected because these are stateless utilities, not handler behavior; making them instance methods would couple them unnecessarily to the handler class

**Rationale**: A single `shared.py` keeps the utilities discoverable and importable with one line. The functions are pure utilities with no shared state.

### D2: `create_mesh_primitive()` uses try/finally for bmesh cleanup

**Decision**: The function wraps bmesh operations in try/finally to guarantee `bm.free()` even on errors.

```python
def create_mesh_primitive(mesh, primitive: str, params: dict) -> None:
    import bmesh
    bm = bmesh.new()
    try:
        # ... dispatch to bmesh.ops based on primitive string
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.validate()
    mesh.update(calc_edges=True, calc_edges_loose=True)
```

**Rationale**: The current code in both `MeshHandler` and `ObjectHandler` does not use try/finally — it calls `bm.free()` only on the happy path or in the ValueError branch. This is a minor correctness improvement.

### D3: `link_data_to_scene()` signature

**Decision**: `link_data_to_scene(data_block, params) -> bpy.types.Object`

The function reads from `params`:
- `object_name` (default: `data_block.name`)
- `collection` (optional collection name)
- `location` (optional `[x, y, z]`)
- `rotation` (optional `[x, y, z]`)

**Alternatives considered**:
- **Explicit keyword arguments** (`link_data_to_scene(data_block, obj_name=None, collection=None, ...)`) — rejected because the callers already have a `params` dict and would need to unpack/repack
- **Accepting `bpy` as argument** — rejected; the function imports `bpy` internally following the existing convention in handler code

**Rationale**: Matches the existing calling convention where callers pass through their `params` dict.

### D4: Hook methods return `bool` as handled-signal

**Decision**: Both `_filter_item()` and `_custom_write()` use return values as signals:
- `_filter_item(item, filter_params) -> bool`: `True` = include, `False` = exclude
- `_custom_write(item, prop_path, value) -> bool`: `True` = handled (skip `_set_nested_attr`), `False` = not handled (fall through)

**Alternatives considered**:
- **Raising `NotImplementedError` sentinel** — rejected as overly complex for a simple include/exclude decision
- **Returning the transformed value** from `_custom_write` — rejected because write hooks often set the property directly on the Blender object (side effect), not transform a value

**Rationale**: Boolean signals are the simplest pattern. Default implementations (`True` for filter, `False` for write) mean existing subclasses require zero changes.

### D5: Updated `write()` flow in GenericCollectionHandler

**Decision**: The write loop becomes:

```python
for prop_path, value in properties.items():
    if not self._custom_write(item, prop_path, value):
        self._set_nested_attr(item, prop_path, value)
    modified.append(prop_path)
```

**Rationale**: `_custom_write()` defaults to `False`, so existing handlers that don't override it get identical behavior — every property falls through to `_set_nested_attr()`. The property is always added to `modified` regardless of which path handled it.

### D6: Updated `list_items()` flow in GenericCollectionHandler

**Decision**: The list loop becomes:

```python
filter_params = filter_params or {}
items = []
for item in collection:
    if not self._filter_item(item, filter_params):
        continue
    items.append(self._list_fields(item))
```

**Rationale**: `_filter_item()` defaults to `True`, so existing handlers get identical behavior — all items pass through. Handlers like `LightHandler` override to check `filter_params.get("light_type")` against `item.type`.

### D7: Migration order — utilities first, then hooks, then handlers

**Decision**: Implementation proceeds in three phases:
1. Create `shared.py` with utility functions + tests
2. Add hooks to `GenericCollectionHandler` + tests
3. Migrate handlers one at a time, verifying each

**Rationale**: Each phase is independently testable and deployable. If a migration causes issues, the utilities and hooks are still useful for future work.

## Risks / Trade-offs

- **Behavioral divergence during migration** → Mitigation: Each migrated handler gets a before/after test comparing CRUD outputs. Existing tests must pass unchanged.
- **`find_referencing_objects()` performance on large scenes** → Accepted: The current code already does the same O(n) scan. No performance change. Future optimization (e.g., caching) is out of scope.
- **WorldHandler and SceneHandler have complex `_custom_write` needs** (node-tree-backed properties, reference lookups) → Mitigation: If `_custom_write()` becomes unwieldy for a specific handler, that handler keeps its own `write()` override. The hook is optional, not mandatory.
- **Merge conflicts if other changes touch handler files concurrently** → Mitigation: The utility extractions are additive (new file), and the hook additions are small, localized edits to `base.py`.
