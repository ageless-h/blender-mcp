# Real-Scenario Test Plan — v1.2.0

**Environment**: Blender 5.1.0, macOS, OpenCode/Claude Code
**Branch**: test/real-scenario
**Date**: 2026-04-13

---

## Pre-flight Checklist

- [ ] Install addon v1.2.0 to Blender 5.1
- [ ] Install MCP server (`uv pip install -e .`)
- [ ] Configure MCP client (OpenCode/Claude)
- [ ] Start Blender, enable addon, start server
- [ ] Verify MCP status appears in bottom status bar ("MCP ● Offline" or "MCP ● N req")

---

## T1: Connection & Baseline (must pass first)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T1.1 | Get scene info | `blender_get_scene` | Returns stats with blender version 5.1 |
| T1.2 | List objects | `blender_get_objects` | Returns default cube + light + camera |
| T1.3 | Get selection | `blender_get_selection` | Returns current mode + active object |
| T1.4 | UI shows status | Manual | Statusbar shows "MCP ● N req 0 err" (global, all editors) |

---

## T2: Dynamic Timeout (v1.2.0 new)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T2.1 | Fast query completes < 10s | `blender_get_scene` | Returns in < 1s (fast tier) |
| T2.2 | Standard operation | `blender_create_object` | Creates cube, completes < 60s |
| T2.3 | Timeout error includes capability name | Manual (force) | Error message says "timed out after Xs for blender.xxx" |

---

## T3: UI — Statusbar + Popup Panel (v1.2.0 new)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T3.1 | Statusbar shows MCP status | Manual | Bottom bar shows "MCP ● N req M err" when running |
| T3.2 | Popup panel opens | Ctrl+Shift+M | Dialog shows server status + activity log |
| T3.3 | Click statusbar opens popup | Manual click | Same popup dialog as hotkey |
| T3.4 | Request counter increments | `blender_get_scene` x3 | Counter shows "3 req" |
| T3.5 | Error counter increments | Trigger error (bad object name) | Counter shows "1 err" |
| T3.6 | Log entry icons correct | 1 success + 1 error | CHECKMARK for success, ERROR for failure |
| T3.7 | Filter log entries | Type in filter box | Only matching entries shown |
| T3.8 | i18n follows Blender language | Switch to Chinese | Labels show Chinese text |

---

## T4: Multi-Connection (v1.2.0 new)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T4.1 | Single connection works | Any tool via MCP client | Works normally |
| T4.2 | Two connections simultaneously | Two terminal `python -c "import socket..."` | Both get responses |
| T4.3 | Client disconnect doesn't kill server | Connect + disconnect + query again | Server continues working |

---

## T5: Dynamic Node Query (v1.2.0 new)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T5.1 | Query all node types | `blender_get_scene` with `type: node_types` | Returns list with count > 50 |
| T5.2 | Filter by prefix "Shader" | `type: node_types, params: {prefix: "Shader"}` | Only ShaderNode* types |
| T5.3 | Dynamic resolution works | `blender_edit_nodes` with type from query | Node created successfully |
| T5.4 | Fallback to static map | Disconnect bpy, resolve "Principled BSDF" | Still resolves to ShaderNodeBsdfPrincipled |

---

## T6: Perception Layer (all 11 tools)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T6.1 | Get objects with filter | `blender_get_objects` type_filter=MESH | Only mesh objects |
| T6.2 | Get object data deep | `blender_get_object_data` includes=modifiers,materials | Returns nested data |
| T6.3 | Get node tree (shader) | `blender_get_node_tree` tree_type=SHADER context=OBJECT target=Material | Returns Principled BSDF + Material Output |
| T6.4 | Get animation data | `blender_get_animation_data` | Returns keyframes/NLA (may be empty) |
| T6.5 | Get materials list | `blender_get_materials` | Returns materials in file |
| T6.6 | Get collections | `blender_get_collections` | Returns collection tree |
| T6.7 | Get armature data | Create armature first, then query | Returns bone hierarchy |
| T6.8 | Get images | `blender_get_images` | Returns image list |
| T6.9 | Capture viewport | `blender_capture_viewport` | Returns base64 image (compressed) |
| T6.10 | Get selection after select | Select cube, then `blender_get_selection` | Returns "Cube" as active |

---

