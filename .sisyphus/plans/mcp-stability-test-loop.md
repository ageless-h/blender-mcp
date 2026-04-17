# MCP Stability Test Loop

## Mission

You are running an autonomous MCP stability test loop. Your goal is to continuously test the blender-mcp server by exercising its 29 tools through real Blender GUI sessions, detecting crashes, hangs, and edge cases, and documenting all findings as GitHub issues.

## Loop Lifecycle

Each iteration follows this pattern:

```
┌─────────────────────────────────────────────────────────────┐
│  1. STARTUP: Launch Blender GUI                             │
│     - open -a Blender                                        │
│     - Wait 3-5 seconds for initialization                    │
│     - Verify MCP connection via blender_get_scene            │
├─────────────────────────────────────────────────────────────┤
│  2. EXPLORATION: Random/strategic tool execution             │
│     - Pick 1-5 tools to exercise                             │
│     - Create diverse objects, materials, animations          │
│     - Test edge cases (long names, special chars, extremes)  │
│     - Test error paths (non-existent objects, invalid params)│
│     - Monitor for: crashes, hangs, memory leaks, errors      │
├─────────────────────────────────────────────────────────────┤
│  3. CLEANUP: Save state & prepare for next iteration         │
│     - Save to /tmp/mcp_test_session_{timestamp}.blend        │
│     - Delete files older than 1 hour (prevent disk bloat)    │
│     - Clean /tmp/mcp_test_*.blend (keep max 10 files)        │
├─────────────────────────────────────────────────────────────┤
│  4. SHUTDOWN: Graceful exit                                  │
│     - wm.quit_blender via MCP                                │
│     - If MCP unresponsive: pkill -f Blender                  │
│     - Verify process terminated                              │
├─────────────────────────────────────────────────────────────┤
│  5. DOCUMENT: Record findings                                │
│     - If issue found: create GitHub issue                    │
│     - Update test log with iteration summary                 │
│     - Commit findings to repo                                │
└─────────────────────────────────────────────────────────────┘
```

## Tool Exercise Strategy

### Layer 1: Perception Tools (11 tools)
Test these for data accuracy and edge cases:
- `blender_get_objects` - Empty scene, 100+ objects, filtered queries
- `blender_get_object_data` - All include options, missing objects
- `blender_get_node_tree` - All 6 contexts, empty trees, complex graphs
- `blender_get_animation_data` - Animated objects, NLA, drivers
- `blender_get_materials` - Unused materials, PBR values
- `blender_get_scene` - All include options
- `blender_get_collections` - Deep hierarchies
- `blender_get_armature_data` - Complex rigs
- `blender_get_images` - Missing images, packed images
- `blender_capture_viewport` - All shading modes
- `blender_get_selection` - Various selection states

### Layer 2: Declarative Write Tools (4 tools)
Test for crash-inducing operations:
- `blender_edit_nodes` - Invalid node types, circular connections
- `blender_edit_animation` - Invalid keyframes, driver expressions
- `blender_edit_sequencer` - VSE operations
- `blender_edit_mesh` - Destructive mesh operations

### Layer 3: Imperative Write Tools (10 tools)
Test for state corruption:
- `blender_create_object` - All types, extreme parameters
- `blender_modify_object` - Parent loops, invalid transforms
- `blender_manage_material` - Material assignment edge cases
- `blender_manage_modifier` - Modifier stack corruption
- `blender_manage_collection` - Collection hierarchy corruption
- `blender_manage_uv` - UV operations on non-mesh
- `blender_manage_constraints` - Constraint conflicts
- `blender_manage_physics` - Physics simulation edge cases
- `blender_setup_scene` - Render settings corruption
- `blender_edit_mesh` - Topology corruption

### Layer 4: Fallback Tools (5 tools)
Test for security and sandbox violations:
- `blender_execute_operator` - Dangerous operators
- `blender_execute_script` - (Should be blocked by security)
- `blender_import_export` - Corrupted files, huge files
- `blender_render_scene` - Render crashes
- `blender_batch_execute` - Batch failures

## Edge Cases to Test

### Input Validation
- [ ] Empty strings for required parameters
- [ ] Unicode characters in names (中文, emoji, RTL)
- [ ] Extremely long names (1000+ chars)
- [ ] Special characters: `/ \ : * ? " < > |`
- [ ] Negative values for positive-only parameters
- [ ] Array bounds: vec3 with 2 or 4 elements
- [ ] Null/None values
- [ ] Circular references (object parent loops)

### State Corruption
- [ ] Operations on deleted objects
- [ ] Concurrent modifications
- [ ] Undo/redo during MCP operations
- [ ] Scene changes while iterating

### Resource Limits
- [ ] 1000+ objects in scene
- [ ] Deep collection hierarchies (50+ levels)
- [ ] Large meshes (1M+ vertices)
- [ ] Many materials (100+)
- [ ] Long animation timelines (10000+ frames)

### Error Recovery
- [ ] MCP connection loss mid-operation
- [ ] Blender crash recovery
- [ ] Invalid operator parameters
- [ ] File permission errors

## Issue Documentation Format

When an issue is found, create a GitHub issue with:

```markdown
## Summary
[One-line description]

## Reproduction Steps
1. Start Blender GUI
2. Execute MCP command: [exact command]
3. [Additional steps]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened - crash, error, hang]

## Environment
- Blender version: [from blender_get_scene]
- MCP version: [from git log -1]
- macOS version: [sw_vers]
- Iteration: #[N]

## Logs
```
[MCP tool output or error messages]
```

## Additional Context
[Any relevant context]
```

## Cleanup Rules

**CRITICAL: Prevent disk bloat**

1. After each iteration, delete test files older than 1 hour:
   ```bash
   find /tmp -name "mcp_test_*.blend" -mmin +60 -delete
   ```

2. Keep maximum 10 test files:
   ```bash
   ls -t /tmp/mcp_test_*.blend | tail -n +11 | xargs rm -f
   ```

3. Clean any temp directories created:
   ```bash
   rm -rf /tmp/blender_temp_* 2>/dev/null
   ```

## Failure Detection

### Crash Detection
- MCP tool call returns connection error
- `pgrep -f Blender` returns empty after tool call
- Tool call hangs for >30 seconds

### Hang Detection
- Tool execution time >60 seconds (use timeout)
- Blender UI frozen (can't verify programmatically)

### Memory Leak Detection
- Monitor process memory: `ps -o rss= -p <pid>`
- Alert if memory grows >500MB per iteration

## Loop State Tracking

Create and maintain `/tmp/mcp_test_state.json`:

```json
{
  "iteration": 0,
  "total_tests": 0,
  "crashes": 0,
  "hangs": 0,
  "errors": [],
  "issues_created": [],
  "last_successful_tool": null,
  "start_time": "2026-04-17T23:00:00Z",
  "blender_pid": null
}
```

Update this file after each iteration.

## Completion Criteria

This loop runs indefinitely until manually cancelled (`/cancel-ralph`). 

Each iteration should:
1. Make progress on testing different tools/edge cases
2. Document any findings as GitHub issues
3. Clean up resources
4. Commit findings to the repository

**Do NOT output completion promise** - this is an infinite monitoring loop.

## Starting Instructions

1. Read `/tmp/mcp_test_state.json` to resume from last state (or create new)
2. Start Blender GUI
3. Begin iteration from where you left off
4. Rotate through tools systematically to ensure coverage
5. Document all findings
6. Never stop unless cancelled
