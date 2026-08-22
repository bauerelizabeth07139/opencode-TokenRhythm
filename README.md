# OpenCode TokenRhythm + NVIDIA Provider Preset

本地 [opencode](https://opencode.ai) 的 [基元律动 (TokenRhythm)](https://tokenrhythm.studio) + NVIDIA NIM 模型提供商预设配置。

## 功能特性

- 接入 TokenRhythm 统一 API 端点：`https://tokenrhythm.studio/v1`
- 接入 NVIDIA NIM API 端点：`https://integrate.api.nvidia.com/v1`
- 内置 19 个 TokenRhythm 模型 + 7 个 NVIDIA NIM 模型
- 推理模型（DeepSeek V4、GLM-5、Kimi K2.x、Mimo、MiniMax M2.x、Qwen3.x）开启推理（`reasoning: true`）
- 多模态模型（Seed 2.1 Pro/Turbo: 图像+视频、Kimi K2.5/K2.6/K2.7-code: 图像、Qwen3.8 Max: 图像）开启附件支持（`attachment: true`）
- 按官方文档填写了各模型的上下文窗口与最大输出长度

## TokenRhythm 模型列表

| 模型 | 上下文 | 最大输出 | 推理 | 附件 | 模态 |
|------|--------|---------|------|------|------|
| deepseek-v4-flash | 1M | 384K | ✓ | - | 文本 |
| deepseek-v4-pro | 1M | 384K | ✓ | - | 文本 |
| deepseek-v4-flash-0731 | 1M | 384K | ✓ | - | 文本 |
| deepseek-v4-pro-0813 | 1M | 384K | ✓ | - | 文本 |
| seed-2.1-pro | 262.1K | 131.1K | ✓ | ✓ | 文本/图像/视频 |
| seed-2.1-turbo | 262.1K | 131.1K | ✓ | ✓ | 文本/图像/视频 |
| glm-5 | 1M | 128K | ✓ | - | 文本 |
| glm-5.1 | 200K | 128K | ✓ | - | 文本 |
| glm-5.2 | 1M | 128K | ✓ | - | 文本 |
| kimi-k2.5 | 256K | 64K | ✓ | ✓ | 文本/图像 |
| kimi-k2.6 | 256K | 128K | ✓ | ✓ | 文本/图像 |
| kimi-k2.7-code | 256K | 16K | ✓ | ✓ | 文本/图像 |
| mimo-v2.5-pro | 256K | 256K | ✓ | - | 文本 |
| minimax-m2.5 | 200K | 200K | ✓ | - | 文本 |
| minimax-m2.7 | 200K | 192K | ✓ | - | 文本 |
| qwenvl-2.0 | - | - | - | - | 图像生成 |
| qwen3.7-max | 1M | 131.1K | ✓ | - | 文本 |
| qwen3.8-max | 1M | 131.1K | ✓ | ✓ | 文本/图像 |
| wan2.7-image | - | - | - | - | 图像生成 |

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

## 一键安装 (Windows)

从 [Releases](https://github.com/bauerelizabeth07139/opencode-TokenRhythm/releases) 下载 `opencode-TokenRhythm-Setup.exe` 并运行，自动将配置安装到 `~/.config/opencode/opencode.jsonc`（已存在则先备份为 `.bak`）。

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

然后用 `/models` 选择模型开始使用。

## 相关链接

- [TokenRhythm 文档](https://tokenrhythm.studio/docs/overview)
- [TokenRhythm 模型列表](https://tokenrhythm.studio/models)
- [NVIDIA NIM API](https://build.nvidia.com/explore/discover)
- [OpenCode Provider 配置文档](https://opencode.ai/docs/providers)
