# mardio-memory-hub

<a href="README.md"><kbd>简体中文</kbd></a>
<a href="README.en.md"><kbd>English</kbd></a>

I built this for my own agent workflow, and it has been useful.

MemoryHub is a lightweight cross-device and agent-to-agent memory layer. It is meant for two practical cases:

1. Different agents, devices, or users need to cooperate, but you do not want to fully open every permission boundary. MemoryHub can carry context, audit notes, network debugging records, candidate memory, and work state.
2. A new device or agent environment needs a personal skill hub, rule hub, and project context hub. The agent reads the rules and current project context before working.

This repository contains only two kinds of things:

1. **MemoryHub server**: Python HTTP API, SQLite index, Markdown file storage, and built-in web frontend.
2. **Agent clients**: Python CLI, Node CLI, AstrBot plugin template, and AGENTS/skill-style usage notes.

The core surface is intentionally small:

```bash
memoryhub ls [keyword]          # without keywords, list SQLite index only
memoryhub read <path>
memoryhub write <path> <content>
memoryhub delete <path>         # archive by default; add --hard to remove
```

Markdown or jsonl files are the source of truth. SQLite powers index listing and filtering. Agents should run `ls` first, then `read` only the documents that matter.

---

## Layout

```text
0-memoryhub-rules/     rules for using MemoryHub itself
1-work-rules/          general work rules
2-projects/            project memory, grouped by project folders
3-tools/               skills, MCP notes, CLIs, plugins, tool docs
memoryhub/             server and Python CLI
node/                  Node CLI
integrations/astrbot/  AstrBot plugin template
docs/                  API and integration notes
```

Status is stored in Markdown frontmatter:

```md
---
status: using
tags: [network, audit]
---

# Current context
```

Allowed statuses:

```text
active    long-term memory
using     currently used memory, usually task context
archived  archived and hidden from default search
```

CLI `delete` is a soft delete by default. It marks the file as `archived`. Use `memoryhub delete <path> --hard` for low-value short-lived memory; this removes both the body file and the SQLite index row.

## Server

Start the server:

```bash
uv run python -m memoryhub.server
```

Without uv:

```bash
python3 -m memoryhub.server
```

Common environment variables:

```env
MEMORYHUB_DATA_DIR=/path/to/memoryhub-data
MEMORYHUB_DB_PATH=/path/to/memoryhub.sqlite
MEMORYHUB_API_HOST=127.0.0.1
MEMORYHUB_API_PORT=8765
MEMORYHUB_API_TOKEN=replace-me
```

API:

```text
GET    /api/ls?q=keyword
GET    /api/read?path=...
POST   /api/write
DELETE /api/delete
GET    /health
```

If `MEMORYHUB_API_TOKEN` is set, HTTP clients must send:

```text
Authorization: Bearer <token>
```

The same server provides the web frontend:

```text
GET /
GET /app
```

When mounting MemoryHub behind an existing admin app, let that app own login and permissions, then proxy MemoryHub server-side. Add this header when proxying the web page:

```text
X-MemoryHub-Trusted-Proxy: 1
```

In that mode, the browser does not see a bearer-token input, and MemoryHub can bind only to `127.0.0.1`.

Optional top-bar links:

```env
MEMORYHUB_MY_APP_2_URL=http://127.0.0.1:3000/admin/agent-memory
MEMORYHUB_MY_APP_2_LABEL=Open my-app-2
MEMORYHUB_CLOUD_DISK_URL=http://127.0.0.1:3000/disk
MEMORYHUB_CLOUD_DISK_LABEL=Open cloud disk
```

## Agent Clients

Python CLI:

```bash
uv run memoryhub ls
uv run memoryhub ls audit
uv run memoryhub read 2-projects/example/current.md
uv run memoryhub write 2-projects/example/current.md "# Current\n\nRemember this."
uv run memoryhub delete 2-projects/example/current.md
uv run memoryhub delete 2-projects/example/current.md --hard
```

Without uv:

```bash
python3 -m memoryhub.cli ls
python3 -m memoryhub.cli ls audit
python3 -m memoryhub.cli read 2-projects/example/current.md
```

Node CLI:

```bash
export MEMORYHUB_BASE_URL=http://127.0.0.1:8765
export MEMORYHUB_API_TOKEN=replace-me

node node/memoryhub-node.mjs ls
node node/memoryhub-node.mjs ls audit
node node/memoryhub-node.mjs read 2-projects/example/current.md
node node/memoryhub-node.mjs write 2-projects/example/current.md "# Current\n\nRemember this."
node node/memoryhub-node.mjs delete 2-projects/example/current.md
```

Recommended agent flow:

1. Run plain `ls` before work to inspect the latest SQLite index.
2. Run `ls keyword` if the index is too large.
3. Run `read` only when full context is needed.
3. Run `write` for durable rules, project context, and debugging records.
4. Run `delete --hard` for short-lived memory that is no longer useful; archive only when you want to keep it for later review.

## AstrBot

Copy this plugin folder into AstrBot's plugin directory:

```text
integrations/astrbot/agent_memory_hub
```

Create runtime config from:

```text
integrations/astrbot/config.example.json
```

Manual chat commands:

```text
/mem_ls
/mem_ls keyword
/mem_read 2-projects/example/current.md
/mem_write 2-projects/example/current.md | # Current

Markdown content to write
/mem_delete 2-projects/example/current.md
```

AstrBot `/mem_delete` and `agent_memory_delete` permanently delete the file and index row. Use them for low-value transient memory.

LLM tool names exposed by the plugin:

```text
agent_memory_ls
agent_memory_read
agent_memory_write
agent_memory_delete
```

Humans should send the concrete commands: `/mem_ls`, `/mem_read`, `/mem_write`, and `/mem_delete`. If tool calling works, the AstrBot LLM can call matching `agent_memory_ls/read/write/delete` tools directly.

## AGENTS/Skill Notes

`AGENTS.md` is the general entrypoint for agents. Agents only need to know:

- Read `0-memoryhub-rules/` first.
- Put work rules in `1-work-rules/`.
- Put project context in `2-projects/<project>/`.
- Put skill, MCP, CLI, and plugin notes in `3-tools/`.
- Use only `ls/read/write/delete` to operate memory.

For a dedicated agent skill, summarize this as: search MemoryHub first, read relevant files, write useful candidate memory, and archive obsolete task memory.

## Using It From Other Projects

The simplest boundary is HTTP: run MemoryHub as a small side service, then let other projects and agents call the API.

If you want to pin the source inside another repository, use a git submodule:

```bash
git submodule add https://github.com/MARDIO1/mardio-memory-hub.git vendor/mardio-memory-hub
```

The parent project records the MemoryHub commit it uses, while MemoryHub remains independently updatable.
