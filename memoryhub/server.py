from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .core import HubPaths, delete_document, get_paths, init_hub, read_document, search, upsert_document
from .web import render_index


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: object) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def html_response(handler: BaseHTTPRequestHandler, status: int, body: bytes) -> None:
    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("content-length") or "0")
    if length == 0:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def make_handler(paths: HubPaths, token: str | None):
    class MemoryHubHandler(BaseHTTPRequestHandler):
        server_version = "MemoryHub/0.1"

        def log_message(self, format: str, *args) -> None:  # noqa: A002
            if os.getenv("MEMORYHUB_ACCESS_LOG") == "1":
                super().log_message(format, *args)

        def require_auth(self) -> bool:
            if not token:
                return True
            expected = f"Bearer {token}"
            if self.headers.get("authorization") == expected:
                return True
            json_response(self, 401, {"error": "missing or invalid bearer token"})
            return False

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            if parsed.path in {"/", "/app"}:
                trusted_proxy = self.headers.get("x-memoryhub-trusted-proxy") == "1"
                html_response(self, 200, render_index(token_required=bool(token) and not trusted_proxy))
                return
            if not self.require_auth():
                return
            try:
                if parsed.path == "/health":
                    json_response(self, 200, {"ok": True})
                elif parsed.path in {"/api/ls", "/api/search"}:
                    q = query.get("q", [""])[0]
                    json_response(self, 200, {"results": search(paths, q, limit=50)})
                elif parsed.path in {"/api/read", "/api/file"}:
                    rel_path = query.get("path", [""])[0]
                    json_response(self, 200, read_document(paths, rel_path))
                else:
                    json_response(self, 404, {"error": "not found"})
            except Exception as error:  # pragma: no cover
                json_response(self, 400, {"error": str(error)})

        def do_POST(self) -> None:
            if not self.require_auth():
                return
            parsed = urlparse(self.path)
            try:
                body = read_json(self)
                if parsed.path in {"/api/write", "/api/file"}:
                    doc = upsert_document(
                        paths,
                        body["path"],
                        body["content"],
                    )
                    json_response(self, 200, {"ok": True, "document": doc})
                else:
                    json_response(self, 404, {"error": "not found"})
            except Exception as error:
                json_response(self, 400, {"error": str(error)})

        def do_DELETE(self) -> None:
            if not self.require_auth():
                return
            try:
                body = read_json(self)
                if urlparse(self.path).path in {"/api/delete", "/api/file"}:
                    json_response(self, 200, {"ok": True, "result": delete_document(paths, body["path"])})
                else:
                    json_response(self, 404, {"error": "not found"})
            except Exception as error:
                json_response(self, 400, {"error": str(error)})

    return MemoryHubHandler


def run_server(paths: HubPaths, *, host: str | None = None, port: int | None = None, token: str | None = None) -> None:
    init_hub(paths)
    actual_host = host or os.getenv("MEMORYHUB_API_HOST", "127.0.0.1")
    actual_port = int(port or os.getenv("MEMORYHUB_API_PORT", "8765"))
    actual_token = token if token is not None else os.getenv("MEMORYHUB_API_TOKEN")
    httpd = ThreadingHTTPServer((actual_host, actual_port), make_handler(paths, actual_token))
    print(f"MemoryHub API listening on http://{actual_host}:{actual_port}")
    httpd.serve_forever()


def main() -> None:
    run_server(get_paths())


if __name__ == "__main__":
    main()
