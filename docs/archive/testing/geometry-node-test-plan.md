# Blender MCP 几何节点测试计划

测试环境：Blender 5.1.0 + MCP Server
参考文档：https://docs.blender.org/manual/zh-hans/latest/modeling/modifiers/geometry_nodes.html

---

## 一、测试目标

验证 Blender MCP 的 `blender_edit_nodes` 工具能够正确操作几何节点树中的各类节点。

**相关工具：**
- `blender_get_node_tree` — 读取节点树
- `blender_edit_nodes` — 编辑节点（添加/删除/连接/断开/设置值）

---

## 二、测试流程

对每个节点执行以下步骤：

```
1. 创建物体 → 2. 添加几何节点修改器 → 3. 添加节点 → 4. 设置参数 → 5. 连接节点 → 6. 验证结果
```

---

## 三、几何节点分类

### 3.1 输入节点 (Input) — 15 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 组输入 | NodeGroupInput | ⭐⭐⭐ | ⬜ |
| 2 | 位置 | GeometryNodeInputPosition | ⭐⭐ | ⬜ |
| 3 | 索引 | GeometryNodeInputIndex | ⭐⭐ | ⬜ |
| 4 | ID | GeometryNodeInputID | ⭐ | ⬜ |
| 5 | 随机值 | GeometryNodeInputRandom | ⭐⭐ | ⬜ |
| 6 | 命名属性 | GeometryNodeInputNamedAttribute | ⭐ | ⬜ |
| 7 | 法向 | GeometryNodeInputNormal | ⭐ | ⬜ |
| 8 | 半径 | GeometryNodeInputRadius | | ⬜ |
| 9 | 物体信息 | GeometryNodeObjectInfo | ⭐ | ⬜ |
| 10 | 场景时间 | GeometryNodeInputSceneTime | | ⬜ |
| 11 | 材质选择 | GeometryNodeMaterialSelection | ⭐ | ⬜ |
| 12 | 集合信息 | GeometryNodeCollectionInfo | ⭐ | ⬜ |
| 13 | 浮点/整数/布尔/向量 | NodeInputXXX | ⭐⭐ | ⬜ |
| 14 | 菲涅尔 | GeometryNodeInputShadeSmooth | | ⬜ |
| 15 | 边角 | GeometryNodeInputMeshEdgeVertices | | ⬜ |

---

### 3.2 输出节点 (Output) — 2 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 组输出 | NodeGroupOutput | ⭐⭐⭐ | ⬜ |
| 2 | 查看器 | GeometryNodeViewer | | ⬜ |

---

### 3.3 几何操作节点 (Geometry Operations) — 25 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 变换几何体 | GeometryNodeTransform | ⭐⭐⭐ | ⬜ |
| 2 | 设置位置 | GeometryNodeSetPosition | ⭐⭐ | ⬜ |
| 3 | 合并几何体 | GeometryNodeJoinGeometry | ⭐⭐ | ⬜ |
| 4 | 分离几何体 | GeometryNodeSeparateGeometry | ⭐ | ⬜ |
| 5 | 删除几何体 | GeometryNodeDeleteGeometry | ⭐⭐ | ⬜ |
| 6 | 分离组件 | GeometryNodeSeparateComponents | | ⬜ |
| 7 | 边界框 | GeometryNodeBoundBox | ⭐ | ⬜ |
| 8 | 几何体到实例 | GeometryNodeGeometryToInstance | | ⬜ |
| 9 | 按距离合并 | GeometryNodeMergeByDistance | ⭐ | ⬜ |
| 10 | 细分表面 | GeometryNodeSubdivisionSurface | ⭐⭐ | ⬜ |
| 11 | 布尔网格 | GeometryNodeMeshBoolean | ⭐⭐ | ⬜ |
| 12 | 挤出网格 | GeometryNodeExtrudeMesh | ⭐⭐ | ⬜ |
| 13 | 缩放元素 | GeometryNodeScaleElements | ⭐ | ⬜ |
| 14 | 双网格 | GeometryNodeDualMesh | | ⬜ |
| 15 | 边缘折痕 | GeometryNodeEdgeCrease | | ⬜ |
| 16 | 设置材质 | GeometryNodeSetMaterial | ⭐⭐ | ⬜ |
| 17 | 设置材质索引 | GeometryNodeSetMaterialIndex | ⭐ | ⬜ |
| 18 | 设置着色平滑 | GeometryNodeSetShadeSmooth | | ⬜ |
| 19 | 采样最近表面 | GeometryNodeSampleNearestSurface | ⭐ | ⬜ |
| 20 | 采样索引 | GeometryNodeSampleIndex | ⭐ | ⬜ |
| 21 | 索引处字段 | GeometryNodeFieldAtIndex | | ⬜ |
| 22 | 接近 | GeometryNodeProximity | ⭐ | ⬜ |
| 23 | 射线投射 | GeometryNodeRaycast | ⭐ | ⬜ |
| 24 | 图像纹理 | GeometryNodeImageTexture | ⭐ | ⬜ |
| 25 | 存储命名属性 | GeometryNodeStoreNamedAttribute | ⭐⭐ | ⬜ |

