## 1. GenericCollectionHandler Base Class

- [x] 1.1 Add `GenericCollectionHandler` class to `handlers/base.py` extending `BaseHandler` with default `read()`, `write()`, `delete()`, `list_items()` implementations and `_read_summary()`, `_list_fields()`, `_type_label()` hooks
- [x] 1.2 Add unit tests for `GenericCollectionHandler` default methods (write, delete, list_items, read with path, read without path, KeyError on missing, NotImplementedError on unoverridden `_read_summary`)
- [x] 1.3 Run full test suite to confirm no regressions: `uv run python -m unittest discover -s tests -p "test_*.py"`

## 2. Migrate Simplest Handlers (Batch 1: zero custom logic)

- [x] 2.1 Migrate `WorkspaceHandler` to subclass `GenericCollectionHandler` — override `_read_summary()` and `create()`
- [x] 2.2 Migrate `MaskHandler` to subclass `GenericCollectionHandler`
- [x] 2.3 Migrate `SurfaceHandler` to subclass `GenericCollectionHandler`
- [x] 2.4 Run test suite to verify batch 1

## 3. Migrate Filepath-Based Handlers (Batch 2)

- [x] 3.1 Migrate `VolumeHandler` to subclass `GenericCollectionHandler`
- [x] 3.2 Migrate `SoundHandler` to subclass `GenericCollectionHandler`
- [x] 3.3 Migrate `MovieClipHandler` to subclass `GenericCollectionHandler`
- [x] 3.4 Migrate `CacheFileHandler` to subclass `GenericCollectionHandler`
- [x] 3.5 Run test suite to verify batch 2

## 4. Migrate Type-Filtered Handlers (Batch 3)

- [x] 4.1 Migrate `LightProbeHandler` to subclass `GenericCollectionHandler` — preserve type filter in `list_items()` override
- [x] 4.2 Migrate `BrushHandler` to subclass `GenericCollectionHandler` — preserve mode filter in `list_items()` override
- [x] 4.3 Run test suite to verify batch 3

## 5. Migrate Richer Simple Handlers (Batch 4)

- [x] 5.1 Migrate `SpeakerHandler` to subclass `GenericCollectionHandler`
- [x] 5.2 Migrate `PaletteHandler` to subclass `GenericCollectionHandler`
- [x] 5.3 Migrate `LatticeHandler` to subclass `GenericCollectionHandler`
- [x] 5.4 Migrate `PaintCurveHandler` to subclass `GenericCollectionHandler`
- [x] 5.5 Migrate `AnnotationHandler` to subclass `GenericCollectionHandler`
- [x] 5.6 Migrate `LibraryHandler` to subclass `GenericCollectionHandler`
- [x] 5.7 Run test suite to verify batch 4

## 6. Merge TextHandler / FontHandler

- [x] 6.1 Extract shared `_FontCurveHandler` base class (or make `TextHandler` a thin subclass of `FontHandler`) in `core_handlers.py`, eliminating duplicated method bodies
- [x] 6.2 Verify both `DataType.TEXT` and `DataType.FONT` remain registered and dispatch correctly
- [x] 6.3 Run test suite to verify merge

## 7. Extract Dispatcher `_resolve_handler()` Helper

- [x] 7.1 Add `_resolve_handler(payload, started)` function in `data/dispatcher.py` that performs bpy check, type parsing, and handler lookup
- [x] 7.2 Refactor `data_create`, `data_read`, `data_write`, `data_delete`, `data_list` to use `_resolve_handler()`
- [x] 7.3 Run test suite to verify dispatcher refactor

## 8. Extract Shared VIEW_3D Context Override Utility

- [x] 8.1 Create `handlers/context_utils.py` with `get_view3d_override(bpy)` function
- [x] 8.2 Replace inline VIEW_3D override code in `physics/handler.py` with import from `context_utils`
- [x] 8.3 Replace inline VIEW_3D override code in `uv/handler.py` with import from `context_utils`
- [x] 8.4 Replace inline VIEW_3D override code in `importexport/handler.py` with import from `context_utils`
- [x] 8.5 Skip — `info/query.py` uses a structurally different pattern (iterates `screen.areas` + accesses `space.shading`) with import from `context_utils`
- [x] 8.6 Run test suite to verify context_utils refactor

## 9. Dead Code Removal and Pathfix Consolidation

- [x] 9.1 Remove unused `_PHYSICS_OPERATOR_MAP` dict from `physics/handler.py`
- [x] 9.2 Create shared `_pathfix.py` at repo root with ROOT + SRC path setup
- [x] 9.3 Replace `examples/_pathfix.py` with re-export from root `_pathfix.py`
- [x] 9.4 Replace `tests/_pathfix.py` with re-export from root `_pathfix.py`
- [x] 9.5 Update `scripts/_pathfix.py` to re-export from root `_pathfix.py`
- [x] 9.6 Run test suite and verify examples still work: `python -m examples.stdio_loop`

## 10. Final Verification

- [x] 10.1 Run full test suite: `uv run python -m unittest discover -s tests -p "test_*.py"`
- [x] 10.2 Verify `data/__init__.py` imports — all 36 handler classes registered correctly
- [x] 10.3 Spot-check: -1,645 / +217 lines across 17 files in `handlers/data/`
