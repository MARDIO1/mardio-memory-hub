# mardio-memory-hub

<a href="README.md"><kbd>简体中文</kbd></a>
<a href="README.en.md"><kbd>English</kbd></a>

自用感觉挺好用。

这是一个轻量的跨设备、跨 Agent 记忆与上下文中转站。它主要解决两类问题：

1. 不同设备、不同 Agent、不同用户的 AI 需要协作，但又不能完全放开权限时，用它做一个很轻的 Agent to Agent 通讯层，传递上下文、审计线索、网络问题排查记录、候选记忆和工作状态。
2. 在新设备上部署 AI 工作环境时，用它当个人 skill hub、rule hub、project context hub。Agent 先读规则和项目上下文，再开始干活。

仓库里只放两类东西：

1. **MemoryHub 服务端**：Python HTTP API、SQLite 索引、Markdown 文件存储、内置 Web 前端。
2. **Agent 调用端**：Python CLI、Node CLI、AstrBot 插件模板、AGENTS/skill 风格的使用描述。

MemoryHub 的核心约定很小：

```bash
memoryhub ls [keyword]          # 不带关键词时只列 SQLite 索引
memoryhub read <path>
memoryhub write <path> <content>
memoryhub delete <path>         # 默认归档；加 --hard 物理删除
```

正文是 Markdown 或 jsonl 文件，SQLite 负责列索引和过滤。人可以像管理文件夹一样看和改，Agent 先用 `ls` 看索引，再按需 `read` 精读正文，避免一上来吞完整文件。

---

## 目录结构

```text
0-memoryhub-rules/     MemoryHub 自己的规则和总说明
1-work-rules/          通用工作规则
2-projects/            项目记忆，按项目继续建子目录
3-tools/               skill、MCP、CLI、插件、工具接入说明
memoryhub/             服务端和 Python CLI
node/                  Node CLI
integrations/astrbot/  AstrBot 插件模板
docs/                  API 和接入说明
```

文件状态写在 Markdown frontmatter 里：

```md
---
status: using
tags: [network, audit]
---

# 当前上下文
```

状态只分三种：

```text
active    长期生效
using     正在使用，通常是当前任务或短期上下文
archived  已归档，默认搜索不显示
```

CLI 里的 `delete` 默认是软删除：把文件标成 `archived`。如果要清理没有价值的瞬时记忆，用 `memoryhub delete <path> --hard`，它会同时删除正文文件和 SQLite 索引。

## 服务端使用

安装依赖后启动服务：

```bash
uv run python -m memoryhub.server
```

不用 uv 也可以：

```bash
python3 -m memoryhub.server
```

常用环境变量：

```env
MEMORYHUB_DATA_DIR=/path/to/memoryhub-data
MEMORYHUB_DB_PATH=/path/to/memoryhub.sqlite
MEMORYHUB_API_HOST=127.0.0.1
MEMORYHUB_API_PORT=8765
MEMORYHUB_API_TOKEN=replace-me
```

API：

```text
GET    /api/ls?q=keyword
GET    /api/read?path=...
POST   /api/write
DELETE /api/delete
GET    /health
```

如果设置了 `MEMORYHUB_API_TOKEN`，HTTP 请求必须带：

```text
Authorization: Bearer <token>
```

Web 前端和 API 是同一个服务：

```text
GET /
GET /app
```

如果要挂到已有后台后面，推荐让原后台负责登录和管理员判断，然后由后台服务端代理 MemoryHub。代理请求 MemoryHub 页面时加：

```text
X-MemoryHub-Trusted-Proxy: 1
```

这样浏览器里不会出现 bearer token 输入框，MemoryHub 可以只监听 `127.0.0.1`。

可选的顶部跳转按钮：

```env
MEMORYHUB_MY_APP_2_URL=http://127.0.0.1:3000/admin/agent-memory
MEMORYHUB_MY_APP_2_LABEL=Open my-app-2
MEMORYHUB_CLOUD_DISK_URL=http://127.0.0.1:3000/disk
MEMORYHUB_CLOUD_DISK_LABEL=Open cloud disk
```

## Agent 端使用

Python CLI：

```bash
uv run memoryhub ls
uv run memoryhub ls audit
uv run memoryhub read 2-projects/example/current.md
uv run memoryhub write 2-projects/example/current.md "# Current\n\nRemember this."
uv run memoryhub delete 2-projects/example/current.md
uv run memoryhub delete 2-projects/example/current.md --hard
```

不用 uv：

```bash
python3 -m memoryhub.cli ls
python3 -m memoryhub.cli ls audit
python3 -m memoryhub.cli read 2-projects/example/current.md
```

Node CLI：

```bash
export MEMORYHUB_BASE_URL=http://127.0.0.1:8765
export MEMORYHUB_API_TOKEN=replace-me

node node/memoryhub-node.mjs ls
node node/memoryhub-node.mjs ls audit
node node/memoryhub-node.mjs read 2-projects/example/current.md
node node/memoryhub-node.mjs write 2-projects/example/current.md "# Current\n\nRemember this."
node node/memoryhub-node.mjs delete 2-projects/example/current.md
```

Agent 的推荐工作流：

1. 开始任务前先跑一次无关键词 `ls`，看 SQLite 索引里的最新文件。
2. 如果索引太多，再用 `ls 关键词` 过滤。
3. 需要完整上下文时 `read` 读取具体文件。
3. 产出新的长期规则、项目上下文、排查记录时 `write`。
4. 短期记忆不用了就 `delete --hard` 清理；只是暂时不想展示时再归档。

## AstrBot 使用

把插件目录复制到 AstrBot 插件目录：

```text
integrations/astrbot/agent_memory_hub
```

再按示例创建运行配置：

```text
integrations/astrbot/config.example.json
```

聊天里可以手动调用：

```text
/mem_ls
/mem_ls keyword
/mem_read 2-projects/example/current.md
/mem_write 2-projects/example/current.md | # Current

这里是要写入的 Markdown 内容
/mem_delete 2-projects/example/current.md
```

AstrBot 的 `/mem_delete` 和 `agent_memory_delete` 是物理删除，适合清理没有长期价值的瞬时记忆。

插件同时暴露给 LLM 的工具名：

```text
agent_memory_ls
agent_memory_read
agent_memory_write
agent_memory_delete
```

也就是说，人在聊天里发具体命令：`/mem_ls`、`/mem_read`、`/mem_write`、`/mem_delete`。如果模型工具调用正常，AstrBot 里的 AI 也可以调用对应的 `agent_memory_ls/read/write/delete` 工具。

## AGENTS/Skill 描述

本仓库的 `AGENTS.md` 是给通用 Agent 看的总入口。Agent 不需要理解一整套复杂数据库，只需要知道：

- 先读 `0-memoryhub-rules/`。
- 工作规则放 `1-work-rules/`。
- 项目上下文放 `2-projects/<project>/`。
- 工具、skill、MCP、插件说明放 `3-tools/`。
- 读写都走 `ls/read/write/delete`。

如果要给某个 Agent 写专用 skill，就把这套规则浓缩成：“先搜索 MemoryHub，再读取相关文件，必要时写回候选记忆；没有价值的瞬时记忆要删除，不要长期污染索引。”

## 和其他项目一起用

最简单的方式是把 MemoryHub 当一个小服务运行，其他项目或 Agent 通过 HTTP API 调它。

如果想把源码固定到另一个仓库里，推荐用 git submodule：

```bash
git submodule add https://github.com/MARDIO1/mardio-memory-hub.git vendor/mardio-memory-hub
```

主项目记录当前使用的 MemoryHub commit，MemoryHub 自己保持独立更新。
