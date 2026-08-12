# OpenCode TokenRhythm Provider Preset

本地 [opencode](https://opencode.ai) 的 [基元律动 (TokenRhythm)](https://tokenrhythm.studio) 模型提供商预设配置。

## 功能特性

- 接入 TokenRhythm 统一 API 端点：`https://tokenrhythm.studio/v1`
- 内置 16 个 LLM 文本模型（DeepSeek V4、Seed 2.1、GLM-5、Kimi K2.x、Mimo、MiniMax M2.x、Qwen3.x）
- 所有模型均开启推理（`reasoning: true`），思考档位最高为 `max`
- 多模态模型（Seed 2.1、Kimi K2.x）开启附件支持（`attachment: true`）
- 按官方文档填写了各模型的上下文窗口与最大输出长度

## 模型列表

| 模型 | 上下文 | 最大输出 | 推理 | 附件 |
|------|--------|---------|------|------|
| deepseek-v4-flash | 1M | 384K | ✓ | - |
| deepseek-v4-pro | 1M | 384K | ✓ | - |
| deepseek-v4-flash-0731 | 1M | 384K | ✓ | - |
| seed-2.1-pro | 262.1K | 131.1K | ✓ | ✓ |
| seed-2.1-turbo | 262.1K | 131.1K | ✓ | ✓ |
| glm-5 | 1M | 128K | ✓ | - |
| glm-5.1 | 200K | 128K | ✓ | - |
| glm-5.2 | 1M | 128K | ✓ | - |
| kimi-k2.5 | 256K | 64K | ✓ | ✓ |
| kimi-k2.6 | 256K | 128K | ✓ | ✓ |
| kimi-k2.7-code | 256K | 128K | ✓ | ✓ |
| mimo-v2.5-pro | 256K | 256K | ✓ | - |
| minimax-m2.5 | 200K | 200K | ✓ | - |
| minimax-m2.7 | 200K | 192K | ✓ | - |
| qwen3.7-max | 1M | 131.1K | ✓ | - |
| qwen3.8-max | 1M | 131.1K | ✓ | - |

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

在 opencode 中输入 `/connect`，选择 **Other**，Provider ID 填 `tokenrhythm`，粘贴你的 TokenRhythm API Key（在 [tokenrhythm.studio](https://tokenrhythm.studio) 注册后获取）。

然后用 `/models` 选择模型开始使用。

## 相关链接

- [TokenRhythm 文档](https://tokenrhythm.studio/docs/overview)
- [TokenRhythm 模型列表](https://tokenrhythm.studio/models)
- [OpenCode Provider 配置文档](https://opencode.ai/docs/providers)
