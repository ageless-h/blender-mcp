# CI Matrix

> 更新日期: 2026-02-08

## CI 配置

文件: `.github/workflows/ci.yml`

## Matrix Dimensions

| 维度 | 值 |
|------|------|
| Blender | 4.2 LTS, 4.5 LTS |
| OS | ubuntu-latest, windows-latest, macos-latest |
| Python | 3.11+ |

## 测试阶段

1. **快速单元测试** (无 Blender): `uv run python -m unittest discover -s tests -p "test_*.py"`
   - 271 tests, ~12 秒
   - 使用 MCP_ADAPTER=mock
2. **真实 Blender 测试** (需 opt-in): `tests/integration/real_blender/`
   - 需要下载 Blender 二进制
   - 通过 `scripts/run_real_blender_tests.py` 执行

## Execution Notes
Integration jobs should be separated from fast unit checks and require caching of Blender binaries.
