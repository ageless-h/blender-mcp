# Blender MCP 着色器节点测试计划

测试环境：Blender 5.1.0 + MCP Server
参考文档：https://docs.blender.org/manual/zh-hans/latest/render/shader_nodes/index.html

---

## 一、测试目标

验证 Blender MCP 的 `blender_edit_nodes` 工具能够正确操作着色器节点树中的各类节点。

**相关工具：**
- `blender_get_node_tree` — 读取节点树
- `blender_edit_nodes` — 编辑节点（添加/删除/连接/断开/设置值）

---

## 二、测试流程

对每个节点执行以下步骤：

```
1. 创建材质 → 2. 启用节点 → 3. 添加节点 → 4. 设置参数 → 5. 连接节点 → 6. 验证结果
```

---

## 三、着色器节点分类

### 3.1 输出节点 (Output) — 2 种

| 序号 | 节点名称 | bl_idname | 状态 |
|------|----------|-----------|------|
| 1 | 材质输出 | ShaderNodeOutputMaterial | ⬜ |
| 2 | 线条样式输出 | ShaderNodeOutputLineStyle | ⬜ |

---

### 3.2 着色器节点 (Shader) — 26 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 原理化 BSDF | ShaderNodeBsdfPrincipled | ⭐⭐⭐ | ⬜ |
| 2 | 混合着色器 | ShaderNodeMixShader | ⭐⭐ | ⬜ |
| 3 | 相加着色器 | ShaderNodeAddShader | ⭐ | ⬜ |
| 4 | 自发光 | ShaderNodeEmission | ⭐⭐ | ⬜ |
| 5 | 漫反射 BSDF | ShaderNodeBsdfDiffuse | ⭐ | ⬜ |
| 6 | 光泽 BSDF | ShaderNodeBsdfAnisotropic | ⭐ | ⬜ |
| 7 | 玻璃 BSDF | ShaderNodeBsdfGlass | ⭐ | ⬜ |
| 8 | 透明 BSDF | ShaderNodeBsdfTransparent | ⭐ | ⬜ |
| 9 | 折射 BSDF | ShaderNodeBsdfRefraction | ⭐ | ⬜ |
| 10 | 次表面散射 | ShaderNodeSubsurfaceScattering | ⭐ | ⬜ |
| 11 | 遮罩 | ShaderNodeHoldout | | ⬜ |
| 12 | 体积散射 | ShaderNodeVolumeScatter | | ⬜ |
| 13 | 体积吸收 | ShaderNodeVolumeAbsorption | | ⬜ |
| 14 | 原理化体积 | ShaderNodeVolumePrincipled | | ⬜ |
| 15 | 原理化头发 BSDF | ShaderNodeBsdfHairPrincipled | | ⬜ |
| 16 | 头发 BSDF | ShaderNodeBsdfHair | | ⬜ |
| 17 | 金属 BSDF | ShaderNodeBsdfMetallic | | ⬜ |
| 18 | 光泽 BSDF | ShaderNodeBsdfSheen | | ⬜ |
| 19 | 半透明 BSDF | ShaderNodeBsdfTranslucent | | ⬜ |
| 20 | 卡通 BSDF | ShaderNodeBsdfToon | | ⬜ |
| 21 | 光线传送门 BSDF | ShaderNodeBsdfRayPortal | 🆕 | ⬜ |
| 22 | 背景 | ShaderNodeBackground | | ⬜ |
| 23 | 高光 BSDF | ShaderNodeEeveeSpecular | | ⬜ |
| 24 | 体积系数 | ShaderNodeVolumeCoefficients | | ⬜ |

---

### 3.3 输入节点 (Input) — 20 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 纹理坐标 | ShaderNodeTexCoord | ⭐⭐ | ⬜ |
| 2 | 映射 | ShaderNodeMapping | ⭐⭐ | ⬜ |
| 3 | 属性 | ShaderNodeAttribute | ⭐ | ⬜ |
| 4 | 菲涅尔 | ShaderNodeFresnel | ⭐⭐ | ⬜ |
| 5 | 层权重 | ShaderNodeLayerWeight | ⭐ | ⬜ |
| 6 | 新建几何体 | ShaderNodeNewGeometry | ⭐⭐ | ⬜ |
| 7 | 物体信息 | ShaderNodeObjectInfo | ⭐⭐ | ⬜ |
| 8 | 粒子信息 | ShaderNodeParticleInfo | | ⬜ |
| 9 | 摄像机数据 | ShaderNodeCameraData | | ⬜ |
| 10 | 线框 | ShaderNodeWireframe | | ⬜ |
| 11 | UV 贴图 | ShaderNodeUVMap | ⭐ | ⬜ |
| 12 | 数值 | ShaderNodeValue | ⭐ | ⬜ |
| 13 | RGB | ShaderNodeRGB | ⭐ | ⬜ |
| 14 | 光程 | ShaderNodeLightPath | ⭐ | ⬜ |
| 15 | 环境光遮蔽 | ShaderNodeAmbientOcclusion | ⭐ | ⬜ |
| 16 | 颜色属性 | ShaderNodeColorAttribute | | ⬜ |
| 17 | 曲线信息 | ShaderNodeHairInfo | | ⬜ |
| 18 | 切线 | ShaderNodeTangent | | ⬜ |
| 19 | 体积信息 | ShaderNodeVolumeInfo | | ⬜ |
| 20 | 射线投射 | ShaderNodeRaycast | 🆕 5.1 | ⬜ |
| 21 | 倒角 | ShaderNodeBevel | | ⬜ |
| 22 | 点信息 | ShaderNodePointInfo | | ⬜ |

