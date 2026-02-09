## Context

The `handlers/data/` directory implements the unified CRUD system for ~40 Blender data types. Each data type has a handler class extending `BaseHandler` (ABC) with five abstract methods: `create()`, `read()`, `write()`, `delete()`, `list_items()`, plus an optional `link()` override. Handlers are registered via `@HandlerRegistry.register` and dispatched through `data/dispatcher.py`.

Of the ~20 implemented handlers, at least 15 "simple" handlers (surface, volume, sound, movieclip, cachefile, mask, workspace, light_probe, speaker, paintcurve, annotation, library, palette, lattice, brush) share near-identical `write()`, `delete()`, and `list_items()` implementations. The only variation is the bpy.data collection name (already mapped in `types.py:DATA_TYPE_TO_COLLECTION`) and a handful of fields returned from `read()` and `list_items()`.

Separately, four handler modules (`physics/handler.py`, `uv/handler.py`, `importexport/handler.py`, `info/query.py`) each contain a copy-pasted ~10-line block for building a VIEW_3D context override dict, and the dispatcher repeats a ~12-line validation preamble across 5 functions.

## Goals / Non-Goals

**Goals:**
- Eliminate ~1,500+ lines of mechanically duplicated handler code without changing any external behavior
- Provide a `GenericCollectionHandler` base that makes adding new data type handlers a ~20-line task
- Extract shared utilities (dispatcher preamble, VIEW_3D context override) to single sources of truth
- Merge the near-identical `TextHandler`/`FontHandler` pair
- Remove dead code (`_PHYSICS_OPERATOR_MAP`)
- Consolidate triplicated `_pathfix.py`

**Non-Goals:**
- Changing any MCP tool schema, response envelope, or external API behavior
- Adding new data type support or new CRUD operations
- Refactoring complex handlers (ObjectHandler, MeshHandler, CollectionHandler, ImageHandler, etc.) — these have significant custom logic and are not candidates for GenericCollectionHandler
- Modifying the `BaseHandler` ABC interface or `HandlerRegistry` mechanics
- Performance optimization (this is a code quality change)

## Decisions

### Decision 1: GenericCollectionHandler as a concrete middle class

**Choice**: Insert `GenericCollectionHandler` between `BaseHandler` (ABC) and the simple handlers as a concrete class providing default CRUD implementations.

```
BaseHandler (ABC)
├── GenericCollectionHandler (concrete defaults)
│   ├── SurfaceHandler (minimal overrides)
│   ├── VolumeHandler (minimal overrides)
│   ├── SoundHandler (minimal overrides)
│   └── ... (~15 simple handlers)
├── MaterialHandler (custom logic, stays as-is)
├── ObjectHandler (custom logic, stays as-is)
└── ...
```

**Rationale**: A middle class preserves the ABC contract, doesn't touch complex handlers, and lets simple handlers opt in by changing one parent class. The alternative — injecting default methods directly into `BaseHandler` — would risk masking bugs in complex handlers that forget to override a method.

**Default implementations provided by GenericCollectionHandler:**
- `write()`: Iterates `properties`, calls `self._set_nested_attr()` for each, returns `{"name": name, "modified": [...]}`
- `delete()`: Calls `self.get_item(name)`, raises `KeyError` if missing, calls `collection.remove(item)`, returns `{"deleted": name}`
- `list_items()`: Iterates `self.get_collection()`, calls `self._list_fields(item)` for each, returns `{"items": [...], "count": N}`
- `read()`: If `path` is given, delegates to `_get_nested_attr`. Otherwise calls `self._read_summary(item)`.

**Override hooks for subclasses:**
- `_read_summary(item) -> dict`: Returns the dict of fields for a full read (no path). **Required override**.
- `_list_fields(item) -> dict`: Returns the dict of fields for list view. Defaults to `{"name": item.name}`.
- `_type_label() -> str`: Human-readable type name for error messages. Defaults to `self.data_type.value`.

