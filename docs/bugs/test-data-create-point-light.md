# Test Report: data.create - Point Light Creation

## Test Objective
验证 `data.create` 工具创建点光源对象的功能。

## Test Environment
- Tool: `data.create`
- Restrictions: 禁止使用 `operator.execute`
- Test Date: 2026-02-06

## Test Case

### Input
```json
{
  "type": "light",
  "name": "PointLight",
  "data": {
    "type": "POINT",
    "energy": 1000,
    "color": [1, 1, 1]
  }
}
```

### Output
```json
{
  "name": "PointLight",
  "type": "light",
  "light_type": "POINT"
}
```

## Observation

- 请求成功执行
- 返回对象包含名称、类型和光源类型信息
- `energy` 和 `color` 参数在响应中未体现（可能未存储或未返回）
- **对象未链接到场景视图层** - 光源数据被创建但不在场景中可见

## Comparison

| 对象类型 | data.create 结果 |
|---------|-----------------|
| mesh (cylinder) | 失败 - 几何数据为0 |
| light (point) | 成功 - 对象已创建 |

## Status
记录存档

## Notes
后续需要验证该光源是否实际存在于场景中被正确渲染。
