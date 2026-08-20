#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TokenRhythm (基元律动) + NVIDIA (英伟达) provider presets installer for opencode.

Running this program (or its packaged .exe) directly installs provider presets
into opencode so that /models can see:

  1. TokenRhythm — every model listed on https://tokenrhythm.studio/models,
     with multimodal (vision) models (Kimi / Seed / Qwen series) correctly
     flagged as supporting image/video attachments.
  2. NVIDIA NIM — chat models served at https://integrate.api.nvidia.com/v1,
     with English display names annotated "(英伟达)" and multimodal models
     flagged as vision-capable.

Actions (default):
  1. Merge `provider.tokenrhythm` and `provider.nvidia` into the global
     opencode config (~/.config/opencode/opencode.json / opencode.jsonc).
  2. Install a plugin at ~/.config/opencode/plugins/tokenrhythm.js that
     keeps both model lists registered even if the config is re-generated.

Usage:
    install_preset.exe             # install presets (default)
    install_preset.exe --plugin    # only install the plugin file
    install_preset.exe --dry-run   # show what would be written, no changes
    install_preset.exe --uninstall # remove tokenrhythm + nvidia providers
    install_preset.exe --project   # install into ./opencode.json instead
"""

import argparse
import json
import os
import re
import sys

PLUGIN_NAME = "tokenrhythm.js"
NVIDIA_SUFFIX = " (英伟达)"

# ---------------------------------------------------------------------------
# Provider presets
# Cost figures are list prices in CNY (TokenRhythm) / USD (NVIDIA) per 1M
# tokens. `attachment`/`modalities` mark multimodal (vision) models.
# ---------------------------------------------------------------------------


def mm_attach(*modes):
    return {"attachment": True, "modalities": {"input": ["text"] + list(modes), "output": ["text"]}}


def mm_text():
    return {"attachment": False, "modalities": {"input": ["text"], "output": ["text"]}}


TOKENRHYTHM_PROVIDER = {
    "npm": "@ai-sdk/openai-compatible",
    "name": "TokenRhythm (基元律动)",
    "options": {"baseURL": "https://tokenrhythm.studio/v1"},
    "env": ["TOKENRHYTHM_API_KEY"],
    "models": {
        # ---- multimodal: text + image ----
        "kimi-k2.5": dict({"name": "Kimi K2.5", "limit": {"context": 256000, "output": 64000},
                           "cost": {"input": 4.0, "output": 21.0, "cache_read": 0.8}}, **mm_attach("image")),
        "kimi-k2.6": dict({"name": "Kimi K2.6", "limit": {"context": 256000, "output": 128000},
                           "cost": {"input": 6.5, "output": 27.0, "cache_read": 1.3}}, **mm_attach("image")),
        "kimi-k2.7-code": dict({"name": "Kimi K2.7 Code", "limit": {"context": 256000, "output": 16000},
                                "cost": {"input": 6.5, "output": 27.0, "cache_read": 1.3}}, **mm_attach("image")),
        # ---- multimodal: text + image + video ----
        "seed-2.1-pro": dict({"name": "Seed 2.1 Pro", "limit": {"context": 262144, "output": 131072},
                              "cost": {"input": 6.0, "output": 30.0, "cache_read": 1.2}}, **mm_attach("image", "video")),
        "seed-2.1-turbo": dict({"name": "Seed 2.1 Turbo", "limit": {"context": 262144, "output": 131072},
                                "cost": {"input": 3.0, "output": 15.0, "cache_read": 0.6}}, **mm_attach("image", "video")),
        "qwen3.8-max": dict({"name": "Qwen 3.8 Max", "limit": {"context": 1000000, "output": 131072},
                             "cost": {"input": 12.0, "output": 36.0, "cache_read": 1.5}}, **mm_attach("image")),
        # ---- text only ----
        "deepseek-v4-flash": dict({"name": "DeepSeek V4 Flash", "limit": {"context": 1000000, "output": 384000},
                                   "cost": {"input": 1.0, "output": 2.0, "cache_read": 0.2}}, **mm_text()),
        "deepseek-v4-pro": dict({"name": "DeepSeek V4 Pro", "limit": {"context": 1000000, "output": 384000},
                                 "cost": {"input": 12.0, "output": 24.0, "cache_read": 1.0}}, **mm_text()),
        "deepseek-v4-flash-0731": dict({"name": "DeepSeek V4 Flash 0731", "limit": {"context": 1000000, "output": 384000},
                                        "cost": {"input": 3.0, "output": 9.0, "cache_read": 0.1}}, **mm_text()),
        "deepseek-v4-pro-0813": dict({"name": "DeepSeek V4 Pro 0813", "limit": {"context": 1000000, "output": 384000},
                                      "cost": {"input": 9.0, "output": 27.0, "cache_read": 0.3}}, **mm_text()),
        "glm-5": dict({"name": "GLM-5", "limit": {"context": 1000000, "output": 128000},
                       "cost": {"input": 6.0, "output": 22.0, "cache_read": 1.5}}, **mm_text()),
        "glm-5.1": dict({"name": "GLM-5.1", "limit": {"context": 200000, "output": 128000},
                         "cost": {"input": 8.0, "output": 28.0, "cache_read": 2.0}}, **mm_text()),
        "glm-5.2": dict({"name": "GLM-5.2", "limit": {"context": 1000000, "output": 128000},
                         "cost": {"input": 8.0, "output": 28.0, "cache_read": 2.0}}, **mm_text()),
        "mimo-v2.5-pro": dict({"name": "MiMo 2.5 Pro", "limit": {"context": 256000, "output": 256000},
                               "cost": {"input": 3.0, "output": 6.0}}, **mm_text()),
        "minimax-m2.5": dict({"name": "MiniMax M2.5", "limit": {"context": 200000, "output": 200000},
                              "cost": {"input": 2.1, "output": 8.4}}, **mm_text()),
        "minimax-m2.7": dict({"name": "MiniMax M2.7", "limit": {"context": 200000, "output": 192000},
                              "cost": {"input": 2.1, "output": 8.4}}, **mm_text()),
        "qwen3.7-max": dict({"name": "Qwen 3.7 Max", "limit": {"context": 1000000, "output": 131072},
                             "cost": {"input": 12.0, "output": 36.0, "cache_read": 2.4}}, **mm_text()),
    },
}

# NVIDIA NIM hosted API (https://integrate.api.nvidia.com/v1) — chat models
# the key can access via /v1/models (queried 2026-08-20). Multimodal models
# flagged accordingly; display names use English + (英伟达).
def _nv_model(name, context, output=131072, modes=("image",), reasoning=False):
    m = {"name": name + NVIDIA_SUFFIX, "limit": {"context": context, "output": output},
         "reasoning": reasoning, "tool_call": True}
    if modes:
        m.update(mm_attach(*modes))
    else:
        m.update(mm_text())
    return m


NVIDIA_PROVIDER = {
    "npm": "@ai-sdk/openai-compatible",
    "name": "NVIDIA (英伟达)",
    "options": {"baseURL": "https://integrate.api.nvidia.com/v1"},
    "env": ["NVIDIA_API_KEY"],
    "models": {
        # ---- multimodal (vision) ----
        "minimaxai/minimax-m3": _nv_model("MiniMax M3", 1000000, 8192, ("image", "video"), True),
        "moonshotai/kimi-k3": _nv_model("Kimi K3", 1048576, 32768, ("image", "video"), True),
        "moonshotai/kimi-k2.6": _nv_model("Kimi K2.6", 256000, 16384, ("image", "video"), True),
        "meta/llama-3.2-11b-vision-instruct": _nv_model("Llama 3.2 11B Vision", 128000, 8192, ("image",)),
        "meta/llama-3.2-90b-vision-instruct": _nv_model("Llama 3.2 90B Vision", 128000, 8192, ("image",)),
        "nvidia/llama-3.1-nemotron-nano-vl-8b-v1": _nv_model("Nemotron Nano VL 8B", 128000, 4096, ("image",)),
        "nvidia/nemotron-nano-12b-v2-vl": _nv_model("Nemotron Nano 12B VL v2", 128000, 8192, ("image", "video")),
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning": _nv_model("Nemotron 3 Nano Omni 30B", 131072, 16384, ("image", "video"), True),
        "microsoft/phi-3-vision-128k-instruct": _nv_model("Phi-3 Vision 128K", 128000, 8192, ("image",)),
        "google/gemma-3-4b-it": _nv_model("Gemma 3 4B IT", 131072, 8192, ("image",)),
        "google/gemma-3-12b-it": _nv_model("Gemma 3 12B IT", 131072, 8192, ("image",)),
        "google/gemma-4-31b-it": _nv_model("Gemma 4 31B IT", 262144, 16384, ("image",)),
        "stepfun-ai/step-3.7-flash": _nv_model("StepFun Step 3.7 Flash", 262144, 8192, ("image",), True),
        "thinkingmachines/inkling": _nv_model("Inkling", 131072, 16384, ("image",), True),
        "meta/muse-glimmer-30b": _nv_model("Muse Glimmer 30B", 131072, 16384, ("image",), True),
        "nvidia/vila": _nv_model("VILA", 32768, 4096, ("image",)),
        # ---- text only ----
        "deepseek-ai/deepseek-v4-flash-0731": _nv_model("DeepSeek V4 Flash 0731", 1000000, 16384, (), True),
        "z-ai/glm-5.2": _nv_model("GLM-5.2", 1000000, 16384, (), True),
        "meta/llama-3.1-8b-instruct": _nv_model("Llama 3.1 8B Instruct", 131072, 8192, ()),
        "meta/llama-3.3-70b-instruct": _nv_model("Llama 3.3 70B Instruct", 131072, 8192, ()),
        "nvidia/llama-3.1-nemotron-70b-instruct": _nv_model("Nemotron 70B Instruct", 131072, 8192, ()),
        "nvidia/llama-3.1-nemotron-ultra-253b-v1": _nv_model("Nemotron Ultra 253B", 131072, 8192, ()),
        "nvidia/llama-3.3-nemotron-super-49b-v1": _nv_model("Nemotron Super 49B", 131072, 8192, ()),
        "nvidia/llama-3.3-nemotron-super-49b-v1.5": _nv_model("Nemotron Super 49B v1.5", 131072, 8192, ()),
        "nvidia/nemotron-3-super-120b-a12b": _nv_model("Nemotron 3 Super 120B", 131072, 16384, ()),
        "nvidia/nemotron-3-ultra-550b-a55b": _nv_model("Nemotron 3 Ultra 550B", 131072, 16384, ()),
        "nvidia/nemotron-3.5-lightning-30b-a3b": _nv_model("Nemotron 3.5 Lightning 30B", 131072, 16384, ()),
        "nvidia/nemotron-nano-3-30b-a3b": _nv_model("Nemotron Nano 3 30B", 131072, 8192, ()),
        "nvidia/nemotron-mini-4b-instruct": _nv_model("Nemotron Mini 4B", 131072, 8192, ()),
        "mistralai/mistral-large": _nv_model("Mistral Large", 131072, 8192, ()),
        "mistralai/mistral-large-2-instruct": _nv_model("Mistral Large 2", 131072, 8192, ()),
        "mistralai/mistral-nemotron": _nv_model("Mistral Nemotron", 131072, 8192, ()),
        "mistralai/mixtral-8x22b-v0.1": _nv_model("Mixtral 8x22B", 65536, 8192, ()),
        "openai/gpt-oss-20b": _nv_model("GPT-OSS 20B", 131072, 16384, (), True),
        "openai/gpt-oss-120b": _nv_model("GPT-OSS 120B", 131072, 16384, (), True),
        "google/codegemma-7b": _nv_model("CodeGemma 7B", 16384, 4096, ()),
        "zyphra/zamba2-7b-instruct": _nv_model("Zamba2 7B Instruct", 131072, 8192, ()),
    },
}

PROVIDERS = {
    "tokenrhythm": TOKENRHYTHM_PROVIDER,
    "nvidia": NVIDIA_PROVIDER,
}


# ---------------------------------------------------------------------------
# Small JSONC parser (strips // and /* */ comments, tolerates trailing commas)
# ---------------------------------------------------------------------------

def strip_jsonc(text):
    out = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\":
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _remove_trailing_commas(text):
    return re.sub(r",\s*([}\]])", r"\1", text)


def load_config_file(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        text = f.read()
    try:
        return json.loads(strip_jsonc(text))
    except Exception:
        return json.loads(_remove_trailing_commas(strip_jsonc(text)))


# ---------------------------------------------------------------------------
# Config discovery
# ---------------------------------------------------------------------------

def global_config_dir():
    if os.name == "nt":
        base = os.environ.get("OPENCODE_CONFIG_HOME") or os.path.join(
            os.environ.get("USERPROFILE") or os.path.expanduser("~"), ".config", "opencode"
        )
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
            os.path.expanduser("~"), ".config", "opencode"
        )
    return base


def find_config_path(project=False):
    if os.environ.get("OPENCODE_CONFIG"):
        return os.environ["OPENCODE_CONFIG"]
    if project:
        here = os.getcwd()
        for name in ("opencode.json", "opencode.jsonc"):
            p = os.path.join(here, name)
            if os.path.isfile(p):
                return p
        return os.path.join(here, "opencode.json")
    base = global_config_dir()
    json_path = os.path.join(base, "opencode.json")
    jsonc_path = os.path.join(base, "opencode.jsonc")
    if os.path.isfile(json_path):
        return json_path
    if os.path.isfile(jsonc_path):
        return jsonc_path
    return json_path


def plugins_dir():
    return os.path.join(global_config_dir(), "plugins")


# ---------------------------------------------------------------------------
# Install / uninstall
# ---------------------------------------------------------------------------

def install_config(config_path, dry_run):
    if os.path.isfile(config_path):
        config = load_config_file(config_path)
    else:
        config = {"$schema": "https://opencode.ai/config.json"}
    config.setdefault("provider", {})

    actions = []
    for pid, provider in PROVIDERS.items():
        if pid in config["provider"]:
            actions.append("update '{}'".format(pid))
        else:
            actions.append("add '{}'".format(pid))
        config["provider"][pid] = provider

    if dry_run:
        print("[dry-run] would {} provider(s) in {}".format(" / ".join(actions), config_path))
        return

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("[ok] {} provider(s) in {}".format(" / ".join(actions), config_path))


def uninstall_config(config_path, dry_run):
    if not os.path.isfile(config_path):
        print("[skip] no config file: {}".format(config_path))
        return
    config = load_config_file(config_path)
    provider = config.get("provider", {})
    removed = [pid for pid in PROVIDERS if pid in provider]
    for pid in removed:
        del provider[pid]
    if not removed:
        print("[skip] none of {} present in {}".format(", ".join(PROVIDERS), config_path))
        return
    if dry_run:
        print("[dry-run] would remove {} from {}".format(", ".join(removed), config_path))
        return
    with open(config_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("[ok] removed {} from {}".format(", ".join(removed), config_path))


def _models_to_js(models, provider_id):
    """Convert a provider models dict into JS `{ id, providerID, name, api,
    capabilities, cost, limit, status, options, headers, release_date }`."""
    js = []
    for mid, meta in models.items():
        caps_in = {"text": True}
        modes = (meta.get("modalities") or {}).get("input") or ["text"]
        for mode in ("audio", "image", "video", "pdf"):
            caps_in[mode] = mode in modes
        caps_out = {"text": True, "audio": False, "image": False, "video": False, "pdf": False}
        att = bool(meta.get("attachment"))
        reasoning = bool(meta.get("reasoning"))
        limit = meta.get("limit") or {}
        cost = meta.get("cost") or {}
        js.append(json.dumps({
            "id": mid,
            "providerID": provider_id,
            "name": meta.get("name") or mid,
            "api": {"id": "openai", "url": "https://" + ("integrate.api.nvidia.com" if provider_id == "nvidia" else "tokenrhythm.studio") + "/v1", "npm": "@ai-sdk/openai-compatible"},
            "capabilities": {
                "temperature": True, "reasoning": reasoning, "attachment": att,
                "toolcall": True, "input": caps_in, "output": caps_out, "interleaved": False,
            },
            "cost": {"input": cost.get("input", 0), "output": cost.get("output", 0),
                     "cache": {"read": cost.get("cache_read", 0), "write": cost.get("cache_write", 0)}},
            "limit": {"context": limit.get("context", 131072), "output": limit.get("output", 8192)},
            "status": "active", "options": {}, "headers": {}, "release_date": "2026-08-20",
        }, ensure_ascii=False))
    return "{\n      " + ",\n      ".join(js) + "\n    }"


def build_plugin_js():
    parts = []
    parts.append("// TokenRhythm (基元律动) + NVIDIA (英伟达) provider presets for opencode")
    parts.append("// Installed by the TokenRhythm preset installer.")
    parts.append("// Registers models (multimodal models flagged) so opencode knows they")
    parts.append("// support image/video attachments even if the config is regenerated.")
    for pid in ("tokenrhythm", "nvidia"):
        name = "TokenRhythmPreset" if pid == "tokenrhythm" else "NvidiaPreset"
        parts.append("")
        parts.append("const {}Models = {}".format(name, _models_to_js(PROVIDERS[pid]["models"], pid)))
        parts.append("")
        parts.append("export const {} = async () => ({{".format(name))
        parts.append("  provider: {")
        parts.append('    id: "{}",'.format(pid))
        parts.append("    models: async () => {}Models,".format(name))
        parts.append("  },")
        parts.append("})")
    return "\n".join(parts) + "\n"


def install_plugin(dry_run):
    target_dir = plugins_dir()
    target = os.path.join(target_dir, PLUGIN_NAME)
    if dry_run:
        print("[dry-run] would write plugin to {}".format(target))
        return
    os.makedirs(target_dir, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write(build_plugin_js())
    print("[ok] plugin installed at {}".format(target))


def main():
    parser = argparse.ArgumentParser(
        description="Install the TokenRhythm + NVIDIA provider presets into opencode"
    )
    parser.add_argument("--plugin", action="store_true", help="only install the plugin file")
    parser.add_argument("--dry-run", action="store_true", help="show actions without writing")
    parser.add_argument("--uninstall", action="store_true", help="remove the tokenrhythm + nvidia providers")
    parser.add_argument("--project", action="store_true", help="use ./opencode.json instead of the global config")
    args = parser.parse_args()

    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(errors="replace")
            except Exception:
                pass

    if args.plugin:
        install_plugin(args.dry_run)
        return

    config_path = find_config_path(args.project)

    if args.uninstall:
        uninstall_config(config_path, args.dry_run)
        return

    install_config(config_path, args.dry_run)
    install_plugin(args.dry_run)

    if not args.dry_run:
        print()
        print("预设已安装 [OK]  TokenRhythm 与 NVIDIA(英伟达) provider 已加入 opencode。")
        print("下一步：")
        print("  1) 设置环境变量：TOKENRHYTHM_API_KEY（tokenrhythm.studio）与/或 NVIDIA_API_KEY（build.nvidia.com）")
        print("  2) 重启 opencode，在对话中运行 /models 即可看到全部模型")
        print("  3) 多模态（视觉）模型已标记，可直接发送图片（如 Kimi / MiniMax-M3 / Seed / Qwen 等）")


if __name__ == "__main__":
    main()