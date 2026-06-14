from __future__ import annotations

import json
import os


def get_app_links() -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    my_app_url = os.getenv("MEMORYHUB_MY_APP_2_URL", "").strip()
    my_app_label = os.getenv("MEMORYHUB_MY_APP_2_LABEL", "my-app-2 后台").strip() or "my-app-2 后台"
    if my_app_url:
        links.append({"label": my_app_label, "url": my_app_url})

    disk_url = os.getenv("MEMORYHUB_CLOUD_DISK_URL", "").strip()
    disk_label = os.getenv("MEMORYHUB_CLOUD_DISK_LABEL", "云盘").strip() or "云盘"
    if disk_url:
        links.append({"label": disk_label, "url": disk_url})
    return links


def render_index(*, token_required: bool) -> bytes:
    config = {
        "tokenRequired": token_required,
        "links": get_app_links(),
    }
    config_json = json.dumps(config, ensure_ascii=False).replace("</", "<\\/")
    return INDEX_HTML.replace("__MEMORYHUB_CONFIG__", config_json).encode("utf-8")


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MemoryHub</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f4f4f5;
      --panel: #ffffff;
      --panel-soft: #fafafa;
      --ink: #09090b;
      --muted: #71717a;
      --line: rgba(0,0,0,.10);
      --line-strong: rgba(0,0,0,.16);
      --hover: #f1f5f9;
      --selected: #e4e4e7;
      --danger: #b42318;
      --accent: #18181b;
      --shadow: 0 1px 2px rgba(0,0,0,.05);
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    button, input, textarea {
      font: inherit;
      letter-spacing: 0;
    }
    button {
      cursor: pointer;
      border: 0;
      background: none;
      color: inherit;
    }
    .shell {
      height: 100dvh;
      display: flex;
      flex-direction: column;
      background: #f7f7f8;
    }
    .topbar {
      position: relative;
      z-index: 5;
      flex-shrink: 0;
      min-height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      border-bottom: 1px solid var(--line);
      background: #fff;
      padding: 0 24px;
      box-shadow: var(--shadow);
    }
    .brand {
      display: flex;
      align-items: baseline;
      gap: 12px;
      min-width: 0;
    }
    h1 {
      margin: 0;
      font-size: 20px;
      line-height: 1;
      font-weight: 700;
    }
    .eyebrow {
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: .14em;
      white-space: nowrap;
    }
    .top-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    .button, .top-actions a {
      min-height: 34px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      padding: 7px 12px;
      color: var(--ink);
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      transition: background .15s ease, color .15s ease, border-color .15s ease;
    }
    .button:hover, .top-actions a:hover { background: #18181b; border-color: #18181b; color: #fff; }
    .button.primary { background: #18181b; border-color: #18181b; color: #fff; }
    .button.primary:hover { background: #27272a; }
    .button.danger { color: var(--danger); border-color: #efc6bf; }
    .button.danger:hover { background: #fee4df; color: var(--danger); border-color: #efc6bf; }
    .workspace {
      flex: 1;
      min-height: 0;
      padding: 16px 24px 24px;
      display: flex;
      overflow: hidden;
    }
    .browser {
      width: min(1600px, 100%);
      margin: 0 auto;
      display: grid;
      grid-template-columns: 250px minmax(300px, 1fr) minmax(420px, 48%);
      min-height: 0;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fff;
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    aside {
      min-width: 0;
      border-right: 1px solid var(--line);
      background: #fafafa;
      display: flex;
      flex-direction: column;
    }
    .side-title {
      flex-shrink: 0;
      padding: 14px 16px 10px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: .12em;
      text-transform: uppercase;
    }
    .category-list {
      padding: 0 8px;
      display: grid;
      gap: 4px;
      overflow: auto;
    }
    .category {
      width: 100%;
      display: flex;
      align-items: center;
      gap: 10px;
      border-radius: 8px;
      padding: 10px;
      color: #52525b;
      text-align: left;
      font-size: 14px;
    }
    .category:hover { background: #f1f5f9; }
    .category.active {
      background: var(--selected);
      color: #111827;
      font-weight: 600;
    }
    .category svg {
      width: 18px;
      height: 18px;
      opacity: .72;
      flex: 0 0 auto;
    }
    .side-info {
      margin-top: auto;
      border-top: 1px solid var(--line);
      padding: 14px 16px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.55;
    }
    .list-pane {
      min-width: 0;
      border-right: 1px solid var(--line);
      display: flex;
      flex-direction: column;
      background: #fff;
    }
    .pane-head {
      min-height: 64px;
      flex-shrink: 0;
      border-bottom: 1px solid var(--line);
      padding: 12px 14px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
    }
    .search {
      height: 38px;
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      padding: 0 11px;
      outline: none;
      font-size: 14px;
    }
    .search:focus, .path-input:focus, textarea:focus {
      border-color: var(--line-strong);
      box-shadow: 0 0 0 3px rgba(24,24,27,.08);
    }
    .file-list {
      flex: 1;
      min-height: 0;
      overflow: auto;
      padding: 8px;
    }
    .file-row {
      width: 100%;
      display: grid;
      grid-template-columns: 28px minmax(0, 1fr);
      gap: 10px;
      align-items: start;
      border-radius: 10px;
      padding: 10px;
      text-align: left;
    }
    .file-row:hover { background: var(--hover); }
    .file-row.active { background: var(--selected); }
    .file-icon {
      width: 28px;
      height: 28px;
      border-radius: 7px;
      display: grid;
      place-items: center;
      background: #f4f4f5;
      color: #52525b;
      font-size: 12px;
      font-weight: 700;
    }
    .file-row.active .file-icon { background: #fff; }
    .file-name {
      font-size: 14px;
      font-weight: 600;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }
    .file-path {
      margin-top: 3px;
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 11px;
      overflow-wrap: anywhere;
    }
    .file-summary {
      margin-top: 6px;
      color: #71717a;
      font-size: 12px;
      line-height: 1.45;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    .meta-line {
      margin-top: 7px;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 20px;
      border-radius: 999px;
      background: #f4f4f5;
      color: #52525b;
      padding: 2px 7px;
      font-size: 11px;
      line-height: 1;
    }
    .pill.active { background: #dcfce7; color: #166534; }
    .pill.using { background: #dbeafe; color: #1d4ed8; }
    .pill.archived { background: #fee2e2; color: #991b1b; }
    .editor-pane {
      min-width: 0;
      display: flex;
      flex-direction: column;
      background: #fff;
    }
    .editor-head {
      flex-shrink: 0;
      min-height: 64px;
      border-bottom: 1px solid var(--line);
      padding: 12px 14px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
    }
    .path-input {
      height: 38px;
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0 11px;
      color: var(--ink);
      outline: none;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
    }
    .editor-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    .tabs {
      flex-shrink: 0;
      padding: 8px 14px;
      border-bottom: 1px solid var(--line);
      display: flex;
      gap: 6px;
      align-items: center;
      justify-content: space-between;
    }
    .tab-group {
      display: flex;
      gap: 6px;
    }
    .tab {
      min-height: 30px;
      border-radius: 6px;
      padding: 5px 10px;
      color: #52525b;
      font-size: 13px;
    }
    .tab.active {
      background: #18181b;
      color: #fff;
    }
    .status-text {
      color: var(--muted);
      font-size: 12px;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .editor-body {
      flex: 1;
      min-height: 0;
      display: grid;
    }
    textarea {
      width: 100%;
      height: 100%;
      min-height: 0;
      resize: none;
      border: 0;
      outline: none;
      padding: 18px;
      color: #111827;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      line-height: 1.65;
      background: #fff;
    }
    .preview {
      overflow: auto;
      padding: 22px 26px 40px;
      line-height: 1.7;
      font-size: 14px;
      color: #27272a;
    }
    .preview h1, .preview h2, .preview h3 {
      margin: 1.2em 0 .45em;
      line-height: 1.25;
      color: #09090b;
    }
    .preview h1 { font-size: 26px; }
    .preview h2 { font-size: 20px; border-bottom: 1px solid var(--line); padding-bottom: 6px; }
    .preview h3 { font-size: 16px; }
    .preview p { margin: .65em 0; }
    .preview ul, .preview ol { padding-left: 1.4em; }
    .preview code {
      border-radius: 4px;
      background: #f4f4f5;
      padding: 2px 4px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: .92em;
    }
    .preview pre {
      overflow: auto;
      border-radius: 8px;
      background: #18181b;
      color: #f4f4f5;
      padding: 14px;
    }
    .preview pre code { background: transparent; color: inherit; padding: 0; }
    .empty, .notice {
      padding: 16px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }
    .locked {
      display: none;
      margin: 8px 14px 0;
      border: 1px solid #fde68a;
      border-radius: 8px;
      background: #fffbeb;
      padding: 10px;
      color: #92400e;
      font-size: 12px;
      line-height: 1.55;
    }
    .locked.visible { display: block; }
    .token-inline {
      margin-top: 8px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
    }
    .hidden { display: none !important; }
    @media (max-width: 1120px) {
      .workspace { padding: 0; }
      .browser {
        width: 100%;
        height: 100%;
        border-radius: 0;
        border-left: 0;
        border-right: 0;
        grid-template-columns: 220px minmax(280px, 1fr);
      }
      .editor-pane {
        grid-column: 1 / -1;
        border-top: 1px solid var(--line);
        min-height: 46dvh;
      }
    }
    @media (max-width: 720px) {
      .topbar { align-items: flex-start; flex-direction: column; padding: 14px 16px; }
      .brand { flex-direction: column; align-items: flex-start; gap: 4px; }
      .workspace { overflow: auto; }
      .browser {
        height: auto;
        min-height: 100%;
        display: flex;
        flex-direction: column;
      }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
      .category-list { display: flex; overflow-x: auto; padding-bottom: 8px; }
      .category { width: auto; white-space: nowrap; }
      .side-info { display: none; }
      .list-pane { min-height: 360px; border-right: 0; border-bottom: 1px solid var(--line); }
      .editor-head { grid-template-columns: 1fr; }
      .editor-actions { justify-content: flex-start; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <h1>MemoryHub</h1>
        <span class="eyebrow">Agent Memory Disk</span>
      </div>
      <nav class="top-actions" id="appLinks">
        <a href="https://github.com/MARDIO1/mardio-memory-hub" target="_blank" rel="noreferrer">GitHub</a>
      </nav>
    </header>

    <div class="workspace">
      <div class="browser">
        <aside>
          <div class="side-title">记忆分区</div>
          <div class="category-list" id="categories"></div>
          <div class="side-info">
            Markdown 文件是正文，SQLite 只是索引。这里像云盘一样管理公共记忆，管理员可以读取、预览、手动修改和归档。
          </div>
        </aside>

        <section class="list-pane">
          <div class="pane-head">
            <input id="queryInput" class="search" type="search" placeholder="搜索路径、标题、正文..." />
            <button id="refreshBtn" class="button" type="button">刷新</button>
          </div>
          <div class="locked" id="tokenPanel">
            直连 MemoryHub 服务时需要 bearer token。通过 my-app-2 管理员入口访问时不会显示这个输入框。
            <div class="token-inline">
              <input id="tokenInput" class="search" type="password" placeholder="Bearer token" autocomplete="off" />
              <button id="saveTokenBtn" class="button" type="button">保存</button>
            </div>
          </div>
          <div class="file-list" id="results"></div>
        </section>

        <section class="editor-pane">
          <div class="editor-head">
            <input id="pathInput" class="path-input" placeholder="2-projects/example/current.md" />
            <div class="editor-actions">
              <button id="newBtn" class="button" type="button">新建 .md</button>
              <button id="readBtn" class="button" type="button">读取</button>
              <button id="deleteBtn" class="button danger" type="button">归档</button>
              <button id="writeBtn" class="button primary" type="button">保存修改</button>
            </div>
          </div>
          <div class="tabs">
            <div class="tab-group">
              <button id="previewTab" class="tab active" type="button">预览</button>
              <button id="editTab" class="tab" type="button">编辑</button>
            </div>
            <div id="statusText" class="status-text">未选择文件</div>
          </div>
          <div class="editor-body">
            <textarea id="contentInput" class="hidden" spellcheck="false"></textarea>
            <article id="preview" class="preview">
              <div class="empty">从左侧选择一条 .md 记忆，右侧会显示预览；切到“编辑”后可以手动修改正文。</div>
            </article>
          </div>
        </section>
      </div>
    </div>
  </div>

  <script id="memoryhub-config" type="application/json">__MEMORYHUB_CONFIG__</script>
  <script>
    const config = JSON.parse(document.getElementById('memoryhub-config').textContent);
    const state = {
      token: localStorage.getItem('memoryhubToken') || '',
      category: 'all',
      docs: [],
      current: null,
      mode: 'preview',
    };
    const basePath = location.pathname === '/memoryhub' || location.pathname.startsWith('/memoryhub/')
      ? '/memoryhub'
      : '';
    const categories = [
      ['all', '全部记忆', 'M'],
      ['rules', 'MemoryHub 规则', '0'],
      ['work-rules', '工作规则', '1'],
      ['projects', '项目记忆', '2'],
      ['tools', '工具与 skill', '3'],
      ['misc', '其他', '*'],
    ];
    const els = {
      appLinks: document.getElementById('appLinks'),
      categories: document.getElementById('categories'),
      tokenPanel: document.getElementById('tokenPanel'),
      tokenInput: document.getElementById('tokenInput'),
      saveTokenBtn: document.getElementById('saveTokenBtn'),
      queryInput: document.getElementById('queryInput'),
      refreshBtn: document.getElementById('refreshBtn'),
      results: document.getElementById('results'),
      pathInput: document.getElementById('pathInput'),
      contentInput: document.getElementById('contentInput'),
      preview: document.getElementById('preview'),
      statusText: document.getElementById('statusText'),
      newBtn: document.getElementById('newBtn'),
      readBtn: document.getElementById('readBtn'),
      writeBtn: document.getElementById('writeBtn'),
      deleteBtn: document.getElementById('deleteBtn'),
      previewTab: document.getElementById('previewTab'),
      editTab: document.getElementById('editTab'),
    };

    function authHeaders(json = true) {
      const headers = {};
      if (json) headers['Content-Type'] = 'application/json';
      if (state.token) headers.Authorization = `Bearer ${state.token}`;
      return headers;
    }

    async function request(url, options = {}) {
      const response = await fetch(url, {
        ...options,
        headers: { ...authHeaders(options.json !== false), ...(options.headers || {}) },
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.error || `HTTP ${response.status}`);
      return payload;
    }

    function setStatus(text) {
      els.statusText.textContent = text;
    }

    function renderLinks() {
      for (const link of config.links || []) {
        const a = document.createElement('a');
        a.href = link.url;
        a.textContent = link.label;
        a.rel = 'noreferrer';
        els.appLinks.prepend(a);
      }
    }

    function renderCategories() {
      els.categories.innerHTML = '';
      for (const [id, label, icon] of categories) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = `category ${state.category === id ? 'active' : ''}`;
        button.innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 6.5A2.5 2.5 0 0 1 6.5 4H10l2 2h5.5A2.5 2.5 0 0 1 20 8.5v8A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5v-10Z"/>
          </svg>
          <span></span>
        `;
        button.querySelector('span').textContent = `${icon} ${label}`;
        button.addEventListener('click', () => {
          state.category = id;
          renderCategories();
          renderResults();
        });
        els.categories.appendChild(button);
      }
    }

    function filteredDocs() {
      if (state.category === 'all') return state.docs;
      return state.docs.filter((item) => item.category === state.category);
    }

    function renderResults() {
      const docs = filteredDocs();
      els.results.innerHTML = '';
      if (!docs.length) {
        els.results.innerHTML = '<div class="empty">没有找到记忆。</div>';
        return;
      }
      for (const item of docs) {
        const row = document.createElement('button');
        row.type = 'button';
        row.className = `file-row ${state.current?.path === item.path ? 'active' : ''}`;
        const ext = item.path.endsWith('.jsonl') ? 'JL' : 'MD';
        row.innerHTML = `
          <div class="file-icon"></div>
          <div>
            <div class="file-name"></div>
            <div class="file-path"></div>
            <div class="file-summary"></div>
            <div class="meta-line">
              <span class="pill"></span>
              <span class="pill"></span>
            </div>
          </div>
        `;
        row.querySelector('.file-icon').textContent = ext;
        row.querySelector('.file-name').textContent = item.title || item.path;
        row.querySelector('.file-path').textContent = item.path;
        row.querySelector('.file-summary').textContent = item.snippet || item.summary || '';
        const pills = row.querySelectorAll('.pill');
        pills[0].classList.add(item.status);
        pills[0].textContent = item.status;
        pills[1].textContent = item.category;
        row.addEventListener('click', () => {
          els.pathInput.value = item.path;
          readCurrent();
        });
        els.results.appendChild(row);
      }
    }

    function escapeHtml(value) {
      return value
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
    }

    function inlineMarkdown(value) {
      return escapeHtml(value)
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
    }

    function markdownToHtml(markdown) {
      const lines = markdown.replace(/^---\\n[\\s\\S]*?\\n---\\n?/, '').split('\\n');
      const out = [];
      let inList = false;
      let inCode = false;
      let codeLines = [];
      function closeList() {
        if (inList) {
          out.push('</ul>');
          inList = false;
        }
      }
      function closeCode() {
        if (inCode) {
          out.push(`<pre><code>${escapeHtml(codeLines.join('\\n'))}</code></pre>`);
          codeLines = [];
          inCode = false;
        }
      }
      for (const line of lines) {
        if (line.startsWith('```')) {
          if (inCode) closeCode();
          else {
            closeList();
            inCode = true;
          }
          continue;
        }
        if (inCode) {
          codeLines.push(line);
          continue;
        }
        if (!line.trim()) {
          closeList();
          continue;
        }
        const heading = line.match(/^(#{1,3})\\s+(.*)$/);
        if (heading) {
          closeList();
          out.push(`<h${heading[1].length}>${inlineMarkdown(heading[2])}</h${heading[1].length}>`);
          continue;
        }
        const item = line.match(/^[-*]\\s+(.*)$/);
        if (item) {
          if (!inList) {
            out.push('<ul>');
            inList = true;
          }
          out.push(`<li>${inlineMarkdown(item[1])}</li>`);
          continue;
        }
        closeList();
        out.push(`<p>${inlineMarkdown(line)}</p>`);
      }
      closeCode();
      closeList();
      return out.join('\\n') || '<div class="empty">空文件</div>';
    }

    function refreshPreview() {
      els.preview.innerHTML = markdownToHtml(els.contentInput.value);
    }

    function setMode(mode) {
      state.mode = mode;
      const editing = mode === 'edit';
      els.contentInput.classList.toggle('hidden', !editing);
      els.preview.classList.toggle('hidden', editing);
      els.editTab.classList.toggle('active', editing);
      els.previewTab.classList.toggle('active', !editing);
      if (!editing) refreshPreview();
    }

    async function search() {
      setStatus('正在刷新...');
      const q = encodeURIComponent(els.queryInput.value.trim());
      const payload = await request(`${basePath}/api/ls?q=${q}`, { headers: { 'Content-Type': 'application/json' } });
      state.docs = payload.results || [];
      renderResults();
      setStatus(`共 ${filteredDocs().length} 条`);
    }

    async function readCurrent() {
      const path = els.pathInput.value.trim();
      if (!path) return setStatus('先选择或输入一个路径');
      setStatus('正在读取...');
      const payload = await request(`${basePath}/api/read?path=${encodeURIComponent(path)}`);
      state.current = payload.document;
      els.pathInput.value = payload.document?.path || path;
      els.contentInput.value = payload.content || '';
      refreshPreview();
      setMode('preview');
      renderResults();
      setStatus(`${payload.document?.status || '-'} / ${payload.document?.updated_at || path}`);
    }

    async function writeCurrent() {
      const path = els.pathInput.value.trim();
      if (!path) return setStatus('先输入路径');
      setStatus('正在保存...');
      const payload = await request(`${basePath}/api/write`, {
        method: 'POST',
        body: JSON.stringify({ path, content: els.contentInput.value }),
      });
      state.current = payload.document;
      refreshPreview();
      await search();
      setStatus(`已保存 ${payload.document.path}`);
    }

    async function archiveCurrent() {
      const path = els.pathInput.value.trim();
      if (!path) return setStatus('先选择文件');
      if (!confirm(`归档 ${path}？`)) return;
      setStatus('正在归档...');
      await request(`${basePath}/api/delete`, {
        method: 'DELETE',
        body: JSON.stringify({ path }),
      });
      await search();
      setStatus(`已归档 ${path}`);
    }

    function newDoc() {
      const stamp = new Date().toISOString().slice(0, 10);
      els.pathInput.value = `2-projects/manual-${stamp}.md`;
      els.contentInput.value = '---\\nstatus: using\\ntags: []\\n---\\n\\n# 新记忆\\n\\n';
      state.current = null;
      setMode('edit');
      setStatus('新建 .md 文件');
    }

    function initTokenPanel() {
      if (!config.tokenRequired) return;
      els.tokenPanel.classList.add('visible');
      els.tokenInput.value = state.token;
      els.saveTokenBtn.addEventListener('click', () => {
        state.token = els.tokenInput.value.trim();
        localStorage.setItem('memoryhubToken', state.token);
        search().catch((error) => setStatus(error.message));
      });
    }

    renderLinks();
    renderCategories();
    initTokenPanel();
    els.refreshBtn.addEventListener('click', () => search().catch((error) => setStatus(error.message)));
    els.queryInput.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') search().catch((error) => setStatus(error.message));
    });
    els.previewTab.addEventListener('click', () => setMode('preview'));
    els.editTab.addEventListener('click', () => setMode('edit'));
    els.contentInput.addEventListener('input', () => {
      if (state.mode === 'preview') refreshPreview();
    });
    els.newBtn.addEventListener('click', newDoc);
    els.readBtn.addEventListener('click', () => readCurrent().catch((error) => setStatus(error.message)));
    els.writeBtn.addEventListener('click', () => writeCurrent().catch((error) => setStatus(error.message)));
    els.deleteBtn.addEventListener('click', () => archiveCurrent().catch((error) => setStatus(error.message)));
    search().catch((error) => setStatus(error.message));
  </script>
</body>
</html>
"""
