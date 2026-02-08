# 脚本工具 (blender_execute_script)

⚠️ **警告**：这是一个危险工具，默认禁用。启用前请确保理解安全风险。

## 概述

`blender_execute_script` 允许执行任意 Python 代码，用于覆盖核心工具无法处理的边缘情况（约 0.1%）。

## 工具签名

```python
blender_execute_script(
    code: str,                # Python 代码
    timeout: int = 30         # 超时秒数
) -> {
    "success": bool,
    "output": str,            # stdout 输出
    "error": str | None,      # 错误信息
    "return_value": Any,      # 最后表达式的返回值
    "execution_time_ms": float
}
```

## 启用配置

在 MCP 服务器配置中启用：

```yaml
# config.yaml
security:
  unsafe_tools:
    script_execute:
      enabled: true           # 默认 false
      timeout_seconds: 30     # 执行超时
      require_consent: true   # 是否需要用户确认
```

## 使用场景

### 1. 复杂批量操作

当需要对大量对象执行复杂逻辑时：

```python
script.execute(code="""
import bpy

# 批量调整所有网格对象的位置
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.location.z += obj.dimensions.z / 2

result = sum(1 for o in bpy.data.objects if o.type == 'MESH')
""")
# 返回：{"success": true, "return_value": 15, ...}
```

### 2. BMesh 底层操作

直接操作网格几何：

```python
script.execute(code="""
import bpy
import bmesh

obj = bpy.data.objects['Cube']
bm = bmesh.new()
bm.from_mesh(obj.data)

# 删除所有非四边形面
non_quads = [f for f in bm.faces if len(f.verts) != 4]
bmesh.ops.delete(bm, geom=non_quads, context='FACES')

bm.to_mesh(obj.data)
bm.free()

result = len(obj.data.polygons)
""")
```

### 3. 自定义算法

实现特定的几何算法：

```python
script.execute(code="""
import bpy
from mathutils import Vector

# 将所有顶点投影到球面
obj = bpy.data.objects['Cube']
mesh = obj.data
radius = 2.0

for vert in mesh.vertices:
    vert.co = vert.co.normalized() * radius

mesh.update()
""")
```

### 4. 复杂节点操作

程序化创建复杂节点网络：

```python
script.execute(code="""
import bpy

mat = bpy.data.materials.new("ProceduralMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# 清空默认节点
nodes.clear()

# 创建节点网络
output = nodes.new('ShaderNodeOutputMaterial')
principled = nodes.new('ShaderNodeBsdfPrincipled')
noise = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')

# 设置位置
output.location = (300, 0)
principled.location = (0, 0)
noise.location = (-400, 0)
color_ramp.location = (-200, 0)

# 连接
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

result = mat.name
""")
```

### 5. 访问未暴露的 API

某些 Blender API 可能未通过标准工具暴露：

```python
script.execute(code="""
import bpy

# 访问 Cycles 渲染设置
scene = bpy.context.scene
if scene.render.engine == 'CYCLES':
    cycles = scene.cycles
    cycles.samples = 128
    cycles.use_denoising = True
    cycles.denoiser = 'OPENIMAGEDENOISE'
    
result = {"samples": cycles.samples, "denoising": cycles.use_denoising}
""")
```

## 安全注意事项

### 风险等级：🔴 极高

此工具可以执行任意代码，可能导致：
- 文件系统访问/修改/删除
- 网络请求
- 系统命令执行
- Blender 崩溃
- 数据丢失

### 建议的安全措施

1. **仅在受信任环境中启用**
   - 本地开发环境
   - 隔离的测试环境

2. **设置合理的超时**
   - 防止无限循环
   - 默认 30 秒

3. **审计日志**
   - 记录所有执行的代码
   - 记录执行结果

4. **用户确认**
   - 每次执行前显示代码
   - 要求用户明确批准

## 返回值说明

### 成功执行

```json
{
    "success": true,
    "output": "Processing complete\n",
    "error": null,
    "return_value": {"count": 15, "status": "ok"},
    "execution_time_ms": 125.5
}
```

### 执行错误

```json
{
    "success": false,
    "output": "",
    "error": "NameError: name 'undefined_var' is not defined",
    "return_value": null,
    "execution_time_ms": 5.2
}
```

### 超时

```json
{
    "success": false,
    "output": "",
    "error": "Execution timeout after 30 seconds",
    "return_value": null,
    "execution_time_ms": 30000.0
}
```

## 与其他工具的关系

`script.execute` 是**逃生舱**，应该仅在以下情况使用：

| 场景 | 推荐工具 | 使用 script.execute |
|-----|---------|-------------------|
| 创建/修改对象 | `data.*` | ❌ |
| 执行标准操作 | `operator.execute` | ❌ |
| 查询状态信息 | `info.query` | ❌ |
| BMesh 精细操作 | - | ✅ |
| 复杂批量逻辑 | - | ✅ |
| 自定义算法 | - | ✅ |
| 未暴露的 API | - | ✅ |