---

### 3.4 纹理节点 (Texture) — 14 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 图像纹理 | ShaderNodeTexImage | ⭐⭐ | ⬜ |
| 2 | 噪波纹理 | ShaderNodeTexNoise | ⭐⭐ | ⬜ |
| 3 | 沃罗诺伊纹理 | ShaderNodeTexVoronoi | ⭐ | ⬜ |
| 4 | 砖墙纹理 | ShaderNodeTexBrick | ⭐ | ⬜ |
| 5 | 棋盘格纹理 | ShaderNodeTexChecker | ⭐ | ⬜ |
| 6 | 渐变纹理 | ShaderNodeTexGradient | ⭐ | ⬜ |
| 7 | 幻彩纹理 | ShaderNodeTexMagic | | ⬜ |
| 8 | 波浪纹理 | ShaderNodeTexWave | ⭐ | ⬜ |
| 9 | 环境纹理 | ShaderNodeTexEnvironment | | ⬜ |
| 10 | 天空纹理 | ShaderNodeTexSky | | ⬜ |
| 11 | IES 纹理 | ShaderNodeTexIES | | ⬜ |
| 12 | 点云密度 | ShaderNodeTexPointDensity | | ⬜ |
| 13 | 白噪波纹理 | ShaderNodeTexWhiteNoise | | ⬜ |
| 14 | Gabor 纹理 | ShaderNodeTexGabor | | ⬜ |

---

### 3.5 颜色节点 (Color) — 14 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 颜色渐变 | ShaderNodeValToRGB | ⭐⭐ | ⬜ |
| 2 | 混合颜色 | ShaderNodeMixRGB | ⭐⭐ | ⬜ |
| 3 | 分离颜色 | ShaderNodeSeparateColor | ⭐ | ⬜ |
| 4 | 合并颜色 | ShaderNodeCombineColor | ⭐ | ⬜ |
| 5 | 色相/饱和度/明度 | ShaderNodeHueSaturation | ⭐ | ⬜ |
| 6 | 亮度/对比度 | ShaderNodeBrightContrast | ⭐ | ⬜ |
| 7 | 伽马 | ShaderNodeGamma | ⭐ | ⬜ |
| 8 | 反相颜色 | ShaderNodeInvert | ⭐ | ⬜ |
| 9 | 颜色平衡 | ShaderNodeColorBalance | | ⬜ |
| 10 | RGB 曲线 | ShaderNodeRGBCurve | | ⬜ |
| 11 | RGB 到 BW | ShaderNodeRGBToBW | ⭐ | ⬜ |
| 12 | 着色器到 RGB | ShaderNodeShaderToRGB | | ⬜ |
| 13 | 黑体辐射 | ShaderNodeBlackbody | | ⬜ |
| 14 | 波长 | ShaderNodeWavelength | | ⬜ |

---

### 3.6 矢量节点 (Vector) — 12 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 凹凸 | ShaderNodeBump | ⭐⭐ | ⬜ |
| 2 | 法线贴图 | ShaderNodeNormalMap | ⭐⭐ | ⬜ |
| 3 | 置换 | ShaderNodeDisplacement | ⭐⭐ | ⬜ |
| 4 | 法线 | ShaderNodeNormal | | ⬜ |
| 5 | 矢量运算 | ShaderNodeVectorMath | ⭐ | ⬜ |
| 6 | 矢量旋转 | ShaderNodeVectorRotate | | ⬜ |
| 7 | 矢量曲线 | ShaderNodeVectorCurve | | ⬜ |
| 8 | 矢量置换 | ShaderNodeVectorDisplacement | | ⬜ |
| 9 | 矢量变换 | ShaderNodeVectorTransform | | ⬜ |
| 10 | 分离 XYZ | ShaderNodeSeparateXYZ | ⭐ | ⬜ |
| 11 | 合并 XYZ | ShaderNodeCombineXYZ | ⭐ | ⬜ |
| 12 | 径向平铺 | ShaderNodeRadialTiling | | ⬜ |

---

### 3.7 转换器节点 (Converter) — 6 种

