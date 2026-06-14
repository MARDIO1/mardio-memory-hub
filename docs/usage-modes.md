# Usage Modes

MemoryHub has four operations everywhere: `ls`, `read`, `write`, and `delete`.

## Python CLI

```bash
python3 -m memoryhub.cli ls "keyword"
python3 -m memoryhub.cli read 2-projects/app/current.md
python3 -m memoryhub.cli write 2-projects/app/current.md "# Current\n\nTask note."
python3 -m memoryhub.cli delete 2-projects/app/current.md
```

## HTTP API

```bash
python3 -m memoryhub.server
curl "$MEMORYHUB_BASE_URL/api/ls?q=keyword" -H "Authorization: Bearer $MEMORYHUB_API_TOKEN"
```

## Node Client

```bash
node node/memoryhub-node.mjs ls keyword
node node/memoryhub-node.mjs read 2-projects/app/current.md
node node/memoryhub-node.mjs write 2-projects/app/current.md "# Current\n\nTask note."
node node/memoryhub-node.mjs delete 2-projects/app/current.md
```

## AstrBot

Copy `integrations/astrbot/agent_memory_hub` into AstrBot's plugin directory and configure runtime values from `integrations/astrbot/config.example.json`.

AstrBot commands:

```text
/mem_ls keyword
/mem_read 2-projects/app/current.md
/mem_write 2-projects/app/current.md | # Current\n\nTask note.
/mem_delete 2-projects/app/current.md
```

## MCP

MCP is not included in the first version. A future MCP server can wrap the same four HTTP endpoints without changing the memory file layout.