---

### 3.4 实例节点 (Instances) — 5 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 点上实例 | GeometryNodeInstanceOnPoints | ⭐⭐⭐ | ⬜ |
| 2 | 实现实例 | GeometryNodeRealizeInstances | ⭐⭐ | ⬜ |
| 3 | 实例缩放 | GeometryNodeInstancesScale | | ⬜ |
| 4 | 实例变换 | GeometryNodeInstancesTransform | | ⬜ |
| 5 | 实例到点 | GeometryNodeInstanceTransform | | ⬜ |

---

### 3.5 点节点 (Point) — 5 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 网格到点 | GeometryNodeMeshToPoints | ⭐⭐ | ⬜ |
| 2 | 点分布 | GeometryNodeDistributePointsOnFaces | ⭐⭐ | ⬜ |
| 3 | 点计数 | GeometryNodePointsToCurves | | ⬜ |
| 4 | 设置点半径 | GeometryNodeSetPointRadius | | ⬜ |
| 5 | 点到顶点 | GeometryNodePointsToVertices | | ⬜ |

---

### 3.6 曲线节点 (Curve) — 8 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 曲线到网格 | GeometryNodeCurveToMesh | ⭐⭐ | ⬜ |
| 2 | 网格到曲线 | GeometryNodeMeshToCurve | ⭐ | ⬜ |
| 3 | 修剪曲线 | GeometryNodeTrimCurve | ⭐ | ⬜ |
| 4 | 曲线长度 | GeometryNodeCurveLength | | ⬜ |
| 5 | 重采样曲线 | GeometryNodeResampleCurve | ⭐ | ⬜ |
| 6 | 填充曲线 | GeometryNodeFillCurve | | ⬜ |
| 7 | 曲线圆角 | GeometryNodeFilletCurve | | ⬜ |
| 8 | 曲线设置柄位 | GeometryNodeSetCurveHandlePositions | | ⬜ |

---

### 3.7 网格图元节点 (Mesh Primitives) — 8 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 网格网格 | GeometryNodeMeshGrid | ⭐ | ⬜ |
| 2 | 网格立方体 | GeometryNodeMeshCube | ⭐ | ⬜ |
| 3 | 网格圆形 | GeometryNodeMeshCircle | ⭐ | ⬜ |
| 4 | 网格圆柱 | GeometryNodeMeshCylinder | ⭐ | ⬜ |
| 5 | 网格锥体 | GeometryNodeMeshCone | ⭐ | ⬜ |
| 6 | 网格球 | GeometryNodeMeshUVSphere | ⭐ | ⬜ |
| 7 | 网格二十面体球 | GeometryNodeMeshIcoSphere | ⭐ | ⬜ |
| 8 | 网格线 | GeometryNodeMeshLine | ⭐ | ⬜ |

---

