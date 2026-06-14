# mardio-memory-hub

<a href="README.md"><kbd>简体中文</kbd></a>
<a href="README.en.md"><kbd>English</kbd></a>

I built this because agents need a shared memory that is easy to inspect, edit,
move, and delete. A database-only memory is hard to review. Random notes in a
folder are hard to search consistently. MemoryHub sits in the middle: Markdown
files are the source of truth, and SQLite is only a rebuildable index.

The useful surface is deliberately small:

```bash
memoryhub ls [keyword]
memoryhub read <path>
memoryhub write <path> <content>
memoryhub delete <path>
```

---

## What It Is

MemoryHub is a small shared-memory layer for AI agents.

It gives agents one common place to store:

- rules that should be read before work starts;
- project notes and current context;
- temporary task memory;
- reusable tool, skill, MCP, and integration notes.

The project contains:

- a Python CLI;
- a small HTTP API with the same four operations;
- a built-in web frontend;
- a Node HTTP client;
- an AstrBot integration template;
- a simple Markdown directory convention.

## Directory Convention

```text
0-memoryhub-rules/     rules for using MemoryHub
1-work-rules/          general work rules
2-projects/            project notes, grouped by project folders
3-tools/               skills, MCP notes, CLIs, integrations
```

## Status

Status is stored in Markdown frontmatter:

```md
---
status: using
tags: [example]
---

# Current task
```

Allowed values:

```text
active    long-term memory
using     current or temporary memory
archived  kept on disk, hidden from default ls
```

`delete` is a soft delete. It marks the file as `archived`.

## Install

With uv:

```bash
uv run memoryhub ls
```

Without uv:

```bash
python3 -m memoryhub.cli ls
```

Use `MEMORYHUB_DATA_DIR` to point MemoryHub at the directory that stores memory
files and the local SQLite index.

## CLI

```bash
memoryhub ls project
memoryhub read 2-projects/example/current.md
memoryhub write 2-projects/example/current.md "# Current\n\nRemember this."
memoryhub delete 2-projects/example/current.md
```

## HTTP API

```bash
python3 -m memoryhub.server
```

```text
GET    /api/ls?q=keyword
GET    /api/read?path=...
POST   /api/write
DELETE /api/delete
```

Set `MEMORYHUB_API_TOKEN` if the HTTP API should require bearer auth.

## Web Frontend

The same server also serves a web page:

```text
GET /
GET /app
```

The page can search, read, write, and archive memory files. If
`MEMORYHUB_API_TOKEN` is set, the page shows a token input; the token is saved
only in the current browser's localStorage.

Use environment variables to connect it to an existing app:

```env
MEMORYHUB_MY_APP_2_URL=http://127.0.0.1:3000/admin/agent-memory
MEMORYHUB_MY_APP_2_LABEL=Open my-app-2
MEMORYHUB_CLOUD_DISK_URL=http://127.0.0.1:3000/disk
MEMORYHUB_CLOUD_DISK_LABEL=Open cloud disk
```

These values only render top-bar links. They do not affect memory data.

## Node Client

```bash
export MEMORYHUB_BASE_URL=http://127.0.0.1:8765
export MEMORYHUB_API_TOKEN=replace-me

node node/memoryhub-node.mjs ls project
node node/memoryhub-node.mjs read 2-projects/example/current.md
node node/memoryhub-node.mjs write 2-projects/example/current.md "# Current\n\nRemember this."
node node/memoryhub-node.mjs delete 2-projects/example/current.md
```

## AstrBot

Copy `integrations/astrbot/agent_memory_hub` into AstrBot's plugin directory and
create a runtime config from `integrations/astrbot/config.example.json`.

The template exposes:

```text
/mem_ls
/mem_read
/mem_write
/mem_delete
```

and matching LLM tools:

```text
agent_memory_ls
agent_memory_read
agent_memory_write
agent_memory_delete
```

## Reuse From Another Project

The cleanest boundary is the HTTP API: run MemoryHub as a small side service and
let any app or agent call the four endpoints.

If you want to vendor the source into another repository, use a submodule:

```bash
git submodule add https://github.com/<owner>/mardio-memory-hub.git vendor/mardio-memory-hub
```

Use subtree only when you want a single checkout and do not mind a heavier
upstream-sync workflow.
