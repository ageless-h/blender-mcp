# Test Report: data.create - Camera Creation

## Test Objective
验证 `data.create` 工具创建摄像机对象的功能。

## Test Environment
- Tool: `data.create`
- Restrictions: 禁止使用 `operator.execute`
- Test Date: 2026-02-06

## Test Case

### Input
```json
{
  "type": "camera",
  "name": "Camera_01",
  "data": {
    "type": "PERSP",
    "lens": 35,
    "clip_start": 0.1,
    "clip_end": 1000
  }
}
```

### Output (Create)
```json
{
  "name": "Camera_01",
  "type": "camera"
}
```

### Output (Read Verification)
```json
{
  "name": "Camera_01",
  "type": "PERSP",
  "lens": 50.0,
  "lens_unit": "MILLIMETERS",
  "clip_start": 0.10000000149011612,
  "clip_end": 1000.0,
  "dof_focus_distance": 10.0
}
```

## Observation

- ✅ 请求成功执行
- ✅ 摄像机对象成功创建
- ⚠️ 部分参数正确存储：
  - `type`: PERSP ✓ (正确)
  - `clip_start`: 0.1 ✓ (正确)
  - `clip_end`: 1000.0 ✓ (正确)
  - `lens`: 50.0 ❌ (请求 35，使用了默认值 50)

## 问题

`lens` 参数被忽略，使用了默认值 50mm 而非请求的 35mm。

## Comparison

| 对象类型 | data.create 结果 | 备注 |
|---------|-----------------|------|
| mesh (圆柱体) | ❌ 失败 | 几何数据为0 |
| light (点光源) | ⚠️ 部分 | 参数未返回，未链接场景 |
| curve (贝塞尔曲线) | ❌ 失败 | 样条数据丢失 |
| metaball | ❌ 不支持 | `unsupported_type` |
| text/font | ❌ 不支持 | `unsupported_type` 或强制转 MESH |
| grease_pencil | ❌ 不支持 | `unsupported_type` |
| **camera** | ⚠️ **部分** | 对象创建成功，但 `lens` 参数被忽略 |

## Status

功能部分可用，`lens` 参数需要修复。

## Notes

摄像机可能是 `data.create` 中工作最完整的类型之一，仅有一个参数未被正确处理。