### 3.8 曲线图元节点 (Curve Primitives) — 6 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 曲线路径 | GeometryNodeCurvePath | | ⬜ |
| 2 | 曲线线段 | GeometryNodeCurveLine | | ⬜ |
| 3 | 曲线螺旋 | GeometryNodeCurveSpiral | | ⬜ |
| 4 | 曲线星形 | GeometryNodeCurveStar | | ⬜ |
| 5 | 曲线圆弧 | GeometryNodeCurveArc | | ⬜ |
| 6 | 曲线贝塞尔段 | GeometryNodeCurveBezierSegment | | ⬜ |

---

### 3.9 工具节点 (Utilities) — 10 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 数学 | ShaderNodeMath | ⭐⭐ | ⬜ |
| 2 | 矢量数学 | ShaderNodeVectorMath | ⭐⭐ | ⬜ |
| 3 | 布尔数学 | FunctionNodeBooleanMath | ⭐ | ⬜ |
| 4 | 浮点到整数 | FunctionNodeFloatToInt | | ⬜ |
| 5 | 开关 | GeometryNodeSwitch | ⭐ | ⬜ |
| 6 | 比较 | FunctionNodeCompare | ⭐ | ⬜ |
| 7 | 浮点曲线 | ShaderNodeFloatCurve | | ⬜ |
| 8 | 颜色渐变 | ShaderNodeValToRGB | ⭐ | ⬜ |
| 9 | 混合 | ShaderNodeMix | ⭐ | ⬜ |
| 10 | 随机值 | GeometryNodeInputRandom | ⭐⭐ | ⬜ |

---

## 四、测试脚本模板

### 4.1 基础测试流程

```python
import socket
import json

def send_request(capability, payload, timeout=30):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect(('127.0.0.1', 9876))
    request = json.dumps({'capability': capability, 'payload': payload})
    sock.sendall((request + '\n').encode('utf-8'))
    response = sock.recv(16384).decode('utf-8')
    sock.close()
    return json.loads(response)

# 1. 创建物体
send_request('blender.create_object', {
    'name': 'TestGeoNode',
    'object_type': 'MESH',
    'primitive': 'cube',
    'size': 2.0
})

# 2. 添加几何节点修改器
send_request('blender.manage_modifier', {
    'action': 'add',
    'object_name': 'TestGeoNode',
    'modifier_name': 'GeometryNodes',
    'modifier_type': 'NODES'
})

# 3. 添加节点
send_request('blender.edit_nodes', {
    'tree_type': 'GEOMETRY',
    'context': 'OBJECT',
    'target': 'TestGeoNode',
    'operations': [{
        'action': 'add',
        'node_type': 'GeometryNodeTransform',
        'name': 'Transform'
    }]
})

# 4. 连接节点
send_request('blender.edit_nodes', {
    'tree_type': 'GEOMETRY',
    'context': 'OBJECT',
    'target': 'TestGeoNode',
    'operations': [{
        'action': 'connect',
        'from_node': 'Group Input',
        'from_socket': 'Geometry',
        'to_node': 'Transform',
        'to_socket': 'Geometry'
    }]
})
```

---

## 五、优先级测试节点

### 高优先级（核心节点）
1. **NodeGroupInput / NodeGroupOutput** — 必须的输入输出
2. **GeometryNodeTransform** — 变换几何体
3. **GeometryNodeInstanceOnPoints** — 实例化
4. **GeometryNodeJoinGeometry** — 合并几何
5. **GeometryNodeSubdivisionSurface** — 细分表面

### 中优先级（常用节点）
- GeometryNodeSetPosition, GeometryNodeMeshBoolean
- GeometryNodeExtrudeMesh, GeometryNodeSetMaterial
- GeometryNodeCurveToMesh, GeometryNodeMeshToCurve

### 低优先级（特殊用途）
- 曲线图元、曲线操作、高级采样等

---

## 六、预期产出

1. **测试报告**: `geometry-node-test-report.md`
2. **覆盖率统计**: 各类节点的通过率
3. **问题清单**: 失败节点及原因

---

*计划创建日期: 2026-04-16*
