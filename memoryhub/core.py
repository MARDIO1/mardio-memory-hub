from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STATUSES = {"active", "using", "archived"}
DEFAULT_DIRS = [
    "0-memoryhub-rules",
    "1-work-rules",
    "2-projects",
    "inbox",
    "3-tools/skills",
    "3-tools/mcp",
    "3-tools/cli",
    "3-tools/integrations",
]


@dataclass(frozen=True)
class HubPaths:
    data_dir: Path
    db_path: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_paths(data_dir: str | None = None, db_path: str | None = None) -> HubPaths:
    root = Path(data_dir or os.getenv("MEMORYHUB_DATA_DIR", "./memoryhub-data")).resolve()
    db = Path(db_path or os.getenv("MEMORYHUB_DB_PATH", str(root / ".memoryhub" / "index.sqlite"))).resolve()
    return HubPaths(root, db)


def ensure_inside(root: Path, target: Path) -> Path:
    resolved = target.resolve()
    root_resolved = root.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise ValueError(f"path escapes memory hub data dir: {target}")
    return resolved


def normalize_rel_path(value: str) -> str:
    cleaned = value.strip().replace("\\", "/").lstrip("/")
    if not cleaned:
        raise ValueError("path is required")
    if cleaned.endswith("/"):
        raise ValueError("path must point to a file")
    if not cleaned.endswith((".md", ".jsonl")):
        cleaned = f"{cleaned}.md"
    return cleaned


