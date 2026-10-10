# relay-converter · 配置转换器

**输入一次 地址+密钥，输出 19 种 AI 客户端可用的配置。**

零依赖 · 单文件 · 中文 · 覆盖桌面端 / 自部署 / 编程插件 / 命令行 / SDK

---

## 为什么需要它

同一个中转站，每个客户端的配置方式都不一样：

| 客户端 | 地址要不要带 `/v1` | 配置在哪 |
|---|---|---|
| Cherry Studio | **不带** | 设置→模型服务 |
| NextChat | 带 | 设置→自定义接口 |
| Chatbox | 域名和路径**分开填** | 设置→模型 |
| Continue | 带 | `~/.continue/config.json` |
| Codex CLI | 带 | `~/.codex/config.toml` |
| … | … | … |

填错一个字段就连不上。这个工具一次全给你。

---

## 用法

```bash
python relay_converter.py -u https://api.example.com/v1 -k sk-xxxx

# 只看某一个客户端
python relay_converter.py -u https://api.example.com/v1 -k sk-xxxx -t cherry

# 一次写出所有配置文件到目录（可直接拷进客户端配置目录）
python relay_converter.py -u https://api.example.com/v1 -k sk-xxxx --out ./configs

# 查看支持列表
python relay_converter.py --list
```

支持环境变量，避免密钥进 shell 历史：

```bash
export RELAY_BASE_URL=https://api.example.com/v1
export RELAY_API_KEY=sk-xxxx
python relay_converter.py --out ./configs
```

---

## 支持的 19 个目标

| 分类 | 目标 |
|---|---|
| 桌面客户端 | Cherry Studio、NextChat、Chatbox、Jan、AnythingLLM、SillyTavern |
| 自部署 | Open WebUI、LobeChat、LibreChat、Dify |
| 编程插件 | Continue (VSCode)、Cline (VSCode) |
| 命令行 | Aider、Codex CLI、OpenCode |
| 通用 | `.env`、cURL、Python SDK、Node.js SDK |

---

## 输出示例

```
$ python relay_converter.py -u https://api.example.com/v1 -k sk-abc -t cherry -t codex

──────────────────────────── Cherry Studio ────────────────────────────
【Cherry Studio】
1. 设置 → 模型服务 → 添加提供商 → 类型选 OpenAI
2. 填写：
   API 地址   https://api.example.com        ← 注意：不要带 /v1
   API 密钥   sk-abc
3. 添加模型 → 填模型 ID：gpt-4o-mini
4. 点「检查」通过后保存

──────────────────────────── Codex CLI ────────────────────────────
# 合并进 ~/.codex/config.toml（不要整体覆盖，会丢掉 projects/mcp_servers）
model = "gpt-4o-mini"
model_provider = "relay"

[model_providers.relay]
name = "Relay"
base_url = "https://api.example.com/v1"
wire_api = "chat"
env_key = "RELAY_API_KEY"
```

---

## 注意

- **Cherry Studio 的 API 地址不要带 `/v1`**（带了会连不上，这是实测结论）
- **Codex CLI 的 config.toml 不要整体覆盖**，否则会丢失你已有的 `projects` / `mcp_servers` 配置
- 各客户端版本迭代较快，字段名如有变化以客户端当前版本为准，欢迎提 Issue
- 生成的配置里含明文密钥，写出文件后注意保管，别提交到公开仓库

---

## 相关项目

| 项目 | 用途 |
|---|---|
| [OneClickRelay](https://github.com/dafeiai918/oneclickrelay) | 一键把中转站写进 60+ 客户端（不用手动粘贴） |
| [relay-bench](https://github.com/dafeiai918/relay-bench) | 测你的中转站行不行 |
| [awesome-relay](https://github.com/dafeiai918/awesome-relay) | 中转站与客户端精选导航 |

---

## License

MIT
