# Blender MCP 修改器测试计划

测试环境：Blender 5.1.0 + MCP Server
参考文档：https://docs.blender.org/manual/zh-hans/latest/modeling/modifiers/index.html

---

## 一、测试目标

验证 Blender MCP 的 `blender_manage_modifier` 工具能够正确操作 Blender 官方文档中列出的所有修改器类型。

---

## 二、测试流程

对每个修改器执行以下步骤：

```
1. 新建物体 → 2. 添加修改器 → 3. 调试修改器参数 → 4. 删除物体 → 5. 记录结果
```

---

## 三、修改器测试清单

### 3.1 编辑类修改器 (Edit)

| 序号 | 修改器 | 类型标识 | 测试参数 | 状态 |
|------|--------|----------|----------|------|
| 1 | 数据传递 | DATA_TRANSFER | object, data_types | ⬜ |
| 2 | 网格缓存 | MESH_CACHE | filepath, frame_start | ⬜ |
| 3 | 网格序列缓存 | MESH_SEQUENCE_CACHE | filepath | ⬜ |
| 4 | UV 投射 | UV_PROJECT | aspect_x, aspect_y | ⬜ |
| 5 | UV 偏移 | UV_WARP | offset | ⬜ |
| 6 | 顶点权重编辑 | VERTEX_WEIGHT_EDIT | group_name | ⬜ |
| 7 | 顶点权重混合 | VERTEX_WEIGHT_MIX | group_a, group_b | ⬜ |
| 8 | 顶点权重邻近 | VERTEX_WEIGHT_PROXIMITY | target, distance | ⬜ |

---

### 3.2 生成类修改器 (Generate)

| 序号 | 修改器 | 类型标识 | 测试参数 | 状态 |
|------|--------|----------|----------|------|
| 9 | 阵列 | ARRAY | count, relative_offset_displace | ⬜ |
| 10 | 阵列(旧版) | ARRAY_LEGACY | count, offset | ⬜ |
| 11 | 倒角 | BEVEL | width, segments, limit_method | ⬜ |
| 12 | 布尔 | BOOLEAN | operation, object | ⬜ |
| 13 | 建形 | BUILD | frame_start, frame_duration | ⬜ |
| 14 | 曲线转管形 | CURVE_TO_TUBE | - | ⬜ |
| 15 | 精简 | DECIMATE | ratio | ⬜ |
| 16 | 拆边 | EDGE_SPLIT | split_angle | ⬜ |
| 17 | 遮罩 | MASK | vertex_group | ⬜ |
| 18 | 网格转体积 | MESH_TO_VOLUME | voxel_size | ⬜ |
| 19 | 镜像 | MIRROR | use_x, use_y, use_z | ⬜ |
| 20 | 多级精度 | MULTIRES | levels | ⬜ |
| 21 | 重构网格 | REMESH | mode, voxel_size | ⬜ |
| 22 | 表面散布 | SCATTER_ON_SURFACE | collection | ⬜ |
| 23 | 螺旋 | SCREW | angle, steps | ⬜ |
| 24 | 蒙皮 | SKIN | use_smooth_shade | ⬜ |
| 25 | 实体化 | SOLIDIFY | thickness, offset | ⬜ |
| 26 | 表面细分 | SUBSURF | levels, render_levels | ⬜ |
| 27 | 三角化 | TRIANGULATE | quad_method, ngon_method | ⬜ |
| 28 | 体积转网格 | VOLUME_TO_MESH | voxel_size | ⬜ |
| 29 | 焊接 | WELD | merge_threshold | ⬜ |
| 30 | 线框 | WIREFRAME | thickness | ⬜ |

---

### 3.3 形变类修改器 (Deform)

| 序号 | 修改器 | 类型标识 | 测试参数 | 状态 |
|------|--------|----------|----------|------|
| 31 | 骨架 | ARMATURE | object, use_vertex_groups | ⬜ |
| 32 | 铸型 | CAST | cast_type, factor, radius | ⬜ |
| 33 | 曲线 | CURVE | object, deform_axis | ⬜ |
| 34 | 置换 | DISPLACE | strength, direction, texture | ⬜ |
| 35 | 钩挂 | HOOK | object, vertex_group | ⬜ |
| 36 | 拉普拉斯形变 | LAPLACIANDEFORM | iterations | ⬜ |
| 37 | 晶格 | LATTICE | object, strength | ⬜ |
| 38 | 网格形变 | MESH_DEFORM | object, precision | ⬜ |
| 39 | 缩裹 | SHRINKWRAP | target, offset | ⬜ |
| 40 | 简易形变 | SIMPLE_DEFORM | deform_mode, factor | ⬜ |
| 41 | 平滑 | SMOOTH | iterations, factor | ⬜ |
| 42 | 矫正平滑 | CORRECTIVE_SMOOTH | iterations | ⬜ |
| 43 | 拉普拉斯平滑 | LAPLACIANSMOOTH | iterations, lambda_factor | ⬜ |
| 44 | 表面变形 | SURFACE_DEFORM | target, strength | ⬜ |
| 45 | 体积置换 | VOLUME_DISPLACE | strength | ⬜ |
| 46 | 弯绕 | WARP | strength | ⬜ |
| 47 | 波浪 | WAVE | amplitude, wavelength, speed | ⬜ |

