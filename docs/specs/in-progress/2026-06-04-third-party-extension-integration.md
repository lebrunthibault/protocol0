# Third-party extension integration

Lets an **external Ableton extension** (built with the Ableton Extensions SDK,
JS/TS) expose its own actions to Protocol0 and receive custom keyboard shortcuts —
the same way a remote-script plugin exposes `@action` methods today, but from a
separate process that Protocol0 does not own.

This is the deliberate next step after `2026-06-03-plugin-api-et-doc.md`, whose
"Hors périmètre" explicitly defers *"Système de plugins tiers/packaging externe"*.
That spec covers plugins that live **inside** the remote-script tree; this one
covers actions that live **outside it**, in a third party's extension.

## Why this is not just "another plugin"

A remote-script plugin runs **in the same Python process** as the HTTP server: the
`PluginLoader` imports it and writes its bound method straight into the `_ROUTES`
registry (`/api/action/<plugin>/<method>`). A third-party Ableton extension runs in
its **own Node.js Extension Host process**, sandboxed, with no shared memory and no
shared registry. The only thing the two processes share is **localhost HTTP**.

So the integration cannot be "register a Python callable". It has to be a **process
boundary contract**: the third party owns its actions and serves them over HTTP;
Protocol0 discovers them and routes keypresses to them.

## The constraint that decides the design: the SDK sandbox

Verified against the SDK docs and the vendored `.d.mts` types
(see memory `sdk-sandbox-pas-encore-appliquee`):

- A sandboxed extension may only write to `context.environment.storageDirectory`
  and `tempDirectory` — **per-extension, runtime-provided, undocumented paths**.
  They are **not shared**, so Protocol0 cannot read a registry an extension drops
  there.
- Writing to an arbitrary shared path (e.g. `%APPDATA%\Protocol0\runtime.json`)
  works **today** only because *"a stricter OS-level sandbox will be introduced in
  the future"* — it is explicitly *"unsupported and will likely break"*. We must
  not bake it into a public contract.
- **Outbound `fetch` is permitted and documented** (*"Call APIs to fetch data…"*).
- **Inbound `http.createServer` has no restriction** (the sandbox targets the
  filesystem, not sockets) — proven by the spike in `src/js-extension/` (Test A).

Therefore the discovery channel **cannot** be a shared file (the runtime.json
pattern used for the script↔agent link). It must be the one channel a sandboxed
extension fully controls: an **outbound HTTP call**.

## Architecture: push to discover, pull to catalog

```
Third-party extension (its own Extension Host, sandboxed)
   │  activate():
   │   1. starts its own HTTP server  →  serves GET /openapi.json  (Protocol0 format)
   │   2. POST http://localhost:9010/api/extensions/register {name, script_url}   ── outbound fetch
   ▼
Agent (:9010, NOT sandboxed — owns the registry)
   │   keeps an in-memory registry { name → {script_url, last_seen} }
   │   pulls each registered /openapi.json (reuses action_catalog.fetch, 1→N)
   │   merges third-party actions into GET /api/actions
   ▼
Keymapper SPA  →  binds a key to a third-party action
Keypress       →  script_client routes the POST to that extension's script_url
```

Two halves, each on a proven mechanism:

- **Push for discovery** — the only thing the sandbox allows: an outbound `fetch`
  that announces *"I exist, here is my URL"*. No shared file.
- **Pull for the catalog** — exactly today's agent→script flow, generalized from
  one source to N. `action_catalog.fetch(url + "/openapi.json")` is reused
  unchanged; it already parses the `/action/<plugin>/<method>` shape.

The registry lives on the **agent (:9010)**, which is a normal external process and
can hold state freely. Nothing new is needed in the Python remote script.

## The contract (layer 1 — source of truth)

A third-party extension is Protocol0-compatible iff it does **both**:

1. **Serves `GET /openapi.json`** on its own localhost port, listing its actions as
   OpenAPI paths under `/action/<extension-name>/<action-name>`, with the same
   param schema convention the script uses (typed `requestBody` properties → action
   params). This is the format `action_catalog.fetch` already consumes.
2. **Registers on startup** via `POST http://localhost:9010/api/extensions/register`
   with `{ "name": "<extension-name>", "script_url": "http://127.0.0.1:<port>" }`,
   and **unregisters on shutdown** via `POST /api/extensions/unregister {name}`
   (best-effort; the agent also expires stale entries — see liveness).

