/**
 * @protocol0/sdk — PROTOTYPE / ergonomics sketch (layer 2).
 *
 * Optional sugar over the HTTP contract documented in
 * docs/integrations/third-party-extensions.md. A third-party Ableton extension
 * can integrate with Protocol0 WITHOUT this lib by implementing the contract by
 * hand — this file just removes the boilerplate (server, /openapi.json,
 * register/unregister, crash-safety).
 *
 * Status: not published, not built, not wired. It exists to validate the API
 * shape before committing to a real package. See
 * docs/specs/todo/2026-06-04-third-party-extension-integration.md (M3).
 *
 * Design note — the registerCommand trap: a context-menu command receives a
 * selection Handle; a keyboard-triggered action does not. This lib therefore
 * exposes a dedicated `actions` map for context-free, keyboard-bindable actions
 * and deliberately does NOT auto-expose the host's context-menu commands.
 */

import * as http from "node:http";
import { URL } from "node:url"; // not on globalThis inside the Extension Host

const AGENT_REGISTER = "http://localhost:9010/api/extensions/register";
const AGENT_UNREGISTER = "http://localhost:9010/api/extensions/unregister";

/** A JSON-schema-ish param type Protocol0 understands. */
type ParamType = "string" | "integer" | "number" | "boolean";

/** One keyboard-bindable action. */
export interface ActionDef {
  /** One-line summary → becomes the action description/label in the keymapper. */
  summary: string;
  /** Declared params (name → type). Required by default; mark optional explicitly. */
  params?: Record<string, ParamType | { type: ParamType; required?: boolean }>;
  /** Your logic. `args` is the decoded JSON body keyed by param name. */
  handler: (args: Record<string, unknown>) => void | Promise<void>;
}

export interface ExposeOptions {
  /** Unique extension name; namespaces your actions as /action/<name>/<action>. */
  name: string;
  /** The actions to expose for keyboard binding. */
  actions: Record<string, ActionDef>;
  /** Preferred port; falls back to an ephemeral port if taken. Default 0 (ephemeral). */
  port?: number;
}

/** Handle returned by exposeToProtocol0 so the caller can tear down on shutdown. */
export interface Protocol0Handle {
  readonly url: string;
  close(): Promise<void>;
}

/**
 * Start the HTTP server, serve /openapi.json + the action handlers, and announce
 * this extension to Protocol0's agent. Call once from your extension's activate().
 */
export function exposeToProtocol0(opts: ExposeOptions): Promise<Protocol0Handle> {
  const { name, actions } = opts;
  const spec = buildOpenApiSpec(name, actions);

  const server = http.createServer((req, res) => {
    // A thrown error here would kill the whole Extension Host — never let one escape.
    void handleRequest(req, res, name, actions, spec).catch((e) => {
      console.error(`[protocol0] handler error: ${String(e)}`);
      if (!res.headersSent) {
        res.writeHead(500, { "content-type": "application/json" });
        res.end(JSON.stringify({ ok: false, error: String(e) }));
      }
    });
  });

  // Crash nets: the host dies on any uncaught error in this process.
  process.on("uncaughtException", (e) => console.error(`[protocol0] uncaught: ${String(e)}`));
  process.on("unhandledRejection", (e) => console.error(`[protocol0] unhandled: ${String(e)}`));

  return new Promise<Protocol0Handle>((resolve) => {
    server.listen(opts.port ?? 0, "127.0.0.1", () => {
      const addr = server.address();
      const port = typeof addr === "object" && addr ? addr.port : (opts.port ?? 0);
      const url = `http://127.0.0.1:${port}`;
      void announce(AGENT_REGISTER, { name, script_url: url });
      console.log(`[protocol0] "${name}" listening on ${url}, registered with agent`);

      const handle: Protocol0Handle = {
        url,
        async close() {
          await announce(AGENT_UNREGISTER, { name });
          await new Promise<void>((r) => server.close(() => r()));
        },
      };
      // Best-effort unregister if the host exits without calling close().
      process.on("exit", () => void announce(AGENT_UNREGISTER, { name }));
      resolve(handle);
    });
  });
}

// --- internals -------------------------------------------------------------

async function handleRequest(
  req: http.IncomingMessage,
  res: http.ServerResponse,
  name: string,
  actions: Record<string, ActionDef>,
  spec: unknown,
): Promise<void> {
  const json = (code: number, body: unknown) => {
    res.writeHead(code, { "content-type": "application/json" });
    res.end(JSON.stringify(body));
  };

  let url: URL;
  try {
    url = new URL(req.url ?? "/", "http://127.0.0.1");
  } catch {
    return json(400, { ok: false, error: "bad request" });
  }

  if (req.method === "GET" && url.pathname === "/openapi.json") {
    return json(200, spec);
  }

  const prefix = `/action/${name}/`;
  if (req.method === "POST" && url.pathname.startsWith(prefix)) {
    const actionName = url.pathname.slice(prefix.length);
    const action = actions[actionName];
    if (!action) return json(404, { ok: false, error: "unknown action" });

    const raw = await readBody(req);
    let args: Record<string, unknown> = {};
    try {
      args = raw ? (JSON.parse(raw) as Record<string, unknown>) : {};
    } catch {
      return json(400, { ok: false, error: "invalid JSON body" });
    }
    await action.handler(args);
    return json(200, { ok: true });
  }

  return json(404, { ok: false, error: "not found" });
}

function readBody(req: http.IncomingMessage): Promise<string> {
  return new Promise((resolve) => {
    let raw = "";
    req.on("data", (c) => (raw += c));
    req.on("end", () => resolve(raw));
  });
}

/** Build the minimal OpenAPI 3.1 doc Protocol0's action_catalog parser reads. */
function buildOpenApiSpec(name: string, actions: Record<string, ActionDef>): unknown {
  const paths: Record<string, unknown> = {};
  for (const [actionName, def] of Object.entries(actions)) {
    const properties: Record<string, { type: ParamType }> = {};
    const required: string[] = [];
    for (const [pName, pDef] of Object.entries(def.params ?? {})) {
      const type = typeof pDef === "string" ? pDef : pDef.type;
      const isRequired = typeof pDef === "string" ? true : pDef.required !== false;
      properties[pName] = { type };
      if (isRequired) required.push(pName);
    }
    const op: Record<string, unknown> = {
      summary: def.summary,
      responses: { "200": { description: "OK" } },
    };
    if (Object.keys(properties).length > 0) {
      const schema: Record<string, unknown> = { type: "object", properties };
      if (required.length > 0) schema.required = required;
      op.requestBody = {
        required: required.length > 0,
        content: { "application/json": { schema } },
      };
    }
    paths[`/action/${name}/${actionName}`] = { post: op };
  }
  return { openapi: "3.1.0", info: { title: name, version: "1.0.0" }, paths };
}

async function announce(endpoint: string, body: Record<string, unknown>): Promise<void> {
  try {
    await fetch(endpoint, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    // Agent not running (yet) — harmless. The extension still works standalone;
    // Protocol0 just won't know about it until a later re-announce.
  }
}
