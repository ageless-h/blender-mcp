# MCP Stability Test Loop - Real-World Scenarios

## Mission

You are running an autonomous MCP stability test loop. Your goal is to test the blender-mcp server through **realistic, complex Blender workflows** that mimic actual user tasks. Each iteration simulates a different real-world scenario, from game asset creation to architectural visualization.

**Key Principle**: Test like a real user, not like a unit test. Real users don't just call tools randomly - they have goals, workflows, and make mistakes.

---

## Real-World Test Scenarios

### Scenario 1: Low-Poly Game Asset Creation (Iterative)

**Goal**: Create a stylized low-poly character or prop for a game

**Workflow**:
```
1. Create base mesh (cube/sphere)
2. Apply subdivision modifier, then decimate for low-poly look
3. Create and assign material with specific PBR values
4. Add simple animation (idle bobbing, rotation)
5. Set up camera and lighting
6. Capture viewport to verify visual result
7. Export as FBX/GLTF
8. Clean up and close
```

**What to Test**:
- Modifier stack operations (add, configure, apply order)
- Material creation with PBR values (roughness, metallic, emission)
- Keyframe animation with interpolation
- Camera and light setup
- Export functionality
- Visual verification via viewport capture

**Edge Cases**:
- Apply modifier without applying previous ones
- Export with non-ASCII characters in name
- Animation on deleted objects
- Material assignment to multiple objects

---

### Scenario 2: Architectural Visualization Setup

**Goal**: Set up a simple architectural scene with furniture and lighting

**Workflow**:
```
1. Create room (plane → extrude → solidify)
2. Create furniture (multiple primitives with transforms)
3. Set up 3-point lighting (key, fill, back)
4. Configure render settings (Cycles, samples, resolution)
5. Create collection hierarchy for organization
6. Assign different materials to different objects
7. Set up camera with proper framing
8. Render preview
```

**What to Test**:
- Complex transform operations (location, rotation, scale)
- Collection management (create, link, hierarchy)
- Multiple light types (POINT, SUN, SPOT, AREA)
- Render engine configuration
- Scene organization patterns

**Edge Cases**:
- Deep collection nesting (10+ levels)
- Parent-child loops
- Scale of 0 on any axis
- Negative scale (mirroring)

---

### Scenario 3: Animation Rigging and Motion Test

**Goal**: Create a simple rig and animate an object

**Workflow**:
```
1. Create armature with multiple bones
2. Create mesh and parent to armature
3. Add constraints to bones (IK, track-to)
4. Create pose animation
5. Set up NLA strips for animation layers
6. Test shape keys
7. Bake animation
8. Play back and verify
```

**What to Test**:
- Armature and bone operations
- Object parenting and constraints
- IK chain setup
- Animation layering (NLA)
- Shape key creation and animation
- Animation baking

**Edge Cases**:
- Constraint conflicts (multiple IK on same chain)
- Animation on non-animated properties
- Shape key on mesh without data
- Driver expressions with invalid Python

---

### Scenario 4: Node-Based Material Creation

**Goal**: Create a complex procedural material using nodes

**Workflow**:
```
1. Create new material
2. Read default node tree
3. Add multiple nodes (noise, color ramp, mix, etc.)
4. Connect nodes in specific pattern
5. Set node values and properties
6. Assign to object
7. Capture rendered viewport
8. Modify and iterate
```

**What to Test**:
- Node tree reading and parsing
- Node addition with correct types
- Node connection patterns
- Value setting on different socket types
- Property setting on nodes
- Complex node graphs (20+ nodes)

**Edge Cases**:
- Connecting incompatible sockets
- Circular node connections
- Adding nodes that don't exist
- Setting values with wrong types
- Deleting nodes that are connected

---

### Scenario 5: Batch Processing and Stress Test

**Goal**: Test MCP under heavy load

**Workflow**:
```
1. Create 50+ objects in batch
2. Apply modifiers to all
3. Create materials for each
4. Assign materials in batch
5. Animate all objects
6. Organize into collections
7. Query all object data
8. Export scene
```

**What to Test**:
- `blender_batch_execute` for parallel operations
- Large scene handling
- Memory usage during operations
- Response time degradation
- Error recovery on batch failures

**Edge Cases**:
- Batch operation with one failing item
- Memory exhaustion
- Timeout on long operations
- Race conditions in parallel operations

---

### Scenario 6: Error Recovery and Corruption Test

**Goal**: Intentionally cause errors and verify recovery

**Workflow**:
```
1. Create objects with valid names
2. Try operations on non-existent objects
3. Try invalid parameter values
4. Create circular references (parent loops)
5. Delete objects mid-animation
6. Try to read deleted object data
7. Verify error messages are helpful
8. Continue with valid operations
```

**What to Test**:
- Error message clarity
- State recovery after errors
- Blender doesn't crash on bad input
- MCP connection remains stable
- Partial operation failures don't corrupt state

**Edge Cases**:
- Empty string for required name
- NaN/Infinity values
- Array with wrong dimensions
- Null references
- Out-of-bounds indices

---

### Scenario 7: UV Mapping and Texturing Workflow

