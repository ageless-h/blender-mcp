# Tool Schema Optimization — Implementation Tasks

## Phase 1: Foundation (Schema Layer + Payload Flattening) ✅ DONE

### Task 1.1: Create schema registry module ✅
- Created `src/blender_mcp/schemas/tools.py` with all 26 tool definitions
- Created `src/blender_mcp/schemas/__init__.py` with exports

### Task 1.2: Flatten payload in mcp_protocol.py ✅
- Removed `payload` wrapper from `inputSchema` generation
- Updated `tools_call()` to read arguments directly (flat params)
- Legacy clients sending `{"payload": {...}}` are unwrapped transparently

### Task 1.3: Add blender_ prefix and new tool name routing ✅
- All 26 tools use `blender_` prefix
- Legacy name map in `mcp_protocol.py` (`_LEGACY_TOOL_MAP`)
- Both old (`data.read`, `data_read`) and new names work

### Task 1.4: Write JSON Schemas for all 26 tools ✅
- Hand-written schemas in `src/blender_mcp/schemas/tools.py`
- Includes descriptions, enums, defaults, constraints, additionalProperties:false

### Task 1.5: Add tool annotations ✅
- All 26 tools have readOnlyHint, destructiveHint, idempotentHint, openWorldHint
- Perception tools: readOnly=true, idempotent=true
- execute_script: destructive=true
- import_export: openWorld=true

---

## Phase 2: Perception Layer (Read Tools) ✅ DONE

### Task 2.1: blender_get_objects ✅
- Routes to data_list with type=object + payload filters
- Schema has type_filter, collection, selected_only, visible_only, name_pattern

### Task 2.2: blender_get_object_data ✅
- Routes to data_read with type=object
- Schema has name, include array, properties path

### Task 2.3: blender_get_node_tree [NEW HANDLER] ✅
- Created `handlers/nodes/reader.py` with `node_tree_read()`
- Supports SHADER (object/world/linestyle), COMPOSITOR, GEOMETRY contexts
- Returns unified {nodes, links} with summary/full depth

### Task 2.4: blender_get_animation_data [NEW HANDLER] ✅
- Created `handlers/animation/reader.py` with `animation_read()`
- Reads keyframes, fcurves, NLA strips, drivers, shape keys
- Supports frame_range filtering and include selection

### Task 2.5: blender_get_materials ✅
- Routes to data_list with type=material

### Task 2.6: blender_get_scene ✅
- Routes to info_query with type=scene_stats

### Task 2.7: blender_get_collections ✅
- Routes to data_read with type=collection

### Task 2.8: blender_get_armature_data ✅
- Routes to data_read with type=armature

### Task 2.9: blender_get_images [NEW HANDLER] ✅
- Added `image_list()` to `handlers/data/image_handler.py`
- Supports filter modes: all/packed/external/missing/unused + name_pattern

### Task 2.10: blender_capture_viewport ✅
- Routes to info_query with type=viewport_capture

### Task 2.11: blender_get_selection ✅
- Routes to info_query with type=selection

---

## Phase 3: Declarative Write Layer ✅ DONE

### Task 3.1: blender_edit_nodes [NEW HANDLER] ✅
- Created `handlers/nodes/editor.py` with `node_tree_edit()`
- Implements: add_node, remove_node, connect, disconnect, set_value, set_property
- Supports all node tree contexts via shared `_resolve_node_tree()`
- Batch execution with per-operation success/failure tracking

### Task 3.2: blender_edit_animation [NEW HANDLER] ✅
- Created `handlers/animation/editor.py` with `animation_edit()`
- Implements: insert/delete/modify keyframe, NLA strip CRUD, driver add/remove, shape key control, set_frame, set_frame_range

### Task 3.3: blender_edit_sequencer [NEW HANDLER] ✅
- Created `handlers/sequencer/editor.py` with `sequencer_edit()`
- Implements: add/modify/delete strips, add_effect, add_transition, move_strip
- Supports: VIDEO, IMAGE, AUDIO, TEXT, COLOR, ADJUSTMENT strip types

---

## Phase 4: Imperative Write Layer ✅ DONE

### Task 4.1: blender_create_object ✅
- Routes to data_create with type=object
- Schema supports all object types via object_type enum

### Task 4.2: blender_modify_object ✅
- Routes to data_write (or data_delete when delete=true)
- Schema supports property modification and deletion

### Task 4.3: blender_manage_material ✅
- Dispatches by action: create→data_create, delete→data_delete, assign/unassign→data_link, edit→data_write

