#!/usr/bin/env node

const baseUrl = (process.env.MEMORYHUB_BASE_URL || "http://127.0.0.1:8765").replace(/\/$/, "");
const token = process.env.MEMORYHUB_API_TOKEN || "";

function usage() {
  console.log(`memoryhub-node:
  ls [query]
  read <path>
  write <path> <content>
  delete <path>`);
}

async function request(method, route, body) {
  const response = await fetch(`${baseUrl}${route}`, {
    method,
    headers: {
      "content-type": "application/json",
      ...(token ? { authorization: `Bearer ${token}` } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(`${method} ${route} failed: ${response.status} ${JSON.stringify(payload)}`);
  }
  return payload;
}

const [command, ...args] = process.argv.slice(2);

try {
  if (!command || command === "help" || command === "--help") {
    usage();
  } else if (command === "ls") {
    const params = new URLSearchParams({ q: args.join(" ") });
    console.log(JSON.stringify(await request("GET", `/api/ls?${params}`), null, 2));
  } else if (command === "read") {
    if (!args[0]) throw new Error("path is required");
    const params = new URLSearchParams({ path: args[0] });
    console.log(JSON.stringify(await request("GET", `/api/read?${params}`), null, 2));
  } else if (command === "write") {
    const [path, ...contentParts] = args;
    if (!path || contentParts.length === 0) throw new Error("path and content are required");
    console.log(JSON.stringify(await request("POST", "/api/write", { path, content: contentParts.join(" ") }), null, 2));
  } else if (command === "delete") {
    if (!args[0]) throw new Error("path is required");
    console.log(JSON.stringify(await request("DELETE", "/api/delete", { path: args[0] }), null, 2));
  } else {
    usage();
    process.exitCode = 2;
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
