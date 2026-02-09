## Why

The handler system has ~460 lines of duplicated code across data handlers: mesh primitive creation is copy-pasted verbatim between `MeshHandler` and `ObjectHandler` (~50 lines); object-linking-to-scene boilerplate is repeated in 7 handlers (~84 lines); "find objects referencing this data block" scanning logic is duplicated in Camera/Light reads (~30 lines); and 4 handlers (`LightHandler`, `TextureHandler`, `WorldHandler`, `SceneHandler`) fully reimplement CRUD methods that `GenericCollectionHandler` already provides, only because it lacks two small hooks — filtered `list_items` and custom `write` property handling. This change extracts shared utilities and adds minimal hooks to `GenericCollectionHandler` so these handlers can be migrated, eliminating the duplication without introducing new abstractions.

## What Changes

- Extract `create_mesh_primitive(mesh, primitive, params)` utility function from the identical bmesh dispatch code in `MeshHandler.create()` and `ObjectHandler._create_mesh_primitive()`
- Extract `link_data_to_scene(data_block, params)` utility function to replace the ~12-line object-linking boilerplate duplicated in 7 handler `create()` methods (Camera, Light, Curve, MetaBall, GreasePencil, FontCurve, Mesh)
- Extract `find_referencing_objects(data_block, object_type)` utility function to replace the duplicated scanning logic in Camera and Light read summaries
- Add `_filter_item(item, filter_params) -> bool` optional hook to `GenericCollectionHandler.list_items()` so subclasses can declare filtering without overriding the entire method
- Add `_custom_write(item, prop_path, value) -> bool` optional hook to `GenericCollectionHandler.write()` so subclasses can handle special properties (e.g., color tuples, node-tree-backed properties) without overriding the entire method
- Migrate `LightHandler`, `TextureHandler`, `WorldHandler`, `SceneHandler` from `BaseHandler` to `GenericCollectionHandler`, keeping only `create()`, `_read_summary()`, `_list_fields()`, and the new hooks where needed

## Capabilities

### New Capabilities

- `handler-shared-utilities`: Shared utility functions for handler implementations — mesh primitive creation, object-to-scene linking, and data-block reference scanning

### Modified Capabilities

- `generic-handler-base`: Add `_filter_item()` and `_custom_write()` optional hooks to `GenericCollectionHandler` to support filtered listing and special property writes without full method overrides

## Impact

- **Code**: `src/blender_mcp_addon/handlers/` — new utilities module, `base.py` (GenericCollectionHandler hooks), `data/core_handlers.py` (Light/World/Font migration), `data/texture_handler.py`, `data/scene_handler.py`, `data/mesh_handler.py`, `data/object_handler.py`
- **APIs**: No external API changes. All CRUD operations produce identical return values before and after migration.
- **Tests**: Existing handler tests must continue to pass. New unit tests for the 3 utility functions and 2 new hooks.
- **Dependencies**: None. Pure internal refactor.
