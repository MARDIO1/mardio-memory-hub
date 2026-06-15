# Agent Memory Hub for AstrBot

Configure `/AstrBot/data/agent-memory/config.json` from `integrations/astrbot/config.example.json`.

This plugin provides four direct commands and matching LLM tools. `/mem_ls`
without a keyword lists the global SQLite index; add a keyword only when you
want filtering.

```text
/mem_ls
/mem_ls keyword
/mem_read path
/mem_write path | markdown
/mem_delete path
```

`/mem_delete` permanently deletes the file and its SQLite index row. Use it for
short-lived memory that should not keep appearing in future index/search flows.