The contract is **HTTP + JSON only** — language- and runtime-agnostic. The SDK lib
(layer 2) is sugar over it, never a requirement.

### Liveness / cleanup

The extension dies with Live and may not get a chance to unregister cleanly. The
agent therefore treats registration as **soft state**:

- On each pull, if an extension's `/openapi.json` is unreachable, mark it stale.
- Drop entries not seen for `N` consecutive pulls (TTL), or whose port refuses
  connection. (Mirrors how the agent already tolerates the script being down →
  empty catalog.)
- Re-registration is idempotent: same `name` → replace `script_url` + reset TTL.

## Action routing on keypress

`script_client.execute(binding)` currently resolves a single base URL (the script
via runtime.json) and POSTs `/api/action/...`. It must learn that an action can
belong to **either** the script **or** a registered extension:

- The merged catalog tags each action with its **owner URL** (script vs which
  extension).
- On keypress, route the POST to the owner's `script_url`, not always the script's.

This is the only change to the keypress path; everything upstream (shortcut store,
listener, SPA) is owner-agnostic.

## The `registerCommand` trap (for the SDK lib, layer 2)

An SDK `command` triggered by a **context menu** receives a selection `Handle`
(e.g. the clicked `AudioClip`). An action triggered by a **global keyboard
shortcut** has **no** such handle — nothing was clicked. So the lib must **not**
transparently expose every `registerCommand` as a Protocol0 action: those that
expect a handle would receive nothing. Use an **explicit opt-in** for
context-free, keyboard-triggerable actions (e.g. a dedicated `actions: {...}` map),
distinct from handle-bound context-menu commands.

## Milestones

### M1 — Agent registry + merged catalog
- `agent/extension_registry.py` (new) — in-memory `{name → {script_url, last_seen}}`,
  `register`, `unregister`, `prune`, `urls()`.
- `agent/web/api.py` — `POST /api/extensions/register` + `/unregister`; `/api/actions`
  merges `action_catalog.fetch` over **script + every registered extension**, each
  action tagged with its owner URL.
- `agent/script_client.py` — route the keypress POST to the action's owner URL.

### M2 — Reference third-party extension
- A minimal standalone extension (its own folder / repo example, **not** under the
  script tree) that implements the layer-1 contract by hand: own HTTP server,
  `/openapi.json`, register/unregister via fetch. Proves the contract without the
  lib. Builds on the existing `src/js-extension/` spike.

### M3 — Layer 2: `@protocol0/sdk` (TS helper) — *optional, gated on a real integrator*
- `exposeToProtocol0(context, { name, actions })` that starts the server, generates
  `/openapi.json`, registers/unregisters, and wraps handlers in try/catch (the
  anti-crash-host net the spike learned the hard way). Sugar over layer 1.
- Do **not** make it the only path — keep layer 1 usable from any language.

### M4 — Layer 3: AI-ready integration doc
- `docs/integrations/third-party-extensions.md` — the layer-1 contract written so a
  third-party dev's AI can implement it: endpoints, JSON shapes, the sandbox
  rationale, a full worked example, the `registerCommand` trap. Linked from
  `README.md` and the website docs.

## Risks

1. **Sandbox tightens and breaks outbound fetch.** Low: fetch is explicitly
   supported; it's the *filesystem* that tightens. Inbound server is the riskier
   bet but the spike already validated it.
2. **Port collisions between extensions.** Each extension picks its own ephemeral
   port and reports the real one at register time (like the script's runtime.json
   fallback). The registry keys on `name`, not port.
3. **A malicious/buggy extension registers garbage.** The agent only ever *pulls*
   and *POSTs to* localhost URLs the extension advertised; a bad `/openapi.json`
   just yields no usable actions. No code from the extension runs in Protocol0.
4. **Action name collisions** (two extensions expose `load_device`). The owner-URL
   tag disambiguates routing; the SPA shows the owning extension name. Catalog keys
   become `(owner, name)`.

## Out of scope

- Auth between processes (all localhost, single-user machine — same trust model as
  the existing script↔agent link).
- Packaging/distribution of third-party extensions (`.ablx` is Ableton's job).
- Exposing the agent registry to the Python script — the script stays unaware;
  aggregation is the agent's responsibility.
