# Quick Start Guide / 快速开始指南

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

Get Blender MCP running in **5 minutes**.

### Prerequisites

- **Blender 4.2+** installed
- **Python 3.11+** installed
- **uv** installed ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

### Step 1: Install the Blender Addon

1. Copy or symlink `src/blender_mcp_addon/` to your Blender addons folder:
   - **Windows**: `%APPDATA%\Blender\<version>\scripts\addons\blender_mcp_addon`
   - **macOS**: `~/Library/Application Support/Blender/<version>/scripts/addons/blender_mcp_addon`
   - **Linux**: `~/.config/blender/<version>/scripts/addons/blender_mcp_addon`

2. In Blender: **Edit > Preferences > Add-ons** > Search "Blender MCP" > Enable

3. In the 3D Viewport, press **N** to open the sidebar, find the **Blender MCP** tab, click **Start Server**

### Step 2: Configure Your MCP Client

Add this to your client's MCP configuration (e.g., Cursor, Windsurf, Claude Code):

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "MCP_ADAPTER": "socket",
        "MCP_SOCKET_HOST": "127.0.0.1",
        "MCP_SOCKET_PORT": "9876"
      }
    }
  }
}
```

See [docs/clients/](./clients/) for client-specific configuration guides.

### Step 3: Verify Connection

Ask your AI assistant:

> "List all objects in my Blender scene"

The assistant should call `blender_get_objects` and return a list of objects (e.g., the default Cube, Camera, Light).

### Step 4: Create Your First Object

Ask your AI assistant:

> "Create a red sphere at position (2, 0, 1)"

The assistant should:
1. Call `blender_create_object` to create a sphere
2. Call `blender_manage_material` to create and assign a red material
3. Call `blender_capture_viewport` to show you the result

**Congratulations!** You're now using Blender MCP.

---

### Troubleshooting

#### Connection Failed / Cannot connect to Blender

- **Check addon is running**: In Blender, press N > Blender MCP tab > verify server shows "Running"
- **Check port**: Default is `9876`. Ensure your client config matches the addon's port setting
- **Check firewall**: Allow local connections on the configured port

#### Timeout Errors

- The command may be too complex. Try breaking it into smaller steps
- Increase timeout: set `MCP_SOCKET_TIMEOUT` environment variable (default: 30 seconds)

#### "Object not found" Errors

- Object names are case-sensitive. Ask the assistant to call `blender_get_objects` first to list actual names

#### Server Not Appearing in Client

- Restart your MCP client after configuration changes
- Verify `uv` is installed and `uvx` is in your PATH: run `uvx --version` in terminal
- Check your client's developer console/logs for errors

#### Python / uv Not Found

- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows)
- Ensure `uvx` is in your system PATH

---

<a name="中文"></a>
## 中文

**5 分钟**内启动 Blender MCP。

### 前置条件

- 已安装 **Blender 4.2+**
- 已安装 **Python 3.11+**
- 已安装 **uv**（[安装指南](https://docs.astral.sh/uv/getting-started/installation/)）

### 第 1 步：安装 Blender 插件

1. 将 `src/blender_mcp_addon/` 复制或符号链接到 Blender 插件目录：
   - **Windows**: `%APPDATA%\Blender\<版本>\scripts\addons\blender_mcp_addon`
   - **macOS**: `~/Library/Application Support/Blender/<版本>/scripts/addons/blender_mcp_addon`
   - **Linux**: `~/.config/blender/<版本>/scripts/addons/blender_mcp_addon`

2. 在 Blender 中：**编辑 > 偏好设置 > 插件** > 搜索 "Blender MCP" > 启用

3. 在 3D 视口中按 **N** 打开侧边栏，找到 **Blender MCP** 标签，点击 **Start Server**

### 第 2 步：配置 MCP 客户端

将以下配置添加到你的客户端（如 Cursor、Windsurf、Claude Code）：

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"],
      "env": {
        "MCP_ADAPTER": "socket",
        "MCP_SOCKET_HOST": "127.0.0.1",
        "MCP_SOCKET_PORT": "9876"
      }
    }
  }
}
```

各客户端的详细配置请参考 [docs/clients/](./clients/)。

### 第 3 步：验证连接

向 AI 助手发送：

> "列出我 Blender 场景中的所有对象"

助手应调用 `blender_get_objects` 并返回对象列表（如默认的 Cube、Camera、Light）。

### 第 4 步：创建第一个对象

向 AI 助手发送：

> "在位置 (2, 0, 1) 创建一个红色球体"

助手应：
1. 调用 `blender_create_object` 创建球体
2. 调用 `blender_manage_material` 创建并分配红色材质
3. 调用 `blender_capture_viewport` 展示结果

**恭喜！** 你已经在使用 Blender MCP 了。

---

### 故障排除

#### 连接失败 / 无法连接 Blender

- **检查插件是否运行中**：在 Blender 中按 N > Blender MCP 标签 > 确认服务器显示 "Running"
- **检查端口**：默认为 `9876`，确保客户端配置与插件端口一致
- **检查防火墙**：允许配置端口的本地连接

#### 超时错误

- 命令可能过于复杂，尝试拆分为更小的步骤
- 增加超时：设置 `MCP_SOCKET_TIMEOUT` 环境变量（默认 30 秒）

#### "Object not found" 错误

- 对象名称区分大小写，先让助手调用 `blender_get_objects` 列出实际名称

#### 客户端中看不到服务器

- 修改配置后重启 MCP 客户端
- 确认 `uv` 已安装且 `uvx` 在 PATH 中：在终端运行 `uvx --version`
- 检查客户端的开发者控制台/日志

#### Python / uv 未找到

- 安装 uv：`curl -LsSf https://astral.sh/uv/install.sh | sh`（macOS/Linux）或 `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`（Windows）
- 确保 `uvx` 在系统 PATH 中
