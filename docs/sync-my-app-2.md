# Syncing With my-app-2

`mardio-memory-hub` should be the source repository for MemoryHub code, docs,
agent instructions, API shape, and integration templates. `my-app-2` should not
copy and evolve a second version of the same framework.

## Recommended Shape

Use a parent/child git relationship:

```text
my-app-2/
  vendor/
    mardio-memory-hub/   git submodule pinned to a commit
```

`my-app-2` owns:

- Next.js routes, RBAC, admin UI, deployment config, and local `.env`.
- The actual runtime memory data directory and SQLite database.
- Server-specific tokens and private domains.

`mardio-memory-hub` owns:

- The four generic operations: `ls`, `read`, `write`, `delete`.
- Python CLI, HTTP service, Node client, and AstrBot template.
- Public documentation and agent-facing rules.

## Why Submodule

Use a git submodule when you want exact version pinning.

Pros:

- `my-app-2` records the exact MemoryHub commit it is using.
- Updates are explicit and reviewable.
- Rollback is just reverting the submodule pointer.
- The MemoryHub repository can be reused by AstrBot, Codex, MCP wrappers, and
  other agents without depending on `my-app-2`.

Cons:

- Deploy scripts must run `git submodule update --init --recursive`.
- Developers need to understand that the child repository has its own commits.

If submodules become annoying, use `git subtree` instead. Subtree is easier for
single-repo checkout, but upstream merges are less clean.

## Add To my-app-2

From the parent repository root:

```bash
git submodule add https://github.com/<owner>/mardio-memory-hub.git my-app-2/vendor/mardio-memory-hub
git commit -m "chore: add memory hub submodule"
```

On deploy or fresh checkout:

```bash
git submodule update --init --recursive
```

## Runtime Integration

Prefer the HTTP API boundary:

```text
my-app-2 API/admin UI
  -> MEMORYHUB_BASE_URL
  -> mardio-memory-hub service
  -> markdown files + rebuildable SQLite index
```

Use `.env` in `my-app-2`:

```env
MEMORYHUB_BASE_URL=http://127.0.0.1:8765
MEMORYHUB_API_TOKEN=replace-with-private-token
MEMORYHUB_DATA_DIR=/absolute/path/to/private/memoryhub-data
```

Then `my-app-2` calls:

```text
GET    /api/ls?q=keyword
GET    /api/read?path=...
POST   /api/write
DELETE /api/delete
```

The Next.js project can keep its own admin pages and permission checks. Those
pages should call the MemoryHub API instead of duplicating MemoryHub indexing
logic.

## Updating The Child Version

After changes are merged into `mardio-memory-hub`:

```bash
git -C my-app-2/vendor/mardio-memory-hub fetch origin
git -C my-app-2/vendor/mardio-memory-hub checkout origin/main
git add my-app-2/vendor/mardio-memory-hub
git commit -m "chore: update memory hub"
```

If you want to always pull the latest upstream `main`:

```bash
git submodule update --remote --merge my-app-2/vendor/mardio-memory-hub
git add my-app-2/vendor/mardio-memory-hub
git commit -m "chore: update memory hub"
```

## Publishing This Repository

If the GitHub repository already exists:

```bash
git remote add origin https://github.com/<owner>/mardio-memory-hub.git
git push -u origin main
```

If it does not exist, create it first on GitHub or with `gh`:

```bash
gh repo create <owner>/mardio-memory-hub --private --source . --remote origin --push
```

Use `--public` only when you are comfortable publishing all repository content.
This repository is designed to avoid private domains and tokens, but review
before public release.
