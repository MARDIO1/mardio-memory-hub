# mardio-memory-hub

<a href="README.md"><kbd>English</kbd></a>
<a href="README.zh-CN.md"><kbd>简体中文</kbd></a>

自用感觉挺好用。

这是一个面向 Agent 的 Markdown-first 记忆中心。它刻意保持很小：文件就是记忆，SQLite 只是可重建的本地搜索索引，Agent 只需要掌握四个动作：

```bash
memoryhub ls [keyword]
memoryhub read <path>
memoryhub write <path> <content>
memoryhub delete <path>
```

这个仓库不应该放私有运行数据。真实域名、token、路径和私人记忆正文应该放在 `.env` 和本地 `MEMORYHUB_DATA_DIR` 里。

## 目录结构

```text
0-memoryhub-rules/     MemoryHub 规则
1-work-rules/          工作规则
2-projects/            项目母文件夹/项目子文件夹
3-tools/               Skills、MCP 说明、CLI 说明、集成模板
```

## 状态

状态写在 Markdown frontmatter 里，不是单独的 CLI 命令：

```md
---
status: active
---

# Note
```

允许的状态：

```text
active    长期有效
using     正在使用
archived  已归档，默认 ls/search 不返回
```

如果没有写状态，`write` 会按 `using` 建索引。`delete` 是软删除：它会把文件标记为 `archived`。

## Python / uv

```bash
uv run memoryhub ls
uv run memoryhub write 2-projects/example/overview.md "# Example\n\nA public example note."
uv run memoryhub ls example
uv run memoryhub read 2-projects/example/overview.md
uv run memoryhub delete 2-projects/example/overview.md
```

不用 uv 也可以：

```bash
python3 -m memoryhub.cli ls
python3 -m memoryhub.cli write 2-projects/example/overview.md "# Example"
```

## HTTP API

服务端暴露同样四个动作：

```bash
python3 -m memoryhub.server
```

```text
GET    /api/ls?q=keyword
GET    /api/read?path=...
POST   /api/write
DELETE /api/delete
```

设置 `MEMORYHUB_API_TOKEN` 后，请求必须带 `Authorization: Bearer <token>`。

## Node 客户端

Node 客户端通过 HTTP API 访问 MemoryHub：

```bash
export MEMORYHUB_BASE_URL=http://127.0.0.1:8765
export MEMORYHUB_API_TOKEN=replace-me

node node/memoryhub-node.mjs ls example
node node/memoryhub-node.mjs read 2-projects/example/overview.md
node node/memoryhub-node.mjs write 2-projects/example/current.md "# Current\n\nTask note."
node node/memoryhub-node.mjs delete 2-projects/example/current.md
```

## 去重

`ls <keyword>` 会按归一化后的正文 hash 去重。Markdown 标题不会参与 hash，所以两个文件即使标题不同，只要正文相同，也会被视为重复。`active` 优先于 `using`；`archived` 默认不返回。

## 被其他仓库调用

对于 `my-app-2`，建议把这个仓库作为上游源，并在父仓库里固定一个子依赖版本。
推荐布局是 git submodule：

```bash
git submodule add https://github.com/<owner>/mardio-memory-hub.git vendor/mardio-memory-hub
git commit -m "chore: add memory hub submodule"
```

运行时把 MemoryHub 当成旁路服务，让 `my-app-2` 通过四个 HTTP 端点调用它。
`MEMORYHUB_BASE_URL`、`MEMORYHUB_API_TOKEN`、真实数据目录等私有值放进 `.env`。

推荐方案：

```bash
git submodule add https://github.com/<owner>/mardio-memory-hub.git vendor/mardio-memory-hub
```

或者：

```bash
git subtree add --prefix vendor/mardio-memory-hub https://github.com/<owner>/mardio-memory-hub.git main --squash
```

应用可以把 HTTP API 作为旁路服务运行，也可以直接调用 Python CLI，并用 `MEMORYHUB_DATA_DIR` 指向自己的本地记忆目录。

更多 `my-app-2` 父子仓库同步方案见 `docs/sync-my-app-2.md`。
