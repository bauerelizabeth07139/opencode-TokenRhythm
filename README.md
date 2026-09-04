# OpenCode TokenRhythm + NVIDIA Provider Preset

本地 [opencode](https://opencode.ai) 的 [基元律动 (TokenRhythm)](https://tokenrhythm.studio) + NVIDIA NIM 模型提供商预设配置。

## 功能特性

- 接入 TokenRhythm 统一 API 端点：`https://tokenrhythm.studio/v1`
- 接入 NVIDIA NIM API 端点：`https://integrate.api.nvidia.com/v1`
- 内置 20 个 TokenRhythm 模型 + 7 个 NVIDIA NIM 模型
- 推理模型（DeepSeek V4、GLM-5.x、Kimi K2.x、LongCat、Mimo、MiniMax M2.x、Qwen3.x）开启推理（`reasoning: true`）
- 多模态模型（Qwen3.8-27B/GLM-5.3 Flash/Qwen3.7 Flash: 图像+视频、Seed 2.1 Pro/Turbo: 图像+视频、Kimi K2.5/K2.6/K2.7-code: 图像）开启附件支持（`attachment: true`）
- 内置图像生成 MCP 服务器（`qwen-image-2.0`），API Key 从环境变量 `TOKENRHYTHM_API_KEY` 读取，无需写入配置文件
- 按官方文档填写了各模型的上下文窗口与最大输出长度

## TokenRhythm 模型列表

| 模型 | 上下文 | 最大输出 | 推理 | 附件 | 模态 |
|------|--------|---------|------|------|------|
| qwen3.8-27b | 1M | 131K | ✓ | ✓ | 文本/图像/视频 |
| deepseek-v4-flash-0731 | 1M | 384K | ✓ | - | 文本 |
| deepseek-v4-pro-0813 | 1M | 384K | ✓ | - | 文本 |
| glm-5 | 1M | 128K | ✓ | - | 文本 |
| glm-5.1 | 200K | 128K | ✓ | - | 文本 |
| glm-5.2 | 1M | 128K | ✓ | - | 文本 |
| glm-5.3 | 1.05M | 131K | ✓ | - | 文本 |
| glm-5.3-flash | 1.05M | 131K | ✓ | ✓ | 文本/图像/视频 |
| kimi-k2.5 | 256K | 64K | ✓ | ✓ | 文本/图像 |
| kimi-k2.6 | 256K | 128K | ✓ | ✓ | 文本/图像 |
| kimi-k2.7-code | 256K | 16K | ✓ | ✓ | 文本/图像 |
| longcat-2.0 | 1M | 128K | ✓ | - | 文本 |
| seed-2.1-pro | 262K | 131K | ✓ | ✓ | 文本/图像/视频 |
| seed-2.1-turbo | 262K | 131K | ✓ | ✓ | 文本/图像/视频 |
| mimo-v2.5-pro | 256K | 256K | ✓ | - | 文本 |
| minimax-m2.5 | 200K | 200K | ✓ | - | 文本 |
| minimax-m2.7 | 200K | 192K | ✓ | - | 文本 |
| qwen-image-2.0 | - | - | - | - | 图像生成 |
| qwen3.7-flash | 1M | 131K | ✓ | ✓ | 文本/图像/视频 |
| qwen3.7-max | 1M | 131K | ✓ | - | 文本 |

## NVIDIA NIM 模型列表

| 模型 | 上下文 | 最大输出 | 推理 |
|------|--------|---------|------|
| llama-3.1-nemotron-ultra-253b-v1 | 128K | 8K | ✓ |
| llama-3.3-nemotron-super-49b-v1 | 128K | 8K | ✓ |
| deepseek-r1 | 128K | 8K | ✓ |
| mistral-large-2-instruct | 128K | 8K | ✓ |
| qwen2.5-72b-instruct | 128K | 8K | ✓ |
| llama-4-maverick-17b | 128K | 8K | ✓ |
| llama-4-scout-17b | 128K | 8K | ✓ |

## 安装

将 `opencode.jsonc` 复制到 opencode 全局配置目录：

```bash
# 全局配置目录（Windows）
copy opencode.jsonc %USERPROFILE%\.config\opencode\opencode.jsonc

# 或合并到已有配置
```

> 注意：`opencode.jsonc` 中配置了 TokenRhythm 图像生成 MCP 服务器，其脚本路径为
> `~/.config/opencode/mcp/tokenrhythm_image_mcp.py`。若需要图像生成功能，请把
> `mcp/tokenrhythm_image_mcp.py` 一并复制到该位置（见下文「图像生成 (MCP)」一节）；
> 否则可在合并配置时删除 `mcp` 块，不影响聊天/推理模型使用。

## 一键安装 (Windows)

从 [Releases](https://github.com/bauerelizabeth07139/opencode-TokenRhythm/releases) 下载 `opencode-TokenRhythm-Setup.exe` 并运行，自动将配置安装到 `~/.config/opencode/opencode.jsonc`（已存在则先备份为 `.bak`）。

> 注意：该安装器只安装 `opencode.jsonc`。图像生成 MCP 脚本需要手动复制，并设置
> `TOKENRHYTHM_API_KEY`（见下文）。

源码见 `installer/Installer.cs`，使用 .NET 编译器构建：

```bash
csc /nologo /optimize+ /target:exe /out:opencode-TokenRhythm-Setup.exe ^
    /resource:opencode.jsonc,opencode.jsonc installer\Installer.cs
```

## 配置 API Key

### TokenRhythm

在 opencode 中输入 `/connect`，选择 **Other**，Provider ID 填 `tokenrhythm`，粘贴你的 TokenRhythm API Key（在 [tokenrhythm.studio](https://tokenrhythm.studio) 注册后获取）。

### NVIDIA NIM

在 opencode 中输入 `/connect`，选择 **Other**，Provider ID 填 `nvidia`，粘贴你的 NVIDIA NIM API Key（在 [build.nvidia.com](https://build.nvidia.com) 获取）。

### 图像生成 (MCP)

图像生成通过 MCP 服务器调用 TokenRhythm 的 `qwen-image-2.0` 模型，API Key 从环境变量读取：

1. 将 `mcp/tokenrhythm_image_mcp.py` 复制到 `~/.config/opencode/mcp/tokenrhythm_image_mcp.py`（与 `opencode.jsonc` 中配置的路径一致）
2. 设置环境变量 `TOKENRHYTHM_API_KEY` 为你的 TokenRhythm API Key：
   ```bash
   # PowerShell
   setx TOKENRHYTHM_API_KEY "你的-API-Key"
   # CMD
   set TOKENRHYTHM_API_KEY=你的-API-Key
   ```
   然后重启 opencode 使其生效；也可以在 `opencode.jsonc` 的 `mcp.tokenrhythm-image-gen.environment` 中直接填写（不推荐，注意不要提交到版本库）。
3. 生成的图片保存到 `~/.config/opencode/generated_images/`

## 使用示例

```text
/models                       # 打开模型选择器，输入 tokenrhythm/ 或 nvidia/ 过滤 Provider
                              # 带推理档位的模型（如 glm-5.3、kimi-k2.6）可在选择器中切换
                              #   low / medium / high 三档思考强度（reasoningEffort）
/connect                      # 首次使用：配置 tokenrhythm 或 nvidia 的 API Key
```

对话示例：

- 文本问答：`用 qwen3.7-max 写一个 Python 快速排序`
- 多模态：`分析这张图片的内容`（粘贴图片后发送）
- 图像生成：`帮我生成一张赛博朋克风格的城市夜景图片`（自动调用 `generate_image` 工具）

## 验证配置

仓库内置配置校验脚本（CI 中也会自动运行）：

```bash
python scripts/validate_config.py
```

脚本会检查 `opencode.jsonc` 的 JSONC 语法、Provider/模型 ID 唯一性、上下文与输出长度、
MCP 配置中是否存在硬编码密钥，并对 MCP 脚本做语法检查。

## 相关链接

- [TokenRhythm 文档](https://tokenrhythm.studio/docs/overview)
- [TokenRhythm 模型列表](https://tokenrhythm.studio/models)
- [NVIDIA NIM API](https://build.nvidia.com/explore/discover)
- [OpenCode Provider 配置文档](https://opencode.ai/docs/providers)
