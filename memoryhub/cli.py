from __future__ import annotations

import argparse
import json
import sys

from .core import delete_document, get_paths, init_hub, list_documents, read_document, search, upsert_document


def print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def read_stdin_or_arg(content: str | None) -> str:
    if content is not None:
        return content
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("content is required: memoryhub write <path> <content> or pipe stdin")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="memoryhub")
    parser.add_argument("--data-dir", default=None, help="MemoryHub data directory")
    parser.add_argument("--db-path", default=None, help="SQLite index path")
    sub = parser.add_subparsers(dest="command", required=True)

    ls_cmd = sub.add_parser("ls", help="List/search memory files")
    ls_cmd.add_argument("query", nargs="?", default="", help="Optional keyword query")
    ls_cmd.add_argument("--json", action="store_true")

    read_cmd = sub.add_parser("read", help="Read one memory file")
    read_cmd.add_argument("path")
    read_cmd.add_argument("--json", action="store_true")

    write_cmd = sub.add_parser("write", help="Write one memory file")
    write_cmd.add_argument("path")
    write_cmd.add_argument("content", nargs="?")
    write_cmd.add_argument("--json", action="store_true")

    delete_cmd = sub.add_parser("delete", help="Archive one memory file")
    delete_cmd.add_argument("path")
    delete_cmd.add_argument("--json", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    paths = get_paths(args.data_dir, args.db_path)
    init_hub(paths)

    if args.command == "ls":
        rows = search(paths, args.query, limit=50) if args.query else list_documents(paths)
        if args.json:
            print_json(rows)
            return
        for item in rows:
            print(f"[{item['status']}] {item['path']} :: {item['title']}")
            if args.query and item.get("snippet"):
                print(f"  {item['snippet']}")
    elif args.command == "read":
        result = read_document(paths, args.path)
        if args.json:
            print_json(result)
        else:
            print(result["content"])
    elif args.command == "write":
        result = upsert_document(paths, args.path, read_stdin_or_arg(args.content))
        if args.json:
            print_json(result)
        else:
            print(f"wrote {result['path']} [{result['status']}]")
    elif args.command == "delete":
        result = delete_document(paths, args.path)
        if args.json:
            print_json(result)
        else:
            print(f"archived {result['path']}")


if __name__ == "__main__":
    main()
