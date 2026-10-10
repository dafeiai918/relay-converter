#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""relay-converter · 一份配置，转成所有 AI 客户端的格式
输入 base_url + api_key，输出 16 种客户端可直接粘贴的配置 / 文件 / 代码
零依赖单文件
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

__version__ = "1.0.0"

REMOTE_URL = "https://raw.githubusercontent.com/dafeiai918/oneclickrelay-remote/main/remote.json"
FALLBACK_RECOMMEND = {"name": "好同根", "url": "https://haotogen.com/"}


class C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"; CYAN = "\033[36m"; GRAY = "\033[90m"


_COLOR = True


def _c(code: str, text: str) -> str:
    return f"{code}{text}{C.RESET}" if _COLOR else text


def enable_ansi() -> None:
    global _COLOR
    if os.name == "nt":
        os.system("")
    _COLOR = sys.stdout.isatty() or os.name == "nt"
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def split_base(url: str) -> tuple[str, str]:
    """返回 (不带/v1的根地址, 带/v1的完整地址)"""
    root = url.strip().rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3].rstrip("/")
    return root, root + "/v1"


# ---------------- 模板 ----------------
# 每个 render(ctx) 返回 (文件名或 None, 文本)

def t_cherry(ctx) -> tuple[str | None, str]:
    return None, f"""【Cherry Studio】
1. 设置 → 模型服务 → 添加提供商 → 类型选 OpenAI
2. 填写：
   API 地址   {ctx['root']}        ← 注意：不要带 /v1
   API 密钥   {ctx['key']}
3. 添加模型 → 填模型 ID：{ctx['model']}
4. 点「检查」通过后保存

一键写入：用 OneClickRelay（github.com/dafeiai918/oneclickrelay）自动完成上述步骤。"""


def t_nextchat(ctx) -> tuple[str | None, str]:
    return None, f"""【NextChat】
设置 → 自定义接口：
   接口地址   {ctx['full']}
   API Key    {ctx['key']}
   模型名     {ctx['model']}
（其他留空，保存后新开会话）"""


def t_chatbox(ctx) -> tuple[str | None, str]:
    return None, f"""【Chatbox】
设置 → 模型 → 添加自定义提供方：
   API 域名   {ctx['root']}
   API 路径   /v1/chat/completions
   API 密钥   {ctx['key']}
   模型名     {ctx['model']}"""


def t_openwebui(ctx) -> tuple[str | None, str]:
    return ".env", f"""OPENAI_API_BASE_URL={ctx['full']}
OPENAI_API_KEY={ctx['key']}
# Open WebUI：管理员设置 → 连接 → OpenAI API 填写同样内容"""


def t_lobechat(ctx) -> tuple[str | None, str]:
    return ".env.lobechat", f"""OPENAI_API_KEY={ctx['key']}
OPENAI_PROXY_URL={ctx['full']}
# LobeChat：不填 OPENAI_PROXY_URL 时默认走官方，务必设置"""


def t_librechat(ctx) -> tuple[str | None, str]:
    payload = {
        "version": 1,
        "endpoints": {"custom": [{
            "name": "中转站",
            "apiKey": ctx["key"],
            "baseURL": ctx["full"],
            "models": {"default": [ctx["model"]], "fetch": True},
            "titleConvo": True,
        }]},
    }
    return "librechat.yaml", "# 把下面内容合并进 librechat.yaml\n" + json.dumps(
        payload, ensure_ascii=False, indent=2)


def t_continue(ctx) -> tuple[str | None, str]:
    payload = {"models": [{
        "title": "中转站",
        "provider": "openai",
        "model": ctx["model"],
        "apiBase": ctx["full"],
        "apiKey": ctx["key"],
    }]}
    return "continue-config.json", ("# 合并进 ~/.continue/config.json（或 config.yaml）\n"
                                    + json.dumps(payload, ensure_ascii=False, indent=2))


def t_cline(ctx) -> tuple[str | None, str]:
    payload = {
        "cline.apiProvider": "openai",
        "cline.openAiBaseUrl": ctx["full"],
        "cline.openAiApiKey": ctx["key"],
        "cline.openAiModelId": ctx["model"],
    }
    return "vscode-settings.json", ("# 合并进 VS Code settings.json\n"
                                    + json.dumps(payload, ensure_ascii=False, indent=2))


def t_aider(ctx) -> tuple[str | None, str]:
    return ".env.aider", f"""OPENAI_API_BASE={ctx['full']}
OPENAI_API_KEY={ctx['key']}
# 用法：aider --model openai/{ctx['model']}"""


def t_codex(ctx) -> tuple[str | None, str]:
    return "codex-config.toml", f"""# 合并进 ~/.codex/config.toml（不要整体覆盖，会丢掉 projects/mcp_servers）
model = "{ctx['model']}"
model_provider = "relay"

[model_providers.relay]
name = "Relay"
base_url = "{ctx['full']}"
wire_api = "chat"
env_key = "RELAY_API_KEY"
# 同时设置环境变量 RELAY_API_KEY={ctx['key']}"""


def t_opencode(ctx) -> tuple[str | None, str]:
    payload = {
        "provider": {
            "relay": {
                "npm": "@ai-sdk/openai-compatible",
                "options": {"baseURL": ctx["full"], "apiKey": ctx["key"]},
                "models": {ctx["model"]: {}},
            }
        }
    }
    return "opencode.json", json.dumps(payload, ensure_ascii=False, indent=2)


def t_jan(ctx) -> tuple[str | None, str]:
    return None, f"""【Jan】
设置 → 模型 → 添加提供商 → OpenAI 兼容：
   Base URL   {ctx['full']}
   API Key    {ctx['key']}
   模型 ID    {ctx['model']}"""


def t_anythingllm(ctx) -> tuple[str | None, str]:
    return None, f"""【AnythingLLM】
设置 → LLM 首选项 → 提供方选 Generic OpenAI：
   Base URL   {ctx['full']}
   API Key    {ctx['key']}
   Chat Model {ctx['model']}"""


def t_sillytavern(ctx) -> tuple[str | None, str]:
    return None, f"""【SillyTavern】
连接设置 → API 选 Chat Completion → 来源选 Custom (OpenAI-compatible)：
   Custom URL   {ctx['full']}
   API Key      {ctx['key']}
   模型名        {ctx['model']}"""


def t_dify(ctx) -> tuple[str | None, str]:
    return None, f"""【Dify】
设置 → 模型供应商 → OpenAI-API-compatible → 添加模型：
   API Base URL   {ctx['full']}
   API Key        {ctx['key']}
   模型名称        {ctx['model']}
注：Dify 许可证禁止移除其前端 LOGO。"""


def t_env(ctx) -> tuple[str | None, str]:
    return ".env", f"""OPENAI_BASE_URL={ctx['full']}
OPENAI_API_BASE={ctx['full']}
OPENAI_API_KEY={ctx['key']}
OPENAI_MODEL={ctx['model']}"""


def t_curl(ctx) -> tuple[str | None, str]:
    return "test.sh", f"""curl {ctx['full']}/chat/completions \\
  -H "Authorization: Bearer {ctx['key']}" \\
  -H "Content-Type: application/json" \\
  -d '{{"model": "{ctx['model']}", "messages": [{{"role": "user", "content": "你好"}}]}}'"""


def t_python(ctx) -> tuple[str | None, str]:
    return "test.py", f'''from openai import OpenAI

client = OpenAI(base_url="{ctx['full']}", api_key="{ctx['key']}")
resp = client.chat.completions.create(
    model="{ctx['model']}",
    messages=[{{"role": "user", "content": "你好"}}],
)
print(resp.choices[0].message.content)'''


def t_node(ctx) -> tuple[str | None, str]:
    return "test.mjs", f'''import OpenAI from "openai";

const client = new OpenAI({{ baseURL: "{ctx['full']}", apiKey: "{ctx['key']}" }});
const resp = await client.chat.completions.create({{
  model: "{ctx['model']}",
  messages: [{{ role: "user", content: "你好" }}],
}});
console.log(resp.choices[0].message.content);'''


TARGETS = [
    ("cherry",      "Cherry Studio",     "桌面客户端", "内置",  t_cherry),
    ("nextchat",    "NextChat",          "桌面客户端", "内置",  t_nextchat),
    ("chatbox",     "Chatbox",           "桌面客户端", "内置",  t_chatbox),
    ("jan",         "Jan",               "桌面客户端", "内置",  t_jan),
    ("openwebui",   "Open WebUI",        "自部署",     "内置",  t_openwebui),
    ("lobechat",    "LobeChat",          "自部署",     "内置",  t_lobechat),
    ("librechat",   "LibreChat",         "自部署",     "内置",  t_librechat),
    ("dify",        "Dify",              "自部署",     "内置",  t_dify),
    ("anythingllm", "AnythingLLM",       "桌面客户端", "内置",  t_anythingllm),
    ("sillytavern", "SillyTavern",       "桌面客户端", "内置",  t_sillytavern),
    ("continue",    "Continue (VSCode)", "编程插件",   "内置",  t_continue),
    ("cline",       "Cline (VSCode)",    "编程插件",   "内置",  t_cline),
    ("aider",       "Aider",             "命令行",     "内置",  t_aider),
    ("codex",       "Codex CLI",         "命令行",     "内置",  t_codex),
    ("opencode",    "OpenCode",          "命令行",     "内置",  t_opencode),
    ("env",         "通用 .env",         "通用",       "内置",  t_env),
    ("curl",        "cURL 测试",         "通用",       "内置",  t_curl),
    ("python",      "Python SDK",        "通用",       "内置",  t_python),
    ("node",        "Node.js SDK",       "通用",       "内置",  t_node),
]


# ---------------- 推荐位 ----------------

def fetch_recommend(timeout: float = 5.0) -> dict | None:
    import urllib.request
    try:
        req = urllib.request.Request(REMOTE_URL, headers={"User-Agent": f"relay-converter/{__version__}"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        rec = data.get("recommend")
        if isinstance(rec, dict) and isinstance(rec.get("url"), str):
            return rec
    except Exception:
        pass
    return FALLBACK_RECOMMEND


# ---------------- 主流程 ----------------

def build_all(ctx) -> list[tuple[str, str]]:
    out = []
    for tid, name, cat, _, fn in TARGETS:
        try:
            _, text = fn(ctx)
        except Exception as exc:
            text = f"(模板错误: {type(exc).__name__})"
        out.append((tid, text))
    return out


def main(argv: list[str] | None = None) -> int:
    enable_ansi()
    parser = argparse.ArgumentParser(
        prog="relay-converter", description="一份配置转成所有 AI 客户端格式（零依赖）")
    parser.add_argument("-u", "--base-url", help="中转站地址，如 https://api.example.com/v1")
    parser.add_argument("-k", "--api-key", help="API 密钥（或环境变量 RELAY_API_KEY）")
    parser.add_argument("-m", "--model", default="gpt-4o-mini", help="默认模型名")
    parser.add_argument("-t", "--target", action="append", default=[],
                        help="只输出指定目标，可多次，如 -t cherry -t nextchat")
    parser.add_argument("--out", help="同时写出文件到目录")
    parser.add_argument("--list", action="store_true", help="列出支持的目标")
    parser.add_argument("-V", "--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    if args.list:
        for tid, name, cat, kind, _ in TARGETS:
            print(f"  {tid:<14} {name:<18} {cat}")
        return 0

    base = args.base_url or os.environ.get("RELAY_BASE_URL", "")
    key = args.api_key or os.environ.get("RELAY_API_KEY", "")
    if not base:
        parser.error("缺少站点地址：用 -u 或环境变量 RELAY_BASE_URL")
    if not key:
        parser.error("缺少密钥：用 -k 或环境变量 RELAY_API_KEY")

    root, full = split_base(base)
    ctx = {"root": root, "full": full, "key": key, "model": args.model}

    picked = set(args.target) or {t[0] for t in TARGETS}
    unknown = picked - {t[0] for t in TARGETS}
    if unknown:
        parser.error(f"未知目标: {', '.join(sorted(unknown))}（用 --list 查看）")

    out_dir = Path(args.out) if args.out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    width = 60
    print()
    print(_c(C.GRAY, "═" * width))
    print(_c(C.BOLD, f"  relay-converter · 配置转换") + _c(C.GRAY, f"  v{__version__}"))
    print(_c(C.GRAY, "═" * width))
    print(f"  地址(带/v1)  {full}")
    print(f"  地址(不带)   {root}")
    print(f"  模型         {args.model}")
    print(_c(C.GRAY, "═" * width))

    for tid, name, cat, _, fn in TARGETS:
        if tid not in picked:
            continue
        fname, text = fn(ctx)
        print()
        print(_c(C.CYAN + C.BOLD, f"── {name} " + "─" * max(0, width - len(name) - 5)))
        print(text)
        if out_dir and fname:
            safe = f"{tid}-{fname}"
            (out_dir / safe).write_text(text, encoding="utf-8")
    if out_dir:
        print()
        print(_c(C.GRAY, f"已写出配置到 {out_dir}"))

    rec = fetch_recommend()
    print()
    print(_c(C.GRAY, "═" * width))
    if rec:
        print(f"  {_c(C.CYAN, '推荐中转站')}  {rec.get('name', '')}  {rec.get('url', '')}")
        print(_c(C.GRAY, "═" * width))
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