### Decision 2: TextHandler delegates to FontHandler

**Choice**: Remove `TextHandler` as a separate implementation. Make it a thin subclass that sets `data_type = DataType.TEXT` but inherits all method implementations from `FontHandler` (or a shared `_FontCurveHandler` base).

**Rationale**: Both handlers operate on `bpy.data.curves` filtered by `type == "FONT"`. Their `create()`, `read()`, `write()`, `delete()`, and `list_items()` are byte-for-byte identical except for the string `"text"` vs `"font"` in results. A shared base eliminates ~90 lines.

**Alternative considered**: Alias `TextHandler = FontHandler` — rejected because they need distinct `data_type` enum values for the registry.

### Decision 3: Extract `_resolve_handler()` in dispatcher

**Choice**: Extract the repeated validation preamble into a single helper:

```python
def _resolve_handler(payload, started) -> tuple[BaseHandler, str, dict | None]:
    """Returns (handler, type_str, error_response_or_None)."""
```

All five dispatcher functions (`data_create/read/write/delete/list`) call this first. If the third return value is not None, they return it immediately as the error response.

**Rationale**: The 12-line block (check_bpy → get type → parse_type → get handler) is identical across all 5 functions. Extracting it to one place ensures consistent error handling and reduces ~60 lines.

### Decision 4: Shared `get_view3d_override()` utility

**Choice**: Create a shared function in `handlers/context_utils.py`:

```python
def get_view3d_override(bpy) -> dict[str, Any]:
    """Build a context override dict with window, VIEW_3D area, and WINDOW region."""
```

Replace the 4 copy-pasted instances in `physics/handler.py`, `uv/handler.py`, `importexport/handler.py`, and `info/query.py`.

**Rationale**: Single source of truth for a fiddly piece of Blender API interaction. If the approach needs to change (e.g., for Blender API version differences), it changes in one place.

### Decision 5: Consolidate `_pathfix.py`

**Choice**: Keep `scripts/_pathfix.py` (which adds both ROOT and SRC) as the canonical version. Replace `examples/_pathfix.py` and `tests/_pathfix.py` with single-line imports from a shared `_pathfix.py` at the repo root, or simply make all three import from `scripts/_pathfix.py`.

**Alternative considered**: Using `sitecustomize.py` (already exists at repo root) — but `sitecustomize.py` runs for all Python processes, which is too broad.

### Decision 6: Incremental migration order

**Choice**: Migrate handlers one-by-one to `GenericCollectionHandler`, running the full test suite after each batch. Order:
1. Start with the simplest (workspace, mask, surface — zero custom logic)
2. Then filepath-based (volume, sound, movieclip, cachefile)
3. Then type-filtered (light_probe, brush)
4. Then slightly richer (speaker, palette, lattice, paintcurve, annotation, library)
5. Finally merge TextHandler/FontHandler

**Rationale**: Incremental migration with test verification at each step minimizes risk and makes bisecting any regression trivial.

## Risks / Trade-offs

- **Risk: Subclass override forgotten** → A handler migrated to `GenericCollectionHandler` might lose custom behavior if `_read_summary()` isn't properly filled in. **Mitigation**: Each migration is verified against existing test suite; `_read_summary()` is the only required override and triggers `NotImplementedError` if missing.
- **Risk: Import ordering with `@HandlerRegistry.register` decorator** → Moving handlers to smaller files or changing inheritance could affect import-time registration. **Mitigation**: The `data/__init__.py` already explicitly imports all handlers; this pattern is preserved.
- **Risk: `_pathfix.py` consolidation breaks discovery** → Tests or examples might fail to find the shared module. **Mitigation**: Keep the existing files but make them one-line re-exports; verify with `uv run python -m unittest discover`.
- **Trade-off**: `GenericCollectionHandler` adds one more class to understand, but the payoff is ~15 fewer files to read when onboarding.
