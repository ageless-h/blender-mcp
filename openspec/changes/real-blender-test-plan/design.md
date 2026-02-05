## Context

当前项目使用 `MockAdapter` 进行集成测试，测试路径为 `tests/integration/`，harness 定义在 `_harness.py`。现有 addon 已包含 socket server 实现（`addon/socket_server.py`），支持 JSON 协议通信。

用户本地已部署三个 Blender 版本：
- 4.2.17 LTS: `F:\Program Files\blender\LTS\blender-4.2.17-windows-x64\blender.exe`
- 4.5.6 LTS: `F:\Program Files\blender\LTS\blender-4.5.6-windows-x64\blender.exe`
- 5.0.1: `F:\Program Files\blender\blender-5.0.1-windows-x64\blender.exe`

项目约束：测试基础设施不应引入重量级依赖；socket 通信已是既定方案；测试需支持 `--background` 模式运行。

## Goals / Non-Goals

**Goals:**
- 提供可配置的 Blender 路径发现机制
- 实现启动真实 Blender 进程并建立 socket 通信的 harness
- 支持按版本矩阵批量执行测试
- 测试结果可导出为 `compatibility-results.json` 格式
- 与现有 `unittest` 框架集成

**Non-Goals:**
- 不实现 Blender 自动下载/安装
- 不支持远程 Blender 实例测试
- 不覆盖 GUI 交互测试（仅 `--background` 模式）
- 不实现 CI 自动化（本期仅本地执行）

## Decisions

### Decision 1: Blender 路径配置方式

**选择**: JSON 配置文件 + 环境变量覆盖

```
tests/blender-paths.json (gitignored)
{
  "blender_executables": [
    {
      "version": "4.2.17",
      "path": "F:\\Program Files\\blender\\LTS\\blender-4.2.17-windows-x64\\blender.exe",
      "tags": ["lts", "baseline"]
    },
    ...
  ]
}
```

环境变量 `BLENDER_TEST_PATHS` 可覆盖配置文件路径。

**备选方案**:
- 纯环境变量：多版本配置繁琐
- pyproject.toml 内嵌：路径包含用户特定信息，不宜 commit

**理由**: JSON 文件支持结构化多版本配置，gitignore 保护用户路径隐私，环境变量提供 CI 灵活性。

### Decision 2: 测试 Harness 架构

**选择**: `BlenderProcessHarness` 类，封装进程生命周期

```python
class BlenderProcessHarness:
    def __init__(self, blender_path: str, port: int = 9876):
        ...
    
    def start(self, timeout: float = 30.0) -> bool:
        """启动 Blender 进程，注入 socket server 脚本，等待就绪"""
        
    def send_request(self, request: dict) -> dict:
        """发送 capability 请求，返回响应"""
        
    def stop(self) -> None:
        """终止 Blender 进程"""
        
    def __enter__ / __exit__:
        """Context manager 支持"""
```

启动流程:
1. 使用 `subprocess.Popen` 启动 `blender.exe --background --python addon/start_socket_server.py`
2. 轮询 socket 连接直到成功或超时
3. 测试完成后 terminate 进程

**备选方案**:
- 使用现有 `addon/poc_harness.py`：该脚本设计为在 Blender 内运行，非外部控制
- Blender 作为持久服务：增加复杂度，隔离性差

**理由**: 每测试独立进程确保隔离性；context manager 模式简化资源管理；复用现有 socket server 代码。

### Decision 3: 端口分配策略

**选择**: 动态端口 + 环境变量传递

```python
def find_free_port() -> int:
    with socket.socket() as s:
        s.bind(('', 0))
        return s.getsockname()[1]
```

通过环境变量 `MCP_SOCKET_PORT` 传递给 Blender 进程。

**备选方案**:
- 固定端口 9876：并行测试会冲突
- 进程参数传递：需修改 socket server 脚本

**理由**: 动态端口支持并行测试；环境变量无需修改现有脚本。

### Decision 4: 测试文件组织

**选择**: 新增 `tests/integration/real_blender/` 目录

```
tests/integration/
├── _harness.py              # 现有 Mock harness
├── test_workflows.py        # 现有 Mock 测试
└── real_blender/
    ├── __init__.py
    ├── _blender_harness.py  # BlenderProcessHarness
    ├── _config.py           # 路径配置加载
    └── test_real_capabilities.py
```

**理由**: 与现有 Mock 测试分离；避免 CI 因缺少 Blender 而失败；支持独立运行。

### Decision 5: 多版本测试执行

**选择**: 参数化测试 + 汇总脚本

```python
# test_real_capabilities.py
@pytest.mark.parametrize("blender_config", load_blender_configs())
def test_scene_read(blender_config):
    with BlenderProcessHarness(blender_config["path"]) as harness:
        response = harness.send_request({"capability": "scene.read", "payload": {}})
        assert response["ok"]
```

独立脚本 `scripts/run_real_blender_tests.py` 汇总结果到 `compatibility-results.json`。

**备选方案**:
- 每版本独立测试文件：代码重复
- 自定义 test runner：偏离标准 pytest 生态

**理由**: pytest 参数化原生支持多版本；汇总脚本解耦测试执行与报告生成。

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| Blender 启动慢（5-10秒） | 测试按 session 复用进程；标记为慢测试 |
| 端口竞争（并行执行） | 动态端口分配 |
| 路径配置错误 | 启动时验证路径存在并检测版本 |
| Windows 路径问题 | 使用 `pathlib.Path` 规范化 |
| 进程泄漏（异常退出） | `atexit` 注册清理；context manager 确保 stop |
| 测试结果不稳定 | 增加重试机制；记录 Blender 输出日志 |

## Open Questions

1. **pytest vs unittest**: 现有项目使用 `unittest`，是否迁移到 pytest 以获得参数化支持？
   - 建议：真实 Blender 测试使用 pytest，保持现有 unittest 测试不变

2. **超时配置**: Blender 启动超时默认 30 秒是否合适？
   - 建议：可配置，默认 30 秒，慢机器可调整

3. **测试覆盖范围**: 第一期覆盖哪些 capability？
   - 建议：`scene.read`, `scene.write` 核心路径

