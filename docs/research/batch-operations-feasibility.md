# -*- coding: utf-8 -*-
# 批量操作可行性调研

> **调研日期**: 2026-04-14
> **调研范围**: Unity MCP batch_execute、当前架构瓶颈分析、Blender 批量 API

---

## 结论

**批量操作可行，但收益有限（约 2-5x，不是 10-100x）。**

Unity MCP 宣称 10-100x 提升，但它的瓶颈是 HTTP/WebSocket 往返延迟（每次数百 ms）。
我们的瓶颈是 TCP + 50ms poll 轮询间隔，单次调用约 55-110ms。

批量操作能消除 N-1 次 TCP 往返和 N-1 次 poll 等待，但 Blender 的 bpy API
本身没有"批量创建"的原语——创建 20 个物体就是调 20 次 bpy.ops.mesh.primitive_cube_add()。

---

## 1. 当前架构延迟分析

每次工具调用的开销分解：

| 阶段 | 延迟 | 说明 |
|------|------|------|
| LLM → MCP server (stdio) | ~1ms | 本地管道 |
| MCP → TCP connect + send | ~2ms | localhost TCP |
| TCP → addon receive + parse | ~1ms | 字节解析 |
| `_dispatch_to_main_thread` poll 等待 | ~50ms | 50ms 轮询间隔 |
| `execute_capability` (bpy 操作) | ~1-50ms | 取决于操作复杂度 |
| Response 返回 | ~2ms | TCP 回传 |
| **总计** | **~55-110ms** | |

创建 20 个物体：20 × 80ms = **1.6 秒**，其中 1.0 秒是 poll 等待。

## 2. Unity MCP batch_execute 参考

来源: [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp)

### API 设计

```json
{
  "commands": [
    {"tool": "manage_gameobject", "params": {"action": "create", "name": "Cube1"}},
    {"tool": "manage_gameobject", "params": {"action": "create", "name": "Cube2"}}
  ],
  "fail_fast": false
}
```

- 列表协议：发送 `[{tool, params}]` 数组
- 主线程顺序执行（`parallel` 参数声明但实际忽略）
- 默认上限 25 条，硬上限 100 条
- 10-100x 提升来源：消除 HTTP 往返 + 减少 token 消耗

### 关键发现

Unity MCP 的 `parallel` 参数是**假的**——Unity API 和 Blender 一样要求主线程操作。
它承认 "commands will run sequentially on the main thread for safety"。

## 3. Blender 批量操作可行性

### 3.1 bpy 有批量 API 吗？

**没有。** Blender 的 Python API 是逐对象操作的：

```python
# 创建 20 个立方体，没有批量原语
for i in range(20):
    bpy.ops.mesh.primitive_cube_add(location=(i, 0, 0))
```

唯一的"批量"能力是 `bpy.data` 的批量查询（一次获取所有对象数据），
我们已经通过 `blender.get_objects` 实现了。

### 3.2 实现方案

**方案 A：新工具 `blender.batch_execute`**

```json
{
  "capability": "blender.batch_execute",
  "payload": {
    "operations": [
      {"capability": "blender.create_object", "payload": {"name": "Cube1", "object_type": "MESH", "primitive": "cube"}},
      {"capability": "blender.create_object", "payload": {"name": "Cube2", "object_type": "MESH", "primitive": "cube"}},
      {"capability": "blender.modify_object", "payload": {"name": "Cube1", "location": [0, 0, 2]}}
    ],
    "fail_fast": false
  }
}
```

addon 端在一次 `_main_thread_poll` 循环中顺序执行所有操作，
只返回一次 TCP 响应。

**优势：**
- 消除 N-1 次 TCP 往返（~4ms × N）
- 消除 N-1 次 poll 等待（~50ms × N）
- 减少 token 消耗（一次工具调用代替 N 次）

**劣势：**
- 增加一个新工具（从 26 → 27）
- LLM 需要学会何时用批量、何时用单独调用
- 部分操作之间有依赖（先创建再修改），批量出错时部分完成状态难以处理

### 3.3 性能预估

| 场景 | 当前 | 批量后 | 提升 |
|------|------|--------|------|
| 创建 20 个物体 | ~1.6s | ~0.5s | 3.2x |
| 创建 5 个物体 + 5 个材质 + 赋予 | ~1.1s | ~0.3s | 3.7x |
| 读取 10 个对象数据 | ~0.8s | ~0.2s | 4x |

提升倍数取决于操作数量，但受限于 bpy 操作本身的执行时间。

### 3.4 替代方案：减少 poll 间隔

当前 `_TIMER_INTERVAL = 0.05`（50ms）。如果改为 0.01（10ms）：

```python
_TIMER_INTERVAL = 0.01  # 从 50ms 改为 10ms
```

创建 20 个物体：20 × 40ms = **0.8s**（从 1.6s 减半），无需新增工具。

这个改动的收益约 2x，但风险很低——更频繁的 poll 意味着更高的 CPU 占用（每秒 100 次 vs 20 次）。

## 4. 建议

| 优先级 | 方案 | 收益 | 复杂度 | 建议 |
|--------|------|------|--------|------|
| 立即可做 | 减少 poll 间隔到 10ms | ~2x | 极低（改一个数字） | ✅ 做 |
| 中期 | `blender.batch_execute` 工具 | ~3-5x | 中等 | ⚠️ 等用户反馈 |
| 远期 | 批量操作 + undo 压缩 | ~3-5x + 更好的 undo | 高 | ❌ 暂不需要 |

**核心结论：批量操作的瓶颈不在 Blender API 层面，而在 MCP 协议的往返延迟。
减少 poll 间隔是最简单有效的优化。新增 batch_execute 工具可以等用户反馈后再决定。**
