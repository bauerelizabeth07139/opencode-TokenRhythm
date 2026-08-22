"""
MCP Server: TokenRhythm Image Generation
Uses TokenRhythm API (qwen-image-2.0) for image generation.
Protocol: MCP stdio JSON-RPC
"""
import json
import sys
import os
import urllib.request
import urllib.error
import base64
import tempfile
import time
from pathlib import Path

API_BASE = "https://tokenrhythm.studio/v1"
API_KEY = "sk_tr_RaQxED919wgOkWnWW9ALNx8B2mCdLkxcrM2Pici5LGs"
MODEL_ID = "qwen-image-2.0"

def log(msg):
    with open(os.path.join(tempfile.gettempdir(), "tokenrhythm-mcp.log"), "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_response(response):
    data = json.dumps(response, ensure_ascii=False)
    sys.stdout.write(data + "\n")
    sys.stdout.flush()

def generate_image(prompt, size="1024x1024", n=1):
    url = f"{API_BASE}/images/generations"
    payload = json.dumps({
        "model": MODEL_ID,
        "prompt": prompt,
        "n": n,
        "size": size,
        "response_format": "b64_json"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    })

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            images = []
            save_dir = Path.home() / ".config" / "opencode" / "generated_images"
            save_dir.mkdir(parents=True, exist_ok=True)

            for i, img_data in enumerate(result.get("data", [])):
                if "b64_json" in img_data:
                    img_bytes = base64.b64decode(img_data["b64_json"])
                    filename = f"tokenrhythm_{int(time.time())}_{i}.png"
                    filepath = save_dir / filename
                    filepath.write_bytes(img_bytes)
                    images.append(str(filepath))

            return {
                "success": True,
                "images": images,
                "count": len(images),
                "model": MODEL_ID,
                "prompt": prompt
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return {"success": False, "error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def handle_request(request):
    method = request.get("method", "")
    req_id = request.get("id", 0)

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "tokenrhythm-image-gen",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "generate_image",
                        "description": "使用基元律动(TokenRhythm) qwen-image-2.0 模型生成图片。输入中文或英文提示词描述你想要的图片。",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "图片提示词/描述，描述你想要生成的图片内容"
                                },
                                "size": {
                                    "type": "string",
                                    "enum": ["1024x1024", "1792x1024", "1024x1792"],
                                    "description": "图片尺寸，默认 1024x1024",
                                    "default": "1024x1024"
                                },
                                "n": {
                                    "type": "integer",
                                    "description": "生成图片数量，默认 1",
                                    "default": 1,
                                    "minimum": 1,
                                    "maximum": 4
                                }
                            },
                            "required": ["prompt"]
                        }
                    }
                ]
            }
        }

    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "generate_image":
            prompt = arguments.get("prompt", "")
            size = arguments.get("size", "1024x1024")
            n = arguments.get("n", 1)

            log(f"Generating image: prompt={prompt[:100]}..., size={size}, n={n}")

            result = generate_image(prompt, size, n)

            if result["success"]:
                text = f"成功生成 {result['count']} 张图片:\n"
                for img_path in result["images"]:
                    text += f"- {img_path}\n"
                text += f"\n模型: {result['model']}\n提示词: {result['prompt']}"
            else:
                text = f"图片生成失败: {result['error']}"

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

def main():
    log("MCP server starting...")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                send_response(response)
        except json.JSONDecodeError as e:
            log(f"JSON parse error: {e}")
        except Exception as e:
            log(f"Error: {e}")

if __name__ == "__main__":
    main()