**Goal**: Set up UV mapping and apply procedural texturing

**Workflow**:
```
1. Create mesh (sphere/torus)
2. Mark seams for UV unwrapping
3. Unwrap UV
4. Pack UV islands
5. Create material with texture
6. Verify UV layout
7. Apply texture coordinates
8. Capture viewport with material preview
```

**What to Test**:
- UV marking and clearing seams
- Unwrap algorithms (smart project, cube, cylinder)
- UV island packing
- UV map management
- Texture coordinate nodes

**Edge Cases**:
- UV operations on non-mesh objects
- Seams on non-manifold geometry
- Pack islands on empty UV
- Multiple UV maps

---

### Scenario 8: Physics Simulation Setup

**Goal**: Set up and run a physics simulation

**Workflow**:
```
1. Create ground plane (passive rigid body)
2. Create falling objects (active rigid bodies)
3. Configure physics properties (mass, friction)
4. Set up force field (wind/turbulence)
5. Configure simulation settings
6. Bake physics simulation
7. Play back animation
8. Capture result
```

**What to Test**:
- Rigid body setup
- Physics property configuration
- Force field creation
- Simulation baking
- Animation playback

**Edge Cases**:
- Physics on non-mesh objects
- Bake with no physics objects
- Force field with no affected objects
- Cancel bake mid-process

---

## Scenario Selection Strategy

Each iteration should pick a **different scenario** to ensure coverage:

| Iteration | Scenario | Focus |
|-----------|----------|-------|
| 1 | Low-Poly Asset | Modifiers, Materials, Animation |
| 2 | ArchViz | Collections, Lights, Render |
| 3 | Rigging | Armature, Constraints, NLA |
| 4 | Node Materials | Node Trees, Connections |
| 5 | Batch/Stress | Performance, Memory |
| 6 | Error Recovery | Edge Cases, Error Handling |
| 7 | UV/Texturing | UV Operations |
| 8 | Physics | Simulation, Baking |

Then cycle back to scenario 1 with **different parameters**.

---

## Detailed Test Checklist

### For Each Scenario:

**Setup Phase**:
- [ ] Start Blender successfully
- [ ] MCP connection established
- [ ] Verify initial scene state

**Execution Phase**:
- [ ] Each tool call has a **purpose** (not random)
- [ ] Verify result after each operation
- [ ] Check for unexpected side effects
- [ ] Monitor for errors/warnings

**Verification Phase**:
- [ ] Query scene state to verify changes
- [ ] Capture viewport for visual verification
- [ ] Check object counts, properties
- [ ] Verify data integrity

**Cleanup Phase**:
- [ ] Save scene (optional, for debugging)
- [ ] Clean up old test files
- [ ] Close Blender gracefully
- [ ] Update test state

---

## Error Classification

### Critical Errors (Immediate Issue)
- Blender crash (process terminates)
- MCP connection loss
- Data corruption (scene unusable)
- Infinite hang (>60 seconds)

### Major Errors (High Priority)
- Tool returns error but shouldn't
- Operation succeeds but has wrong result
- State inconsistency (object exists but can't query)
- Memory leak (>500MB growth)

### Minor Errors (Low Priority)
- Poor error message (unclear)
- Unexpected warning in logs
- Suboptimal performance (>5s response)
- UI doesn't update after operation

---

## Issue Documentation Format

When an issue is found:

```markdown
## Summary
[One-line description of the bug]

## Scenario
[Which test scenario triggered this]

## Reproduction Steps
1. [Step 1 - exact MCP command]
2. [Step 2 - exact MCP command]
3. [Continue...]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened]

## Root Cause (if known)
[Your analysis of why this happened]

## Environment
- Blender version: [from blender_get_scene]
- MCP version: [from git log -1 --oneline]
- macOS version: [sw_vers -productVersion]
- Iteration: #[N]

## Screenshots/Logs
[Viewport capture if visual issue]
[Tool output if relevant]

## Suggested Fix (optional)
[If you have ideas for how to fix]
```

---

## Memory and Performance Monitoring

After each iteration, check:

```bash
# Memory usage (macOS)
ps -o rss= -p <blender_pid>

# Log if >1GB
if [ $memory -gt 1048576 ]; then
  echo "WARNING: Blender using >1GB memory"
fi
```

Track memory growth across iterations.

---

## State Tracking

`/tmp/mcp_test_state.json`:

```json
{
  "iteration": 0,
  "current_scenario": "Low-Poly Game Asset",
  "scenarios_completed": [],
  "total_operations": 0,
  "critical_errors": 0,
  "major_errors": 0,
  "minor_errors": 0,
  "issues_created": ["#1", "#2", ...],
  "memory_samples": [],
  "start_time": "2026-04-17T23:00:00Z",
  "last_successful_scenario": null
}
```

---

## Starting Instructions

1. Check Blender is not running
2. Read `/tmp/mcp_test_state.json` or create new
3. Select next scenario based on iteration
4. Execute scenario workflow step by step
5. Document any errors found
6. Clean up and close Blender
7. Update state file
8. Continue to next iteration

**Do NOT output completion promise** - this runs until cancelled.
