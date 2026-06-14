# API

Authentication is optional. If `MEMORYHUB_API_TOKEN` is set, pass:

```text
Authorization: Bearer <token>
```

The API mirrors the CLI's four operations.

## Web UI

The HTTP server also serves the built-in web frontend:

```http
GET /
GET /app
```

Configure top-bar links with:

```env
MEMORYHUB_MY_APP_2_URL=http://127.0.0.1:3000/admin/agent-memory
MEMORYHUB_CLOUD_DISK_URL=http://127.0.0.1:3000/disk
```

## ls

```http
GET /api/ls?q=keyword
```

Returns deduplicated documents. Archived files are excluded by default.

## read

```http
GET /api/read?path=2-projects/example/overview.md
```

## write

```http
POST /api/write
Content-Type: application/json

{
  "path": "2-projects/example/overview.md",
  "content": "# Example Overview\n\n..."
}
```

Use markdown frontmatter for status:

```md
---
status: active
---
```

## delete

Soft delete marks the document as `archived`:

```http
DELETE /api/delete
Content-Type: application/json

{
  "path": "2-projects/example/overview.md"
}
```
