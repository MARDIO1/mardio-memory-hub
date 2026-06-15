import json
from pathlib import Path
from typing import Any
from urllib.parse import quote

import aiohttp
from astrbot.api import llm_tool, star
from astrbot.api.event import AstrMessageEvent, MessageEventResult, filter

CONFIG_PATH = Path("/AstrBot/data/agent-memory/config.json")


class Main(star.Star):
    def __init__(self, context: star.Context) -> None:
        super().__init__(context)
        self.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

    async def _request(self, method: str, route: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        base_url = self.config["base_url"].rstrip("/")
        headers = {"Content-Type": "application/json"}
        if self.config.get("token"):
            headers["Authorization"] = f"Bearer {self.config['token']}"
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.request(method, f"{base_url}{route}", json=payload, headers=headers, timeout=8) as response:
                data = await response.json()
                if response.status >= 400:
                    raise RuntimeError(f"MemoryHub API failed: {response.status} {data}")
                return data

    def _reply(self, event: AstrMessageEvent, text: str) -> None:
        event.set_result(MessageEventResult().message(text).use_t2i(False))

    def _format_ls(self, data: dict[str, Any]) -> str:
        lines = []
        for item in data.get("results", []):
            lines.append(f"[{item['status']}] {item['path']} :: {item['title']}\n{item.get('snippet', '')}")
        return "\n\n".join(lines) or "No memory matched."

    @filter.command("mem_ls")
    async def mem_ls(self, event: AstrMessageEvent, query: str = "") -> None:
        data = await self._request("GET", f"/api/ls?q={quote(query)}")
        self._reply(event, self._format_ls(data))

    @filter.command("mem_read")
    async def mem_read(self, event: AstrMessageEvent, path: str = "") -> None:
        if not path:
            self._reply(event, "Usage: /mem_read <path>")
            return
        data = await self._request("GET", f"/api/read?path={quote(path)}")
        self._reply(event, data.get("content", "")[:1800])

    @filter.command("mem_write")
    async def mem_write(self, event: AstrMessageEvent) -> None:
        raw = event.message_str.strip()
        for prefix in ("/mem_write", "mem_write"):
            if raw.startswith(prefix):
                raw = raw[len(prefix):].strip()
                break
        if "|" not in raw:
            self._reply(event, "Usage: /mem_write <path> | <markdown>")
            return
        rel_path, content = [part.strip() for part in raw.split("|", 1)]
        data = await self._request("POST", "/api/write", {"path": rel_path, "content": content})
        self._reply(event, f"Wrote: {data.get('document', {}).get('path')}")

    @filter.command("mem_delete")
    async def mem_delete(self, event: AstrMessageEvent, path: str = "") -> None:
        if not path:
            self._reply(event, "Usage: /mem_delete <path>")
            return
        data = await self._request("DELETE", "/api/delete", {"path": path, "hard": True})
        self._reply(event, f"Deleted: {data.get('result', {}).get('path')}")

    @llm_tool(name="agent_memory_ls")
    async def agent_memory_ls(self, event: AstrMessageEvent, query: str = "") -> str:
        """List/search MemoryHub records.

        Args:
            query(string): Optional search keywords.
        """
        return json.dumps(await self._request("GET", f"/api/ls?q={quote(query)}"), ensure_ascii=False)

    @llm_tool(name="agent_memory_read")
    async def agent_memory_read(self, event: AstrMessageEvent, path: str) -> str:
        """Read one MemoryHub file.

        Args:
            path(string): MemoryHub file path.
        """
        return json.dumps(await self._request("GET", f"/api/read?path={quote(path)}"), ensure_ascii=False)

    @llm_tool(name="agent_memory_write")
    async def agent_memory_write(self, event: AstrMessageEvent, path: str, content: str) -> str:
        """Write one MemoryHub file.

        Args:
            path(string): MemoryHub file path.
            content(string): Markdown or jsonl content.
        """
        return json.dumps(await self._request("POST", "/api/write", {"path": path, "content": content}), ensure_ascii=False)

    @llm_tool(name="agent_memory_delete")
    async def agent_memory_delete(self, event: AstrMessageEvent, path: str) -> str:
        """Permanently delete one MemoryHub file.

        Args:
            path(string): MemoryHub file path.
        """
        return json.dumps(await self._request("DELETE", "/api/delete", {"path": path, "hard": True}), ensure_ascii=False)