| 序号 | 节点名称 | bl_idname | 优先级 | 状态 |
|------|----------|-----------|--------|------|
| 1 | 数学 | ShaderNodeMath | ⭐⭐ | ⬜ |
| 2 | 混合 | ShaderNodeMix | ⭐⭐ | ⬜ |
| 3 | 范围映射 | ShaderNodeMapRange | ⭐ | ⬜ |
| 4 | 钳制 | ShaderNodeClamp | | ⬜ |
| 5 | 浮点曲线 | ShaderNodeFloatCurve | | ⬜ |
| 6 | 曲线 RGB | ShaderNodeCurveRGB | | ⬜ |

---

## 四、测试脚本模板

### 4.1 基硋试流程

```python
import socket
import json

def send_request(capability, payload, timeout=30):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect(('127.0.0.1', 9876))
    request = json.dumps({'capability': capability, 'payload': payload})
    sock.sendall((request + '\n').encode('utf-8'))
    response = sock.recv(8192).decode('utf-8')
    sock.close()
    return json.loads(response)

# 1. 创建材质
result = send_request('blender.manage_material', {
    'action': 'create',
    'name': 'TestMaterial'
})

# 2. 添加着色器节点
result = send_request('blender.edit_nodes', {
    'tree_type': 'SHADER',
    'context': 'OBJECT',
    'target': 'TestMaterial',
    'operations': [{
        'action': 'add',
        'node_type': 'ShaderNodeBsdfPrincipled',
        'name': 'Principled BSDF'
    }]
})

# 3. 设置节点参数
result = send_request('blender.edit_nodes', {
    'tree_type': 'SHADER',
    'context': 'OBJECT',
    'target': 'TestMaterial',
    'operations': [{
        'action': 'set_value',
        'node': 'Principled BSDF',
        'input': 'Base Color',
        'value': [1.0, 0.0, 0.0, 1.0]  # 红色
    }]
})

# 4. 连接节点
result = send_request('blender.edit_nodes', {
    'tree_type': 'SHADER',
    'context': 'OBJECT',
    'target': 'TestMaterial',
    'operations': [{
        'action': 'connect',
        'from_node': 'Principled BSDF',
        'from_socket': 'BSDF',
        'to_node': 'Material Output',
        'to_socket': 'Surface'
    }]
})

# 5. 读取节点树验证
result = send_request('blender.get_node_tree', {
    'tree_type': 'SHADER',
    'context': 'OBJECT',
    'target': 'TestMaterial',
    'depth': 'full'
})
```

---

### 4.2 MCP 命令示例

#### 添加原理化 BSDF 节点
```json
{
  "capability": "blender.edit_nodes",
  "payload": {
    "tree_type": "SHADER",
    "context": "OBJECT",
    "target": "MyMaterial",
    "operations": [{
      "action": "add",
      "node_type": "ShaderNodeBsdfPrincipled",
      "name": "MyBSDF"
    }]
  }
}
```

#### 设置节点颜色参数
```json
{
  "capability": "blender.edit_nodes",
  "payload": {
    "tree_type": "SHADER",
    "context": "OBJECT",
    "target": "MyMaterial",
    "operations": [{
      "action": "set_value",
      "node": "MyBSDF",
      "input": "Base Color",
      "value": [0.8, 0.2, 0.1, 1.0]
    }]
  }
}
```

#### 连接噪波纹理到原理化 BSDF
```json
{
  "capability": "blender.edit_nodes",
  "payload": {
    "tree_type": "SHADER",
    "context": "OBJECT",
    "target": "MyMaterial",
    "operations": [{
      "action": "connect",
      "from_node": "Noise Texture",
      "from_socket": "Color",
      "to_node": "Principled BSDF",
      "to_socket": "Base Color"
    }]
  }
}
```

---

## 五、优先级测试节点

### 高优先级（核心节点）
1. **ShaderNodeBsdfPrincipled** — 最常用的着色器
2. **ShaderNodeOutputMaterial** — 必须的输出节点
3. **ShaderNodeTexImage** — 纹理贴图
4. **ShaderNodeTexNoise** — 程序化纹理
5. **ShaderNodeMath** — 数学运算
6. **ShaderNodeMixRGB** — 颜色混合

### 中优先级（常用节点）
- ShaderNodeBsdfDiffuse, ShaderNodeBsdfGlass, ShaderNodeBsdfGlossy
- ShaderNodeTexCoord, ShaderNodeMapping
- ShaderNodeSeparateColor, ShaderNodeCombineColor
- ShaderNodeBump, ShaderNodeNormalMap

### 低优先级（特殊用途）
- 体积节点、线框、粒子信息等

---

## 六、预期产出

1. **测试报告**: `shader-node-test-report.md`
2. **覆盖率统计**: 各类节点的通过率
3. **问题清单**: 失败节点及原因

---

*计划创建日期: 2026-04-16*
