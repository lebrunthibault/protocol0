# Integrating a third-party Ableton extension with Protocol0

> **Audience:** a developer (or their AI assistant) building an
> [Ableton Extensions SDK](https://www.ableton.com/) extension who wants its
> actions to be **bindable to keyboard shortcuts** through Protocol0.
>
> This page is the **contract**. It is HTTP + JSON only — no Protocol0 code runs
> inside your extension, and you can implement it in any language/runtime, not just
> the SDK. A TypeScript helper (`@protocol0/sdk`) exists to do all of this for you,
> but it is optional sugar over what is described here.

## What you get

Protocol0 runs a global keyboard hook. If your extension exposes its actions to
Protocol0, the user can bind any key combo to one of your actions in the Protocol0
keymapper UI. When they press the combo, Protocol0 calls your action over localhost
HTTP — even when Ableton's window is not focused.

## The model in one diagram

```
Your extension (Ableton Extension Host, sandboxed)
   on activate():
     1. start an HTTP server on 127.0.0.1:<your-port>
        → it must serve  GET /openapi.json   (format below)
        → it must serve  POST /action/<your-name>/<action>   (your handlers)
     2. announce yourself to Protocol0's agent (one outbound fetch):
        POST http://localhost:9010/api/extensions/register
             { "name": "<your-name>", "script_url": "http://127.0.0.1:<your-port>" }
   on shutdown():
     POST http://localhost:9010/api/extensions/unregister  { "name": "<your-name>" }

Protocol0 agent (port 9010)
   - remembers you, then pulls your /openapi.json
   - merges your actions into the keymapper
   - on keypress, POSTs to  http://127.0.0.1:<your-port>/action/<your-name>/<action>
```

**Why announce by HTTP and not by a shared file?** Extensions are sandboxed: the
SDK only lets you write to your own `storageDirectory` / `tempDirectory`, which
Protocol0 cannot read. Writing to a shared path works in the current beta but is
*"unsupported and will likely break"* once the stricter sandbox ships. An **outbound
`fetch`** is the one channel the sandbox fully supports — so that is how you
register. (Inbound HTTP servers are unrestricted, which is why serving
`/openapi.json` is fine.)

## Step 1 — Serve `GET /openapi.json`

Protocol0 reads a minimal subset of OpenAPI 3.1. For **each action**, emit one path
under `/action/<your-name>/<action-name>` with a `post` operation. Only paths
starting with `/action/` are considered — anything else is ignored.

```json
{
  "openapi": "3.1.0",
  "info": { "title": "my-extension", "version": "1.0.0" },
  "paths": {
    "/action/my-extension/randomize_colors": {
      "post": {
        "summary": "Randomize the colors of all clips in the set.",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": { "seed": { "type": "integer" } },
                "required": ["seed"]
              }
            }
          }
        },
        "responses": { "200": { "description": "OK" } }
      }
    }
  }
}
```

How Protocol0 maps this into the keymapper (exactly what its catalog parser reads):

| OpenAPI field | Becomes |
|---|---|
| last path segment (`randomize_colors`) | the action **name** |
| name in Title Case (`Randomize Colors`) | the **label** shown in the UI |
| `summary` (first docstring line) | the action **description** |
| `requestBody` JSON-schema `properties` | the action **params** (`{name, type, required}`) |

Supported param types: `string`, `integer`, `number`, `boolean`. An action with no
params just omits `requestBody`.

## Step 2 — Serve your action handlers

For each advertised action, accept `POST /action/<your-name>/<action-name>` with a
JSON body matching the params you declared, run your logic, and reply `200`.

```ts
// pseudo, plain Node http
if (req.method === "POST" && url.pathname === "/action/my-extension/randomize_colors") {
  const { seed } = JSON.parse(body || "{}");
  await context.withinTransaction(() => { /* ... mutate the Live set ... */ });
  return json(200, { ok: true });
}
```

> **Crash safety (learned the hard way):** an uncaught exception **kills the whole
> Extension Host**. Wrap every handler in try/catch and add
> `process.on("uncaughtException", …)` / `unhandledRejection`. Also, web globals like
> `URL` are not on `globalThis` in the host runtime — import from `node:url`.

## Step 3 — Register and unregister

```ts
// on activate, after your server is listening:
await fetch("http://localhost:9010/api/extensions/register", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ name: "my-extension", script_url: `http://127.0.0.1:${port}` }),
}).catch(() => { /* agent not running yet — harmless, re-register later or rely on retry */ });

// on shutdown:
process.on("exit", () => { /* best-effort unregister */ });
```

Registration is **idempotent and soft state**: re-registering with the same `name`
replaces your URL. If your extension dies without unregistering, Protocol0 prunes
you once your `/openapi.json` stops responding. Re-announce on every `activate()`.

## The `registerCommand` trap

The SDK's context-menu commands receive a selection `Handle` (the clicked clip,
track, …). A **keyboard-triggered** action has **no** such handle — nothing was
clicked. So do **not** blindly expose your context-menu commands as Protocol0
actions: they would be called with no handle. Expose a **separate, explicit set** of
context-free actions for keyboard binding.

## Reference

- The agent endpoints: `POST /api/extensions/register`, `POST /api/extensions/unregister`.
- The catalog parser Protocol0 uses to read your `/openapi.json`:
  `src/agent/src/action_catalog.rs`.
- The validated proof-of-concept extension: `src/js-extension/`.
- Design rationale and milestones:
  `docs/specs/todo/2026-06-04-third-party-extension-integration.md`.
- The optional TypeScript helper that implements all of the above:
  `@protocol0/sdk` (see `src/js-extension/sdk/`).
