from __future__ import annotations

import json
import os


def get_app_links() -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    my_app_url = os.getenv("MEMORYHUB_MY_APP_2_URL", "").strip()
    my_app_label = os.getenv("MEMORYHUB_MY_APP_2_LABEL", "Open my-app-2").strip() or "Open my-app-2"
    if my_app_url:
        links.append({"label": my_app_label, "url": my_app_url})

    disk_url = os.getenv("MEMORYHUB_CLOUD_DISK_URL", "").strip()
    disk_label = os.getenv("MEMORYHUB_CLOUD_DISK_LABEL", "Open cloud disk").strip() or "Open cloud disk"
    if disk_url:
        links.append({"label": disk_label, "url": disk_url})
    return links


def render_index(*, token_required: bool) -> bytes:
    config = {
        "tokenRequired": token_required,
        "links": get_app_links(),
    }
    config_json = json.dumps(config, ensure_ascii=False).replace("</", "<\\/")
    html_body = INDEX_HTML.replace("__MEMORYHUB_CONFIG__", config_json)
    return html_body.encode("utf-8")


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MemoryHub</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f7f4;
      --panel: #ffffff;
      --ink: #1f2523;
      --muted: #64706c;
      --line: #d9ded8;
      --accent: #246b52;
      --accent-2: #c84d31;
      --soft: #edf3ef;
      --code: #101615;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    header {
      border-bottom: 1px solid var(--line);
      background: rgba(255,255,255,.9);
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(10px);
    }
    .bar, main {
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
    }
    .bar {
      min-height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }
    h1 {
      margin: 0;
      font-size: 20px;
      line-height: 1.2;
    }
    .tagline {
      color: var(--muted);
      font-size: 13px;
      margin-top: 4px;
    }
    .links {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: flex-end;
    }
    a.button, button {
      min-height: 36px;
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 8px;
      padding: 8px 12px;
      font: inherit;
      font-size: 14px;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    button.primary {
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }
    button.danger {
      color: var(--accent-2);
      border-color: #e7b6aa;
    }
    main {
      padding: 24px 0 40px;
      display: grid;
      grid-template-columns: 380px minmax(0, 1fr);
      gap: 16px;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      min-width: 0;
    }
    .panel-head {
      padding: 16px;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    h2 {
      margin: 0;
      font-size: 15px;
    }
    .panel-body { padding: 16px; }
    .search-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      margin-bottom: 12px;
    }
    input, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      font: inherit;
      font-size: 14px;
      padding: 10px 11px;
      outline: none;
    }
    input:focus, textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(36,107,82,.12);
    }
    textarea {
      min-height: 420px;
      resize: vertical;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      line-height: 1.55;
      color: var(--code);
    }
    .token-row {
      display: none;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      margin-bottom: 12px;
    }
    .token-row.visible { display: grid; }
    .hint {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
    }
    .list {
      display: grid;
      gap: 8px;
      max-height: calc(100vh - 220px);
      overflow: auto;
      padding-right: 2px;
    }
    .doc {
      width: 100%;
      text-align: left;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 10px;
      cursor: pointer;
    }
    .doc:hover { background: var(--soft); }
    .doc strong {
      display: block;
      font-size: 14px;
      margin-bottom: 4px;
      overflow-wrap: anywhere;
    }
    .doc code {
      display: block;
      font-size: 12px;
      color: var(--muted);
      overflow-wrap: anywhere;
    }
    .doc p {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
    }
    .status {
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      border-radius: 999px;
      background: var(--soft);
      color: var(--accent);
      padding: 2px 8px;
      font-size: 12px;
      margin-top: 8px;
    }
    .editor-grid {
      display: grid;
      gap: 12px;
    }
    .actions {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 8px;
    }
    .left-actions, .right-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .message {
      min-height: 20px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    @media (max-width: 860px) {
      .bar {
        align-items: flex-start;
        flex-direction: column;
        padding: 14px 0;
      }
      .links { justify-content: flex-start; }
      main { grid-template-columns: 1fr; }
      .list { max-height: none; }
      textarea { min-height: 320px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="bar">
      <div>
        <h1>MemoryHub</h1>
        <div class="tagline">Markdown 是正文，SQLite 是索引。Agent 和人都用同一套记忆。</div>
      </div>
      <nav class="links" id="appLinks">
        <a class="button" href="https://github.com/MARDIO1/mardio-memory-hub" target="_blank" rel="noreferrer">GitHub</a>
      </nav>
    </div>
  </header>

  <main>
    <section>
      <div class="panel-head">
        <h2>记忆列表</h2>
        <button id="refreshBtn" type="button">刷新</button>
      </div>
      <div class="panel-body">
        <div class="token-row" id="tokenRow">
          <input id="tokenInput" type="password" placeholder="Bearer token" autocomplete="off" />
          <button id="saveTokenBtn" type="button">保存</button>
        </div>
        <div class="search-row">
          <input id="queryInput" type="search" placeholder="搜索路径、标题、正文..." />
          <button id="searchBtn" class="primary" type="button">搜索</button>
        </div>
        <p class="hint">默认不显示 archived。选择一条记忆后可以读取、修改或归档。</p>
        <div class="list" id="results"></div>
      </div>
    </section>

    <section>
      <div class="panel-head">
        <h2>读取 / 写入</h2>
        <span class="hint" id="selectedMeta">未选择文件</span>
      </div>
      <div class="panel-body editor-grid">
        <input id="pathInput" placeholder="2-projects/example/current.md" />
        <textarea id="contentInput" spellcheck="false" placeholder="在这里写 Markdown 或 JSONL"></textarea>
        <div class="actions">
          <div class="left-actions">
            <button id="newBtn" type="button">新建</button>
            <button id="readBtn" type="button">读取</button>
          </div>
          <div class="right-actions">
            <button id="deleteBtn" class="danger" type="button">归档</button>
            <button id="writeBtn" class="primary" type="button">写入</button>
          </div>
        </div>
        <div class="message" id="message"></div>
      </div>
    </section>
  </main>

  <script id="memoryhub-config" type="application/json">__MEMORYHUB_CONFIG__</script>
  <script>
    const config = JSON.parse(document.getElementById('memoryhub-config').textContent);
    const state = { token: localStorage.getItem('memoryhubToken') || '' };
    const basePath = location.pathname === '/memoryhub' || location.pathname.startsWith('/memoryhub/')
      ? '/memoryhub'
      : '';

    const els = {
      appLinks: document.getElementById('appLinks'),
      tokenRow: document.getElementById('tokenRow'),
      tokenInput: document.getElementById('tokenInput'),
      saveTokenBtn: document.getElementById('saveTokenBtn'),
      queryInput: document.getElementById('queryInput'),
      searchBtn: document.getElementById('searchBtn'),
      refreshBtn: document.getElementById('refreshBtn'),
      results: document.getElementById('results'),
      pathInput: document.getElementById('pathInput'),
      contentInput: document.getElementById('contentInput'),
      selectedMeta: document.getElementById('selectedMeta'),
      newBtn: document.getElementById('newBtn'),
      readBtn: document.getElementById('readBtn'),
      writeBtn: document.getElementById('writeBtn'),
      deleteBtn: document.getElementById('deleteBtn'),
      message: document.getElementById('message'),
    };

    function showMessage(text) {
      els.message.textContent = text || '';
    }

    function headers() {
      const output = { 'Content-Type': 'application/json' };
      if (state.token) output.Authorization = `Bearer ${state.token}`;
      return output;
    }

    async function request(url, options = {}) {
      const response = await fetch(url, { ...options, headers: { ...headers(), ...(options.headers || {}) } });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
      return payload;
    }

    function renderLinks() {
      for (const link of config.links || []) {
        const a = document.createElement('a');
        a.className = 'button';
        a.href = link.url;
        a.textContent = link.label;
        a.target = '_blank';
        a.rel = 'noreferrer';
        els.appLinks.prepend(a);
      }
    }

    function renderResults(results) {
      els.results.innerHTML = '';
      if (!results.length) {
        const empty = document.createElement('p');
        empty.className = 'hint';
        empty.textContent = '没有找到记忆。';
        els.results.appendChild(empty);
        return;
      }
      for (const item of results) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'doc';
        button.innerHTML = `
          <strong></strong>
          <code></code>
          <p></p>
          <span class="status"></span>
        `;
        button.querySelector('strong').textContent = item.title || item.path;
        button.querySelector('code').textContent = item.path;
        button.querySelector('p').textContent = item.snippet || item.summary || '';
        button.querySelector('.status').textContent = `${item.status} / ${item.category}`;
        button.addEventListener('click', () => {
          els.pathInput.value = item.path;
          readCurrent();
        });
        els.results.appendChild(button);
      }
    }

    async function search() {
      const q = encodeURIComponent(els.queryInput.value.trim());
      showMessage('搜索中...');
      const payload = await request(`${basePath}/api/ls?q=${q}`, { headers: { 'Content-Type': 'application/json' } });
      renderResults(payload.results || []);
      showMessage(`找到 ${(payload.results || []).length} 条。`);
    }

    async function readCurrent() {
      const path = els.pathInput.value.trim();
      if (!path) return showMessage('先输入 path。');
      showMessage('读取中...');
      const payload = await request(`${basePath}/api/read?path=${encodeURIComponent(path)}`);
      els.contentInput.value = payload.content || '';
      els.selectedMeta.textContent = payload.document ? `${payload.document.status} / ${payload.document.updated_at}` : path;
      showMessage(`已读取 ${path}`);
    }

    async function writeCurrent() {
      const path = els.pathInput.value.trim();
      if (!path) return showMessage('先输入 path。');
      showMessage('写入中...');
      const payload = await request(`${basePath}/api/write`, {
        method: 'POST',
        body: JSON.stringify({ path, content: els.contentInput.value }),
      });
      els.selectedMeta.textContent = `${payload.document.status} / ${payload.document.updated_at}`;
      showMessage(`已写入 ${payload.document.path}`);
      await search();
    }

    async function deleteCurrent() {
      const path = els.pathInput.value.trim();
      if (!path) return showMessage('先输入 path。');
      if (!confirm(`归档 ${path}？`)) return;
      showMessage('归档中...');
      await request(`${basePath}/api/delete`, {
        method: 'DELETE',
        body: JSON.stringify({ path }),
      });
      showMessage(`已归档 ${path}`);
      await search();
    }

    function newDoc() {
      els.pathInput.value = '2-projects/example/current.md';
      els.contentInput.value = '---\\nstatus: using\\ntags: []\\n---\\n\\n# Current\\n\\n';
      els.selectedMeta.textContent = '新文件';
      showMessage('');
    }

    function initToken() {
      if (!config.tokenRequired) return;
      els.tokenRow.classList.add('visible');
      els.tokenInput.value = state.token;
      els.saveTokenBtn.addEventListener('click', () => {
        state.token = els.tokenInput.value.trim();
        localStorage.setItem('memoryhubToken', state.token);
        showMessage('Token 已保存在当前浏览器。');
        search().catch((error) => showMessage(error.message));
      });
    }

    els.searchBtn.addEventListener('click', () => search().catch((error) => showMessage(error.message)));
    els.refreshBtn.addEventListener('click', () => search().catch((error) => showMessage(error.message)));
    els.queryInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') search().catch((error) => showMessage(error.message));
    });
    els.readBtn.addEventListener('click', () => readCurrent().catch((error) => showMessage(error.message)));
    els.writeBtn.addEventListener('click', () => writeCurrent().catch((error) => showMessage(error.message)));
    els.deleteBtn.addEventListener('click', () => deleteCurrent().catch((error) => showMessage(error.message)));
    els.newBtn.addEventListener('click', newDoc);

    renderLinks();
    initToken();
    search().catch((error) => showMessage(error.message));
  </script>
</body>
</html>
"""
