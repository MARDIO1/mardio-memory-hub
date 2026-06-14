# mardio-memory-hub

<a href="README.md"><kbd>简体中文</kbd></a>
<a href="README.en.md"><kbd>English</kbd></a>

自用感觉挺好用。

我做这个东西，是因为 Agent 需要一个公共记忆，但这个记忆不能只躲在数据库里。只放数据库，管理员不好看、Agent 不好改、迁移也麻烦；只放一堆 Markdown，又很难统一搜索和去重。

MemoryHub 的思路很简单：**Markdown 文件是正文，SQLite 只是索引。** 人可以像管理普通文件一样看和改，Agent 可以用固定的四个动作读写。

```bash
memoryhub ls [keyword]
memoryhub read <path>
memoryhub write <path> <content>
memoryhub delete <path>
```

---

## 它是什么

`mardio-memory-hub` 是一个给 AI Agent 共用的轻量记忆仓库。

它适合存这些东西：

- Agent 开工前应该读取的规则；
- 项目的长期背景和当前上下文；
- 某个任务正在用的临时记忆；
- 常用 skill、MCP、CLI、工具接入说明。

它现在包含：

- Python CLI；
- 同样四个动作的 HTTP API；
- Node HTTP 客户端；
- AstrBot 插件模板；
- 一套 Markdown 目录约定。

## 目录约定

```text
0-memoryhub-rules/     MemoryHub 自己的使用规则
1-work-rules/          通用工作规则
2-projects/            项目记忆，按项目建子目录
3-tools/               skills、MCP、CLI、插件和工具说明
```

目录名开头带数字，是为了让 Agent 和人都能稳定地按顺序扫一遍。

## 记忆状态

状态写在 Markdown frontmatter 里：

```md
---
status: using
tags: [example]
---

# 当前任务
```

支持三种状态：

```text
active    长期有效
using     正在使用，通常是当前任务或短期上下文
archived  已归档，默认 ls 不显示
```

`memoryhub delete` 不是物理删除，而是把文件标记成 `archived`。这样误删以后还能找回来，也不会继续污染默认搜索结果。

## 安装和运行

用 uv：

```bash
uv run memoryhub ls
```

不用 uv：

```bash
python3 -m memoryhub.cli ls
```

`MEMORYHUB_DATA_DIR` 用来指定实际存放记忆文件和 SQLite 索引的位置。

## CLI 用法

```bash
memoryhub ls project
memoryhub read 2-projects/example/current.md
memoryhub write 2-projects/example/current.md "# Current\n\nRemember this."
memoryhub delete 2-projects/example/current.md
```

四个动作故意保持很少。分类、生命周期、标签这些信息都写在 Markdown 里，Agent 可以用自然语言约定来管理，不需要再记一堆子命令。

## HTTP API

启动服务：

```bash
python3 -m memoryhub.server
```

接口也是同样四个动作：

```text
GET    /api/ls?q=keyword
GET    /api/read?path=...
POST   /api/write
DELETE /api/delete
```

如果设置了 `MEMORYHUB_API_TOKEN`，HTTP 请求需要带 bearer token。

## Node 客户端

```bash
export MEMORYHUB_BASE_URL=http://127.0.0.1:8765
export MEMORYHUB_API_TOKEN=replace-me

node node/memoryhub-node.mjs ls project
node node/memoryhub-node.mjs read 2-projects/example/current.md
node node/memoryhub-node.mjs write 2-projects/example/current.md "# Current\n\nRemember this."
node node/memoryhub-node.mjs delete 2-projects/example/current.md
```

## AstrBot

把 `integrations/astrbot/agent_memory_hub` 放到 AstrBot 插件目录，再按 `integrations/astrbot/config.example.json` 写运行配置。

插件提供聊天命令：

```text
/mem_ls
/mem_read
/mem_write
/mem_delete
```

也提供给 LLM 调用的工具：

```text
agent_memory_ls
agent_memory_read
agent_memory_write
agent_memory_delete
```

## 在其他项目里使用

最稳的方式是把 MemoryHub 当成一个小服务运行，其他项目或 Agent 通过 HTTP API 调它。

如果想把源码固定到某个项目里，推荐用 submodule：

```bash
git submodule add https://github.com/<owner>/mardio-memory-hub.git vendor/mardio-memory-hub
```

这样主项目只记录正在使用的 MemoryHub commit；MemoryHub 自己仍然保持独立更新。

如果你不想处理 submodule，也可以用 subtree，但后续和上游同步会更笨重。
