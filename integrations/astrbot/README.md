# AstrBot Integration

This integration is a template. It does not contain real tokens or private URLs.

Install by copying:

```text
integrations/astrbot/agent_memory_hub -> /AstrBot/data/plugins/agent_memory_hub
integrations/astrbot/config.example.json -> /AstrBot/data/agent-memory/config.json
```

Edit `/AstrBot/data/agent-memory/config.json` with local runtime values.

Commands:

```text
/mem_ls keyword
/mem_read 2-projects/example/overview.md
/mem_write 2-projects/example/current.md | # Current\n\nTask note
/mem_delete 2-projects/example/current.md
```

The plugin also registers LLM tools:

```text
agent_memory_ls
agent_memory_read
agent_memory_write
agent_memory_delete
```