### Task 4.4: blender_manage_modifier ✅
- Dispatches by action: add→data_create, remove→data_delete, configure→data_write, apply/move→operator_execute

### Task 4.5: blender_manage_collection ✅
- Dispatches by action: create→data_create, delete→data_delete, link/unlink→data_link, visibility→data_write, parent→data_link

### Task 4.6: blender_manage_uv [NEW HANDLER] ✅
- Created `handlers/uv/handler.py` with `uv_manage()`
- Implements: mark/clear seam, unwrap, smart_project, cube/cylinder/sphere project, lightmap_pack, pack_islands, average_island_scale, add/remove/set_active UV map
- Handles edit mode entry/exit automatically

### Task 4.7: blender_manage_constraints [NEW HANDLER] ✅
- Created `handlers/constraints/handler.py` with `constraints_manage()`
- Supports both object and bone constraints (Armature/BoneName syntax)
- Implements: add, configure, remove, enable, disable, move_up, move_down

### Task 4.8: blender_manage_physics [NEW HANDLER] ✅
- Created `handlers/physics/handler.py` with `physics_manage()`
- Supports: rigid body, cloth, soft body, fluid (domain/flow), particle, force field
- Implements: add, configure, remove, bake, free_bake

### Task 4.9: blender_setup_scene [NEW HANDLER] ✅
- Created `handlers/scene/config.py` with `scene_setup()`
- Handles: engine, samples, resolution, output format/path, film, denoising, world background, timeline/FPS

---

## Phase 5: Fallback Layer ✅ DONE

### Task 5.1: blender_execute_operator ✅
- Reuses existing operator_execute handler
- Schema has operator, params, context fields (flat)

### Task 5.2: blender_execute_script ✅
- Reuses existing script_execute handler
- Schema has code field (flat)

### Task 5.3: blender_import_export [NEW HANDLER] ✅
- Created `handlers/importexport/handler.py` with `import_export()`
- Maps format enum to specific import/export operators
- Supports: FBX, OBJ, GLTF, GLB, USD, USDC, USDA, ALEMBIC, STL, PLY, SVG, DAE, X3D

---

## Phase 6: Integration & Cleanup ✅ DONE

### Task 6.1: Update catalog.py ✅
- Updated minimal_capability_set descriptions to reference new tool names as [LEGACY]
- Updated new_tool_scope_map with all 26 blender.* capability scopes

### Task 6.2: Update mcp_protocol.py ✅
- Complete rewrite to use schema registry for tool listing
- Flat params with legacy payload unwrapping
- Legacy tool name resolution via _LEGACY_TOOL_MAP
- Added prompts/list and prompts/get JSON-RPC methods

### Task 6.3: Update capabilities/base.py ✅
- Added `_dispatch_new_capability()` for all 26 blender.* capabilities
- Reuses existing handlers where possible, lazy-imports new handlers
- Legacy capability routing preserved

### Task 6.4: Add MCP Prompts ✅
- Created `src/blender_mcp/prompts/registry.py` with 7 prompt definitions
- All 7 prompts implemented with structured PromptMessages
- Registered prompts capability in server initialization

### Task 6.5: Testing ✅
- Updated `tests/mcp/test_registration.py` with 14 tests (all passing)
- Tests cover: 26 tools, annotations, flat schemas, prompts, legacy names, cross-references

### Task 6.6: Documentation
- Pending: README update with new tool list

---

## Priority & Dependencies

```
Phase 1 (Foundation)      ← Must be first, everything depends on this
  ↓
Phase 2 (Read)            ← Can be parallel with Phase 4
Phase 4 (Imperative Write)← Can be parallel with Phase 2
  ↓
Phase 3 (Declarative Write) ← Depends on node/animation handler patterns from Phase 2
Phase 5 (Fallback)          ← Depends on Phase 1 only
  ↓
Phase 6 (Integration)     ← Last, depends on all above
```

## Estimated Effort

| Phase | Tools | New Handlers | Effort |
|-------|-------|-------------|--------|
| 1. Foundation | 0 | 0 | Medium (schema infra + routing) |
| 2. Perception | 11 | 4 | High (NodeTreeReader, AnimationReader, ImageReader, ArmatureExtend) |
| 3. Declarative | 3 | 3 | Very High (NodeTreeEditor, AnimationEditor, SequencerEditor) |
| 4. Imperative | 9 | 4 | High (UVHandler, ConstraintHandler, PhysicsHandler, SceneConfig) |
| 5. Fallback | 3 | 0 | Low (schema only, reuse handlers) |
| 6. Integration | 0 | 0 | Medium (wiring + testing + docs) |
