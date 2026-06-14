# mardio-memory-hub

<a href="README.md"><kbd>English</kbd></a>
<a href="README.zh-CN.md"><kbd>简体中文</kbd></a>

Markdown-first memory hub for agents.

The repository is intentionally small: files are the memory, SQLite is only a local searchable index, and agents operate through four verbs:

```bash
memoryhub ls [keyword]
memoryhub read <path>
memoryhub write <path> <content>
memoryhub delete <path>
```

No private runtime data belongs in this repository. Real domains, tokens, paths, and memory bodies should live in `.env` and a local `MEMORYHUB_DATA_DIR`.

## Layout

```text
0-memoryhub-rules/     MemoryHub rules
1-work-rules/          Work rules
2-projects/            Project parent/subfolders
3-tools/               Skills, MCP notes, CLI notes, integrations
```

## Status

Status is optional markdown frontmatter, not a separate CLI command:

```md
---
status: active
---

# Note
```

Allowed values:

```text
active    long-term valid
using     currently useful
archived  retained but excluded from default ls/search
```

If no status is present, `write` indexes the file as `using`. `delete` is a soft delete: it marks the file as `archived`.

## Python / uv

```bash
uv run memoryhub ls
uv run memoryhub write 2-projects/example/overview.md "# Example\n\nA public example note."
uv run memoryhub ls example
uv run memoryhub read 2-projects/example/overview.md
uv run memoryhub delete 2-projects/example/overview.md
```

Without uv:

```bash
python3 -m memoryhub.cli ls
python3 -m memoryhub.cli write 2-projects/example/overview.md "# Example"
```

## HTTP API

The service exposes the same four verbs:

```bash
python3 -m memoryhub.server
```

```text
GET    /api/ls?q=keyword
GET    /api/read?path=...
POST   /api/write
DELETE /api/delete
```

Set `MEMORYHUB_API_TOKEN` to require `Authorization: Bearer <token>`.

## Node Client

The Node client talks to the HTTP API:

```bash
export MEMORYHUB_BASE_URL=http://127.0.0.1:8765
export MEMORYHUB_API_TOKEN=replace-me

node node/memoryhub-node.mjs ls example
node node/memoryhub-node.mjs read 2-projects/example/overview.md
node node/memoryhub-node.mjs write 2-projects/example/current.md "# Current\n\nTask note."
node node/memoryhub-node.mjs delete 2-projects/example/current.md
```

## Deduplication

`ls <keyword>` deduplicates by normalized body hash. Markdown headings are ignored for the hash, so two files with different titles but the same body are treated as duplicates. `active` wins over `using`; archived files are excluded by default.

## Use From Another Repository

For `my-app-2`, use this repository as the upstream source and pin it as a child dependency.
The recommended layout is a git submodule:

```bash
git submodule add https://github.com/<owner>/mardio-memory-hub.git vendor/mardio-memory-hub
git commit -m "chore: add memory hub submodule"
```

Run MemoryHub as a side service and let `my-app-2` call the four HTTP endpoints with
`MEMORYHUB_BASE_URL` and `MEMORYHUB_API_TOKEN`. Keep app-specific tokens, domains, and
data directories in `.env`.

Recommended options:

```bash
git submodule add https://github.com/<owner>/mardio-memory-hub.git vendor/mardio-memory-hub
```

or:

```bash
git subtree add --prefix vendor/mardio-memory-hub https://github.com/<owner>/mardio-memory-hub.git main --squash
```

Applications can run the HTTP API as a side service, or call the Python CLI directly with `MEMORYHUB_DATA_DIR` pointing to their local memory directory.

See `docs/sync-my-app-2.md` for the recommended parent/child git workflow.