---

### 3.4 法向类修改器 (Normals)

| 序号 | 修改器 | 类型标识 | 测试参数 | 状态 |
|------|--------|----------|----------|------|
| 48 | 法线编辑 | NORMAL_EDIT | mode | ⬜ |
| 49 | 加权法向 | WEIGHTED_NORMAL | mode | ⬜ |
| 50 | 按角度平滑 | SMOOTH_BY_ANGLE | angle | ⬜ |

---

### 3.5 物理类修改器 (Physics)

| 序号 | 修改器 | 类型标识 | 测试参数 | 状态 |
|------|--------|----------|----------|------|
| 51 | 布料 | CLOTH | mass, tension_stiffness | ⬜ |
| 52 | 碰撞 | COLLISION | permeability | ⬜ |
| 53 | 动态绘画 | DYNAMIC_PAINT | type | ⬜ |
| 54 | 爆破 | EXPLODE | use_edge_cut | ⬜ |
| 55 | 流体 | FLUID | cache_type | ⬜ |
| 56 | 海洋 | OCEAN | wave_scale, choppiness | ⬜ |
| 57 | 粒子实例 | PARTICLE_INSTANCE | particle_system | ⬜ |
| 58 | 粒子系统 | PARTICLE_SYSTEM | particle_system | ⬜ |
| 59 | 软体 | SOFT_BODY | mass, friction | ⬜ |

---

## 四、测试脚本模板

### 4.1 单个修改器测试步骤

```python
# 步骤 1: 新建物体
send_request('blender.create_object', {
    'name': 'TestObject',
    'object_type': 'MESH',
    'primitive': 'cube',
    'size': 2.0
})

# 步骤 2: 添加修改器
send_request('blender.manage_modifier', {
    'action': 'add',
    'object_name': 'TestObject',
    'modifier_name': '<修改器名称>',
    'modifier_type': '<类型标识>',
    'settings': {<测试参数>}
})

# 步骤 3: 调试修改器参数
send_request('blender.manage_modifier', {
    'action': 'configure',
    'object_name': 'TestObject',
    'modifier_name': '<修改器名称>',
    'settings': {<修改后的参数>}
})

# 步骤 4: 删除物体
send_request('blender.modify_object', {
    'name': 'TestObject',
    'delete': True
})

# 步骤 5: 记录结果
# ✅ 通过 / ❌ 失败 + 错误信息
```

---

### 4.2 MCP 命令示例

#### 添加表面细分修改器
```json
{
  "capability": "blender.manage_modifier",
  "payload": {
    "action": "add",
    "object_name": "TestCube",
    "modifier_name": "Subsurf",
    "modifier_type": "SUBSURF",
    "settings": {"levels": 3, "render_levels": 4}
  }
}
```

#### 配置倒角修改器
```json
{
  "capability": "blender.manage_modifier",
  "payload": {
    "action": "configure",
    "object_name": "TestCube",
    "modifier_name": "Bevel",
    "settings": {"width": 0.1, "segments": 3, "limit_method": "ANGLE"}
  }
}
```

#### 应用修改器
```json
{
  "capability": "blender.manage_modifier",
  "payload": {
    "action": "apply",
    "object_name": "TestCube",
    "modifier_name": "Bevel"
  }
}
```

#### 删除修改器
```json
{
  "capability": "blender.manage_modifier",
  "payload": {
    "action": "remove",
    "object_name": "TestCube",
    "modifier_name": "Bevel"
  }
}
```

---

## 五、测试执行计划

### 5.1 执行顺序

1. **第一批**: 编辑类修改器 (8个) - 测试基础数据操作
2. **第二批**: 生成类修改器 (22个) - 测试几何体生成
3. **第三批**: 形变类修改器 (17个) - 测试形变效果
4. **第四批**: 法向类修改器 (3个) - 测试法线操作
5. **第五批**: 物理类修改器 (9个) - 测试物理模拟

### 5.2 批量测试脚本

待执行测试时，使用以下 Python 脚本连接 MCP 服务器并批量测试：

```python
import socket
import json

def send_request(capability, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(('127.0.0.1', 9876))
    request = json.dumps({'capability': capability, 'payload': payload})
    sock.sendall((request + '\n').encode('utf-8'))
    response = sock.recv(8192).decode('utf-8')
    sock.close()
    return json.loads(response)

# 测试循环...
```

---

## 六、记录表格模板

| 修改器 | 添加结果 | 配置结果 | 错误信息 | 备注 |
|--------|----------|----------|----------|------|
| SUBSURF | ⬜ | ⬜ | | |
| BEVEL | ⬜ | ⬜ | | |
| ... | ... | ... | ... | ... |

---

## 七、预期产出

1. **测试报告**: `modifier-test-report.md` - 记录所有测试结果
2. **问题清单**: 记录失败的修改器及原因
3. **覆盖率统计**: 各类修改器的通过率

---

*计划创建日期: 2026-04-16*
