# opencode-TokenRhythm 🎵

[基元律动 (TokenRhythm)](https://tokenrhythm.studio) + [NVIDIA NIM](https://build.nvidia.com) provider **preset** for [opencode](https://opencode.ai).

双击 / 运行打包好的 **EXE**，即可一键把 TokenRhythm 与 NVIDIA 的全部模型预设加入 opencode —— 之后在 `/models`
中就能看到所有模型，其中支持多模态的模型（Kimi / Seed / Qwen / MiniMax-M3 等）已正确标记为可接收图片 / 视频附件。
NVIDIA 的模型使用英文名并标注 **(英伟达)** 以区分同名模型。

## 快速开始（Windows）

```powershell
# 1. 运行安装器（直接运行，无需安装任何依赖）
.\dist\opencode-tokenrhythm-preset.exe

# 2. 设置 API Key（至少一个）
[Environment]::SetEnvironmentVariable("TOKENRHYTHM_API_KEY", "sk_xxx", "User")        # tokenrhythm.studio
[Environment]::SetEnvironmentVariable("NVIDIA_API_KEY", "nvapi-xxx", "User")          # build.nvidia.com

# 3. 重启 opencode，在对话中执行 /models 即可看到全部 TokenRhythm 与 NVIDIA 模型
```

安装器默认会：
1. 把 `provider.tokenrhythm` 与 `provider.nvidia` 合并进全局配置 `~/.config/opencode/opencode.json`（或 `opencode.jsonc`）；
2. 在 `~/.config/opencode/plugins/tokenrhythm.js` 安装一个插件，注册全部模型（含多模态标记）。

## 从源码运行 / 打包 EXE

```bash
# 直接运行安装器
python install_preset.py

# 打包为 EXE（Windows）
powershell -ExecutionPolicy Bypass -File build_exe.ps1
# 产物：dist\opencode-tokenrhythm-preset.exe
```

```bash
# macOS / Linux
./build_exe.sh
# 产物：dist/opencode-tokenrhythm-preset
```

## 安装器命令

| 命令 | 说明 |
|------|------|
| `install_preset.exe` | 安装预设（默认：合并配置 + 安装插件） |
| `install_preset.exe --plugin` | 仅安装插件文件 |
| `install_preset.exe --dry-run` | 预览将执行的操作，不写入任何文件 |
| `install_preset.exe --uninstall` | 从配置中移除 tokenrhythm 与 nvidia provider |
| `install_preset.exe --project` | 安装到当前目录的 `opencode.json` 而不是全局配置 |

## 模型列表（https://tokenrhythm.studio/models）

> 已自动核对模态支持。✅ = 多模态（支持图片/视频输入），opencode 将允许发送附件。

### 多模态模型（vision，可发图片）

| 模型 | 模态 | 上下文 | 最大输出 | 输入 ¥/M | 输出 ¥/M |
|------|------|--------|---------|---------|---------|
| `kimi-k2.5` | 文本 / 图像 | 256K | 64K | 4.00 | 21.00 |
| `kimi-k2.6` | 文本 / 图像 | 256K | 128K | 6.50 | 27.00 |
| `kimi-k2.7-code` | 文本 / 图像 | 256K | 16K | 6.50 | 27.00 |
| `seed-2.1-pro` | 文本 / 图像 / 视频 | 262.1K | 131.1K | 6.00 | 30.00 |
| `seed-2.1-turbo` | 文本 / 图像 / 视频 | 262.1K | 131.1K | 3.00 | 15.00 |
| `qwen3.8-max` | 文本 / 图像 | 1M | 131.1K | 12.00 | 36.00 |

### 纯文本模型

| 模型 | 上下文 | 最大输出 | 输入 ¥/M | 输出 ¥/M |
|------|--------|---------|---------|---------|
| `deepseek-v4-flash` | 1M | 384K | 1.00 | 2.00 |
| `deepseek-v4-pro` | 1M | 384K | 12.00 | 24.00 |
| `deepseek-v4-flash-0731` | 1M | 384K | 3.00 | 9.00 |
| `deepseek-v4-pro-0813` | 1M | 384K | 9.00 | 27.00 |
| `glm-5` | 1M | 128K | 6.00 | 22.00 |
| `glm-5.1` | 200K | 128K | 8.00 | 28.00 |
| `glm-5.2` | 1M | 128K | 8.00 | 28.00 |
| `mimo-v2.5-pro` | 256K | 256K | 3.00 | 6.00 |
| `minimax-m2.5` | 200K | 200K | 2.10 | 8.40 |
| `minimax-m2.7` | 200K | 192K | 2.10 | 8.40 |
| `qwen3.7-max` | 1M | 131.1K | 12.00 | 36.00 |

> 图片生成模型 `qwen-image-2.0`、`wan2.7-image` 属于图像生成（非对话）模型，不加入聊天 provider，见
> [opencode-tokenrhythm-image-mcp](https://github.com/bauerelizabeth07139/opencode-tokenrhythm-image-mcp)。

## NVIDIA 模型（英伟达，https://integrate.api.nvidia.com/v1）

> provider id `nvidia`，API Key 放在环境变量 `NVIDIA_API_KEY`。共 37 个对话模型，其中 16 个为多模态（支持图片/视频输入）。

### 多模态模型（vision，可发图片 / 视频）

| 模型 | 模态 | 上下文 | 最大输出 |
|------|------|--------|---------|
| `minimaxai/minimax-m3` | 文本 / 图像 / 视频（推理） | 1M | 8K |
| `moonshotai/kimi-k3` | 文本 / 图像 / 视频（推理） | 1M | 32K |
| `moonshotai/kimi-k2.6` | 文本 / 图像 / 视频（推理） | 256K | 16K |
| `meta/llama-3.2-11b-vision-instruct` | 文本 / 图像 | 128K | 8K |
| `meta/llama-3.2-90b-vision-instruct` | 文本 / 图像 | 128K | 8K |
| `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | 文本 / 图像 | 128K | 4K |
| `nvidia/nemotron-nano-12b-v2-vl` | 文本 / 图像 / 视频 | 128K | 8K |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | 文本 / 图像 / 视频（推理） | 128K | 16K |
| `microsoft/phi-3-vision-128k-instruct` | 文本 / 图像 | 128K | 8K |
| `google/gemma-3-4b-it` | 文本 / 图像 | 128K | 8K |
| `google/gemma-3-12b-it` | 文本 / 图像 | 128K | 8K |
| `google/gemma-4-31b-it` | 文本 / 图像 | 256K | 16K |
| `stepfun-ai/step-3.7-flash` | 文本 / 图像（推理） | 256K | 8K |
| `thinkingmachines/inkling` | 文本 / 图像（推理） | 128K | 16K |
| `meta/muse-glimmer-30b` | 文本 / 图像（推理） | 128K | 16K |
| `nvidia/vila` | 文本 / 图像 | 32K | 4K |

### 纯文本模型

| 模型 | 上下文 | 最大输出 | 备注 |
|------|--------|---------|------|
| `deepseek-ai/deepseek-v4-flash-0731` | 1M | 16K | 推理 |
| `z-ai/glm-5.2` | 1M | 16K | 推理 |
| `meta/llama-3.1-8b-instruct` | 128K | 8K | |
| `meta/llama-3.3-70b-instruct` | 128K | 8K | |
| `nvidia/llama-3.1-nemotron-70b-instruct` | 128K | 8K | |
| `nvidia/llama-3.1-nemotron-ultra-253b-v1` | 128K | 8K | |
| `nvidia/llama-3.3-nemotron-super-49b-v1` | 128K | 8K | |
| `nvidia/llama-3.3-nemotron-super-49b-v1.5` | 128K | 8K | |
| `nvidia/nemotron-3-super-120b-a12b` | 128K | 16K | |
| `nvidia/nemotron-3-ultra-550b-a55b` | 128K | 16K | |
| `nvidia/nemotron-3.5-lightning-30b-a3b` | 128K | 16K | |
| `nvidia/nemotron-nano-3-30b-a3b` | 128K | 8K | |
| `nvidia/nemotron-mini-4b-instruct` | 128K | 8K | |
| `mistralai/mistral-large` | 128K | 8K | |
| `mistralai/mistral-large-2-instruct` | 128K | 8K | |
| `mistralai/mistral-nemotron` | 128K | 8K | |
| `mistralai/mixtral-8x22b-v0.1` | 64K | 8K | |
| `openai/gpt-oss-20b` | 128K | 16K | 推理 |
| `openai/gpt-oss-120b` | 128K | 16K | 推理 |
| `google/codegemma-7b` | 16K | 4K | 代码 |
| `zyphra/zamba2-7b-instruct` | 128K | 8K | |

## 手动配置（不用 EXE）

也可以直接把 `preset/tokenrhythm.json` 的内容合并进你的 `opencode.json`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "tokenrhythm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "TokenRhythm (基元律动)",
      "options": { "baseURL": "https://tokenrhythm.studio/v1" },
      "env": ["TOKENRHYTHM_API_KEY"],
      "models": { /* 见 preset/tokenrhythm.json */ }
    },
    "nvidia": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NVIDIA (英伟达)",
      "options": { "baseURL": "https://integrate.api.nvidia.com/v1" },
      "env": ["NVIDIA_API_KEY"],
      "models": { /* 见 preset/tokenrhythm.json */ }
    }
  }
}
```

> `@ai-sdk/openai-compatible` 会被 opencode 自动安装（Bun）。API Key 放在环境变量 `TOKENRHYTHM_API_KEY` / `NVIDIA_API_KEY`。

## 目录结构

```
opencode-TokenRhythm/
├── install_preset.py        # 安装器主程序（打包为 EXE 的入口）
├── build_exe.ps1            # Windows 打包脚本
├── build_exe.sh             # macOS / Linux 打包脚本
├── plugin/
│   └── tokenrhythm.js       # opencode 插件（注册全部模型，含多模态标记）
├── preset/
│   └── tokenrhythm.json     # 可直接合并的 provider 预设（JSON）
├── models/
│   └── models.json          # 模型目录（数据源：tokenrhythm.studio/models + build.nvidia.com 模型清单）
└── README.md
```

## License

MIT