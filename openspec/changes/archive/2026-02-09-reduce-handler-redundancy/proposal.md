## Why

The `handlers/data/` directory contains ~20 handler files where at least 15 follow a near-identical boilerplate pattern. The `write()`, `delete()`, and `list_items()` methods are structurally identical across these handlers — only the bpy.data collection name and a few read-summary fields differ. This results in ~1,500+ lines of mechanically duplicated code that inflates maintenance cost, increases bug surface area, and makes onboarding harder. Additionally, `TextHandler` and `FontHandler` are near-complete duplicates operating on the same `bpy.data.curves` collection with `type == "FONT"`.

## What Changes

- **Introduce `GenericCollectionHandler`** — a concrete base class in `handlers/base.py` that provides default implementations for `write()`, `delete()`, `list_items()`, and `read(path=...)` delegation. Simple handlers subclass it and only override `_read_summary()`, `_list_fields()`, and optionally `create()`.
- **Collapse ~15 simple handler files** (surface, volume, sound, movieclip, cachefile, mask, workspace, light_probe, speaker, paintcurve, annotation, library, palette, lattice, brush) into minimal subclasses of `GenericCollectionHandler` (~20 lines each instead of ~120).
- **Merge `TextHandler` into `FontHandler`** — `TextHandler` delegates to `FontHandler` or both share a single implementation, eliminating ~90 lines of duplication.
- **Extract `_resolve_handler()` helper in dispatcher** — the 5 dispatcher functions (`data_create/read/write/delete/list`) share a ~12-line preamble for bpy check + type parsing + handler lookup. Extract to a single helper.
- **Extract shared `get_view3d_context_override()` utility** — the same ~10-line VIEW_3D area/region lookup is copy-pasted in `physics/handler.py`, `uv/handler.py`, `importexport/handler.py`, and `info/query.py`.
- **Remove dead `_PHYSICS_OPERATOR_MAP`** in `physics/handler.py` — defined but never referenced.
- **Deduplicate `_pathfix.py`** — `examples/_pathfix.py` and `tests/_pathfix.py` are byte-identical; consolidate into a single shared module.

## Capabilities

### New Capabilities

- `generic-handler-base`: Defines the contract for `GenericCollectionHandler` — the default CRUD method implementations, the override hooks (`_read_summary`, `_list_fields`), and the invariant that all existing handler behavior is preserved through the refactor.

### Modified Capabilities

_(None — all changes are implementation-level refactoring. No spec-level behavioral requirements change. The `blender-data-types` handler registry pattern, response envelope, and external tool behavior remain identical.)_

## Impact

- **Code**: `src/blender_mcp_addon/handlers/` — base.py gains `GenericCollectionHandler`; ~15 handler files in `data/` shrink dramatically; `data/dispatcher.py` gains `_resolve_handler()`; new shared utility module for VIEW_3D context override; `data/core_handlers.py` merges Text/Font; `physics/handler.py` loses dead map.
- **Tests**: Existing handler tests must continue to pass (regression). New tests for `GenericCollectionHandler` default methods.
- **APIs**: No external API changes. MCP tool schemas, response envelopes, and capability names are unchanged.
- **Risk**: Low — pure internal refactoring behind stable `BaseHandler` interface. Each collapsed handler can be verified by running the existing test suite.
