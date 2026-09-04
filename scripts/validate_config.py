#!/usr/bin/env python3
"""
Validate the TokenRhythm provider preset and its MCP server.

Checks:
  1. opencode.jsonc is valid JSONC (comments + trailing commas tolerated).
  2. Expected providers (tokenrhythm, nvidia) exist with an @ai-sdk/openai-compatible
     npm package and a valid HTTPS baseURL.
  3. Model IDs are unique per provider; context/output limits are sane
     (non-negative integers; 0 = "not specified", used by qwen-image-2.0).
  4. If a model declares reasoning variants, each variant sets reasoningEffort.
  5. No hardcoded secrets: MCP environment values must be empty or reference
     environment variables only, and no API-key-like strings appear anywhere
     in the config.
  6. mcp/tokenrhythm_image_mcp.py compiles and its API key comes from an env var.

Usage:
  python scripts/validate_config.py
Exit code 0 on success, 1 on any failure.
"""

import json
import os
import py_compile
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "opencode.jsonc")
MCP_PATH = os.path.join(ROOT, "mcp", "tokenrhythm_image_mcp.py")

EXPECTED_PROVIDERS = {
    "tokenrhythm": "https://tokenrhythm.studio/v1",
    "nvidia": "https://integrate.api.nvidia.com/v1",
}

# Loose API-key heuristics: sk-* prefixes, long hex/base64 tokens.
SECRET_PATTERNS = [
    re.compile(r"sk[-_][A-Za-z0-9]{16,}"),
    re.compile(r"[A-Za-z0-9]{40,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{16,}"),
]

errors = []
warnings = []


def strip_jsonc_comments(text):
    """Remove // and /* */ comments, keeping string contents intact."""
    out = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n:
            nxt = text[i + 1]
            if nxt == "/":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            if nxt == "*":
                i += 2
                while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i = min(i + 2, n)
                continue
        out.append(c)
        i += 1
    return "".join(out)


def strip_trailing_commas(text):
    """Remove commas directly before } or ] (JSONC convenience), skipping
    whitespace/newlines between the comma and the closing bracket."""
    out = []
    in_string = False
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        if c == ",":
            j = i + 1
            while j < n and text[j] in " \t\r\n":
                j += 1
            if j < n and text[j] in "}]":
                i += 1  # drop the comma
                continue
        out.append(c)
        i += 1
    return "".join(out)


def load_jsonc(path):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    for attempt in (raw, strip_jsonc_comments(raw), strip_trailing_commas(strip_jsonc_comments(raw))):
        try:
            return json.loads(attempt)
        except json.JSONDecodeError:
            continue
    # Re-raise the most permissive attempt's error for a useful message
    return json.loads(strip_trailing_commas(strip_jsonc_comments(raw)))


def scan_secrets(obj, where="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            scan_secrets(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan_secrets(v, f"{where}[{i}]")
    elif isinstance(obj, str):
        for pat in SECRET_PATTERNS:
            if pat.search(obj):
                # An empty-string placeholder or a pure env-var reference is fine.
                if not obj or obj.startswith("${") or obj.isupper() and "_" in obj:
                    continue
                errors.append(f"possible hardcoded secret at {where}: {obj[:12]}...")


def main():
    print("==> validating", os.path.relpath(CONFIG_PATH, ROOT))
    config = load_jsonc(CONFIG_PATH)
    print("    JSONC parses OK")

    if "$schema" not in config:
        warnings.append("missing $schema")

    providers = config.get("provider", {})
    if len(providers) < len(EXPECTED_PROVIDERS):
        errors.append(f"expected providers {sorted(EXPECTED_PROVIDERS)}, found {sorted(providers)}")

    for name, expected_url in EXPECTED_PROVIDERS.items():
        prov = providers.get(name)
        if prov is None:
            errors.append(f"provider '{name}' missing")
            continue
        if prov.get("npm") != "@ai-sdk/openai-compatible":
            errors.append(f"provider '{name}': npm should be @ai-sdk/openai-compatible, got {prov.get('npm')!r}")
        base = (prov.get("options") or {}).get("baseURL")
        if base != expected_url:
            errors.append(f"provider '{name}': baseURL {base!r} != expected {expected_url!r}")

        models = prov.get("models") or {}
        if not models:
            errors.append(f"provider '{name}': no models")
        for mid, m in models.items():
            limits = m.get("limit") or {}
            for key in ("context", "output"):
                val = limits.get(key)
                if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                    errors.append(f"provider '{name}' model '{mid}': limit.{key} must be a non-negative int, got {val!r}")
            variants = m.get("variants") or {}
            for vname, vopts in variants.items():
                if not isinstance(vopts, dict) or "reasoningEffort" not in vopts:
                    errors.append(f"provider '{name}' model '{mid}' variant '{vname}': missing reasoningEffort")
            modalities = m.get("modalities") or {}
            for side in ("input", "output"):
                if side in modalities and not isinstance(modalities[side], list):
                    errors.append(f"provider '{name}' model '{mid}': modalities.{side} must be a list")

    mcp = config.get("mcp") or {}
    for sname, spec in mcp.items():
        env = spec.get("environment") or {}
        for k, v in env.items():
            # MCP environment values must stay empty or reference env vars —
            # never hardcode an API key in the committed config.
            if isinstance(v, str) and v and not v.startswith("${"):
                errors.append(f"mcp '{sname}'.environment.{k}: value must be empty or an env-var reference like ${{VAR}}")

    scan_secrets(config)

    print("==> validating", os.path.relpath(MCP_PATH, ROOT))
    if not os.path.isfile(MCP_PATH):
        errors.append(f"MCP script not found: {MCP_PATH}")
    else:
        py_compile.compile(MCP_PATH, doraise=True)
        with open(MCP_PATH, "r", encoding="utf-8") as f:
            src = f.read()
        if "os.environ.get(\"TOKENRHYTHM_API_KEY\"" not in src:
            errors.append("MCP script must read TOKENRHYTHM_API_KEY from the environment (no hardcoded keys)")

    for w in warnings:
        print("    WARN:", w)
    for e in errors:
        print("    ERROR:", e)
    if errors:
        print("FAILED with %d error(s)" % len(errors))
        sys.exit(1)
    print("OK: config and MCP server look good")


if __name__ == "__main__":
    main()