## T7: Imperative Write Layer (9 tools)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T7.1 | Create object | `blender_create_object` type=MESH primitive=cube | Cube appears in viewport |
| T7.2 | Modify object transform | `blender_modify_object` location=[0,0,2] | Object moves up |
| T7.3 | Create material | `blender_manage_material` action=create base_color=[1,0,0,1] | Red material created |
| T7.4 | Assign material | `blender_manage_material` action=assign | Material assigned to object |
| T7.5 | Add modifier | `blender_manage_modifier` action=add type=SUBSURF | Subsurf modifier added |
| T7.6 | Configure modifier | `blender_manage_modifier` action=configure settings={levels: 2} | Subdivision levels set |
| T7.7 | Create collection | `blender_manage_collection` action=create | New collection created |
| T7.8 | Link object to collection | `blender_manage_collection` action=link_object | Object linked |
| T7.9 | Add constraint | `blender_manage_constraints` action=add type=TRACK_TO | Constraint added |
| T7.10 | Manage physics | `blender_manage_physics` action=add physics_type=RIGID_BODY | Rigid body added |
| T7.11 | Setup scene | `blender_setup_scene` engine=CYCLES resolution_x=1920 | Scene settings updated |
| T7.12 | UV unwrap | `blender_manage_uv` action=smart_project | UV unwrapped |

---

## T8: Declarative Write Layer (3 tools)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T8.1 | Edit nodes: add node | `blender_edit_nodes` action=add_node | Noise Texture node added |
| T8.2 | Edit nodes: connect | `blender_edit_nodes` action=connect | Nodes linked |
| T8.3 | Edit nodes: set_value | `blender_edit_nodes` action=set_value value=0.5 | Value set |
| T8.4 | Edit animation: insert keyframe | `blender_edit_animation` action=insert_keyframe | Keyframe inserted |
| T8.5 | Edit sequencer: add strip | `blender_edit_sequencer` action=add_strip | VSE strip added (may fail on 5.1 timer context) |

---

## T9: Fallback Layer (3 tools)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T9.1 | Execute operator | `blender_execute_operator` operator=object.shade_smooth | Object shaded smooth |
| T9.2 | Execute script | `blender_execute_script` code="import bpy; bpy.data.objects[0].name='TestCube'" | Object renamed |
| T9.3 | Import/Export | `blender_import_export` action=export format=FBX filepath=/tmp/test.fbx | File exported |

---

## T10: Error Suggestions (v1.1 feature, verify in v1.2)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T10.1 | Not found error has suggestion | Query non-existent object | Error includes suggestion like "Use blender_get_objects to list" |
| T10.2 | Timeout error has suggestion | Force timeout | Error includes suggestion |
| T10.3 | All errors have suggestion field | Various failures | `suggestion` field present |

---

## T11: Screenshot Compression (v1.1 feature, verify in v1.2)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T11.1 | Default thumbnail=true | `blender_capture_viewport` | Returns compressed image |
| T11.2 | Full size capture | `blender_capture_viewport` thumbnail=false | Returns full resolution |
| T11.3 | Thumbnail is smaller | Compare sizes | Thumbnail base64 < 50KB |

---

## T12: Property Parser (v1.1 feature, verify in v1.2)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T12.1 | Set color via hex | `blender_edit_nodes` set_value value="#ff0000" | Color set to red |
| T12.2 | Set vector via string | `blender_edit_nodes` set_value value=[1,0,0] | Vector set |
| T12.3 | Set property on object | `blender_modify_object` via coerce | Property coerced correctly |

---

## T13: Blender 5.0 Animation API (v1.1 feature, verify in v1.2)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T13.1 | Read keyframes | `blender_get_animation_data` on animated object | Works on 5.1 layered API |
| T13.2 | Insert keyframe | `blender_edit_animation` | Keyframe inserted via compatible API |

---

## T14: Watchdog (v1.1 feature, verify in v1.2)

| # | Test | Tool | Expected |
|---|------|------|----------|
| T14.1 | Server survives file load | File > New, then query | Still responds |
| T14.2 | Server survives undo | Ctrl+Z multiple times, then query | Still responds |

---

## Installation Steps

### 1. Install Addon to Blender 5.1

```bash
# Remove old addon
rm -rf ~/Library/Application\ Support/Blender/5.1/scripts/addons/blender_mcp_addon

# Copy new addon
cp -r /Users/huzhiheng/code/blender-mcp/blender-mcp-test-real/src/blender_mcp_addon \
      ~/Library/Application\ Support/Blender/5.1/scripts/addons/blender_mcp_addon
```

### 2. Install MCP Server

```bash
cd /Users/huzhiheng/code/blender-mcp/blender-mcp-test-real
uv sync
uv pip install -e .
```

### 3. Configure MCP Client (OpenCode)

Add to OpenCode config:
```json
{
  "mcpServers": {
    "blender": {
      "command": "uv",
      "args": ["run", "python", "-m", "blender_mcp.mcp_protocol"],
      "cwd": "/Users/huzhiheng/code/blender-mcp/blender-mcp-test-real"
    }
  }
}
```

### 4. Start Test

1. Open Blender 5.1
2. Edit > Preferences > Add-ons > Enable "Blender MCP"
3. Statusbar shows "MCP" — click it or press Ctrl+Shift+M > Start Server
4. In OpenCode: `blender_get_scene` to verify connection