def slugify(value: str) -> str:
    slug = re.sub(r"[^\w.\-\u4e00-\u9fff]+", "-", value.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "memory"


def infer_category(rel_path: str) -> str:
    first = rel_path.split("/", 1)[0]
    if first.startswith("0-"):
        return "rules"
    if first.startswith("1-"):
        return "work-rules"
    if first.startswith("2-"):
        return "projects"
    if first.startswith("3-"):
        return "tools"
    if first == "inbox":
        return "inbox"
    if first in {"personas", "context-packs", "memories"}:
        return "projects"
    return "misc"


def content_hash(content: str) -> str:
    body_content = content
    if body_content.startswith("---\n"):
        end = body_content.find("\n---", 4)
        if end >= 0:
            body_content = body_content[end + 4 :]
    body_lines = [line for line in body_content.splitlines() if not line.lstrip().startswith("#")]
    body = "\n".join(body_lines) if body_lines else body_content
    normalized = re.sub(r"\s+", " ", body.strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def title_from_content(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip() or fallback
    return fallback


def summary_from_content(content: str, max_len: int = 220) -> str:
    text = re.sub(r"\s+", " ", content.replace("#", " ")).strip()
    return text[:max_len]


def frontmatter_value(content: str, key: str) -> str | None:
    if not content.startswith("---\n"):
        return None
    end = content.find("\n---", 4)
    if end < 0:
        return None
    for line in content[4:end].splitlines():
        name, sep, value = line.partition(":")
        if sep and name.strip().lower() == key.lower():
            return value.strip().strip("\"'")
    return None


def status_from_content(content: str, fallback: str = "using") -> str:
    status = frontmatter_value(content, "status")
    return status if status in VALID_STATUSES else fallback


def set_content_status(content: str, status: str) -> str:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")
    if content.startswith("---\n"):
        end = content.find("\n---", 4)
        if end >= 0:
            head = content[4:end].splitlines()
            body = content[end + 4 :].lstrip("\n")
            found = False
            updated = []
            for line in head:
                name, sep, _ = line.partition(":")
                if sep and name.strip().lower() == "status":
                    updated.append(f"status: {status}")
                    found = True
                else:
                    updated.append(line)
            if not found:
                updated.append(f"status: {status}")
            return "---\n" + "\n".join(updated) + "\n---\n\n" + body
    return f"---\nstatus: {status}\n---\n\n{content}"


def connect(paths: HubPaths) -> sqlite3.Connection:
    paths.db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(paths.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
          id TEXT PRIMARY KEY,
          path TEXT NOT NULL UNIQUE,
          category TEXT NOT NULL,
          title TEXT NOT NULL,
          summary TEXT NOT NULL DEFAULT '',
          tags_json TEXT NOT NULL DEFAULT '[]',
          status TEXT NOT NULL DEFAULT 'using',
          content_hash TEXT NOT NULL,
          size_bytes INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          last_accessed_at TEXT
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(content_hash)")
    return conn


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["tags"] = json.loads(data.pop("tags_json") or "[]")
    return data


def init_hub(paths: HubPaths) -> None:
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    for directory in DEFAULT_DIRS:
        (paths.data_dir / directory).mkdir(parents=True, exist_ok=True)
    rules_path = paths.data_dir / "0-memoryhub-rules" / "memoryhub-rules.md"
    if not rules_path.exists():
        rules_path.write_text(
            "\n".join(
                [
                    "# MemoryHub Rules",
                    "",
                    "- Markdown/jsonl files are the source of truth.",
                    "- SQLite is only an index, not the memory body.",
                    "- Use CLI or API for ls, read, write, and delete.",
                    "- Status values: active, using, archived.",
                    "- Do not store secrets, tokens, private domains, or credentials in memory files.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    with connect(paths) as conn:
        conn.commit()
    reindex(paths)


def upsert_document(
    paths: HubPaths,
    rel_path: str,
    content: str,
    *,
    title: str | None = None,
    summary: str | None = None,
    tags: list[str] | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    rel_path = normalize_rel_path(rel_path)
    effective_status = status or status_from_content(content)
    if effective_status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")
    absolute = ensure_inside(paths.data_dir, paths.data_dir / rel_path)
    absolute.parent.mkdir(parents=True, exist_ok=True)
    absolute.write_text(content, encoding="utf-8")
    return index_file(paths, absolute, title=title, summary=summary, tags=tags, status=effective_status)


def index_file(
    paths: HubPaths,
    absolute: Path,
    *,
    title: str | None = None,
    summary: str | None = None,
    tags: list[str] | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    absolute = ensure_inside(paths.data_dir, absolute)
    rel_path = absolute.relative_to(paths.data_dir).as_posix()
    content = absolute.read_text(encoding="utf-8")
    now = utc_now()
    doc_id = hashlib.sha256(rel_path.encode("utf-8")).hexdigest()[:24]
    with connect(paths) as conn:
        existing = conn.execute("SELECT * FROM documents WHERE path = ?", (rel_path,)).fetchone()
        effective_status = status or status_from_content(content, existing["status"] if existing else "using")
        if effective_status not in VALID_STATUSES:
            effective_status = "using"
        record = {
            "id": doc_id,
            "path": rel_path,
            "category": infer_category(rel_path),
            "title": title or title_from_content(content, Path(rel_path).stem),
            "summary": summary if summary is not None else summary_from_content(content),
            "tags_json": json.dumps(tags if tags is not None else (json.loads(existing["tags_json"]) if existing else []), ensure_ascii=False),
            "status": effective_status,
            "content_hash": content_hash(content),
            "size_bytes": absolute.stat().st_size,
            "created_at": existing["created_at"] if existing else now,
            "updated_at": now,
        }
        conn.execute(
            """
            INSERT INTO documents (
              id, path, category, title, summary, tags_json, status, content_hash,
              size_bytes, created_at, updated_at
            ) VALUES (
              :id, :path, :category, :title, :summary, :tags_json, :status, :content_hash,
              :size_bytes, :created_at, :updated_at
            )
            ON CONFLICT(path) DO UPDATE SET
              category=excluded.category,
              title=excluded.title,
              summary=excluded.summary,
              tags_json=excluded.tags_json,
              status=excluded.status,
              content_hash=excluded.content_hash,
              size_bytes=excluded.size_bytes,
              updated_at=excluded.updated_at
            """,
            record,
        )
        conn.commit()
        row = conn.execute("SELECT * FROM documents WHERE path = ?", (rel_path,)).fetchone()
        return row_to_dict(row)


def reindex(paths: HubPaths) -> dict[str, int]:
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    indexed = 0
    seen: set[str] = set()
    for absolute in paths.data_dir.rglob("*"):
        if not absolute.is_file() or absolute.suffix not in {".md", ".jsonl"}:
            continue
        if ".memoryhub" in absolute.parts:
            continue
        row = index_file(paths, absolute)
        seen.add(row["path"])
        indexed += 1
    with connect(paths) as conn:
        existing = [row["path"] for row in conn.execute("SELECT path FROM documents").fetchall()]
        removed = 0
        for rel_path in existing:
            if rel_path not in seen:
                conn.execute("DELETE FROM documents WHERE path = ?", (rel_path,))
                removed += 1
        conn.commit()
    return {"indexed": indexed, "removed": removed}


def list_documents(paths: HubPaths, status: str | None = None, category: str | None = None) -> list[dict[str, Any]]:
    if not paths.db_path.exists():
        reindex(paths)
    query = "SELECT * FROM documents"
    clauses = []
    args: list[Any] = []
    if status:
        clauses.append("status = ?")
        args.append(status)
    if category:
        clauses.append("category = ?")
        args.append(category)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY updated_at DESC, path ASC"
    with connect(paths) as conn:
        return [row_to_dict(row) for row in conn.execute(query, args).fetchall()]


def read_document(paths: HubPaths, rel_path: str) -> dict[str, Any]:
    rel_path = normalize_rel_path(rel_path)
    absolute = ensure_inside(paths.data_dir, paths.data_dir / rel_path)
    content = absolute.read_text(encoding="utf-8")
    with connect(paths) as conn:
        row = conn.execute("SELECT * FROM documents WHERE path = ?", (rel_path,)).fetchone()
        conn.execute("UPDATE documents SET last_accessed_at = ? WHERE path = ?", (utc_now(), rel_path))
        conn.commit()
    return {"document": row_to_dict(row) if row else index_file(paths, absolute), "content": content}


def search(paths: HubPaths, query: str = "", *, limit: int = 10, include_archived: bool = False) -> list[dict[str, Any]]:
    terms = [term.lower() for term in query.split() if term.strip()]
    rows = list_documents(paths)
    status_rank = {"active": 0, "using": 1, "archived": 2}
    results: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()
    for row in rows:
        if row["status"] == "archived" and not include_archived:
            continue
        try:
            content = (paths.data_dir / row["path"]).read_text(encoding="utf-8")
        except FileNotFoundError:
            continue
        haystack = " ".join(
            [
                row["path"],
                row["title"],
                row["summary"],
                " ".join(row["tags"]),
                content,
            ]
        ).lower()
        if terms and not all(term in haystack for term in terms):
            continue
        if row["content_hash"] in seen_hashes:
            continue
        seen_hashes.add(row["content_hash"])
        score = sum(haystack.count(term) for term in terms) if terms else 1
        snippet = make_snippet(content, terms)
        results.append({**row, "score": score, "snippet": snippet})
    results.sort(key=lambda item: (status_rank.get(item["status"], 9), -item["score"], item["path"]))
    return results[: max(1, min(limit, 50))]


def make_snippet(content: str, terms: list[str], max_len: int = 320) -> str:
    normalized = re.sub(r"\s+", " ", content).strip()
    lower = normalized.lower()
    start = 0
    for term in terms:
        idx = lower.find(term)
        if idx >= 0:
            start = max(0, idx - 80)
            break
    return normalized[start : start + max_len]


def set_status(paths: HubPaths, rel_path: str, status: str) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"invalid status: {status}")
    rel_path = normalize_rel_path(rel_path)
    absolute = ensure_inside(paths.data_dir, paths.data_dir / rel_path)
    if absolute.exists():
        absolute.write_text(set_content_status(absolute.read_text(encoding="utf-8"), status), encoding="utf-8")
    with connect(paths) as conn:
        conn.execute("UPDATE documents SET status = ?, updated_at = ? WHERE path = ?", (status, utc_now(), rel_path))
        conn.commit()
        row = conn.execute("SELECT * FROM documents WHERE path = ?", (rel_path,)).fetchone()
        if not row:
            raise FileNotFoundError(rel_path)
        return row_to_dict(row)


def delete_document(paths: HubPaths, rel_path: str, *, hard: bool = False) -> dict[str, Any]:
    rel_path = normalize_rel_path(rel_path)
    if not hard:
        return set_status(paths, rel_path, "archived")
    absolute = ensure_inside(paths.data_dir, paths.data_dir / rel_path)
    if absolute.exists():
        absolute.unlink()
    with connect(paths) as conn:
        conn.execute("DELETE FROM documents WHERE path = ?", (rel_path,))
        conn.commit()
    return {"path": rel_path, "deleted": True}
