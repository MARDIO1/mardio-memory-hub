# MemoryHub Rules

MemoryHub is a markdown-first memory system for agents.

## Categories

- `0-memoryhub-rules`: rules for MemoryHub itself.
- `1-work-rules`: cross-task working rules and preferences.
- `2-projects`: project parent folders and project subfolders.
- `3-tools`: reusable skills, MCP notes, CLI usage, and integration templates.

## Status

- `active`: long-term valid memory.
- `using`: currently useful task or workspace memory.
- `archived`: retained for audit but excluded from default search.

## Required Operations

Use CLI or API for all operations.

```bash
memoryhub ls "keyword"
memoryhub read "2-projects/example/note.md"
memoryhub write "2-projects/example/note.md" "# Note"
memoryhub delete "2-projects/example/note.md"
```

Status lives in markdown frontmatter:

```md
---
status: active
---
```

`delete` marks the file as `archived`.

## Search Discipline

Search results are deduplicated by normalized content hash. Agents should still avoid repeating the same document in one reasoning turn.

## Privacy

Never commit real tokens, domains, private server paths, IPs, cookies, or secrets.
