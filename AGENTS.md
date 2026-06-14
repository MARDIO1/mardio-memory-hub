# MemoryHub Agent Instructions

MemoryHub has four operations:

```bash
memoryhub ls [keyword]
memoryhub read <path>
memoryhub write <path> <content>
memoryhub delete <path>
```

Files are the source of truth. SQLite is only a rebuildable local index.

Before a task:

1. Run `memoryhub ls "<project or task keyword>"`.
2. Read `0-memoryhub-rules/memoryhub-rules.md`.
3. Read relevant files under `1-work-rules`, `2-projects`, or `3-tools`.

During a task:

1. Write useful task memory with `memoryhub write`.
2. Put status in markdown frontmatter when needed:
   ```md
   ---
   status: active
   ---
   ```
3. Use `status: using` for temporary task memory.
4. Use `status: active` for long-term memory.

Deleting:

1. `memoryhub delete <path>` is a soft delete.
2. It marks the file as `archived`.
3. Do not manually remove memory files unless you know how to rebuild the index.

Privacy:

1. Do not store tokens, passwords, private domains, IPs, cookies, or personal secrets in memory files.
2. Keep real runtime values in `.env`, never in Git.
3. Use `.env.example` for public templates.
