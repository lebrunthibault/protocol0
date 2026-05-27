# Constitution — Protocol0 Keyboard Shortcut Manager

> This document describes the **vision** and **guiding principles** of a
> keyboard shortcut manager for Ableton Live, built on top of the Protocol0
> remote script. It describes the long-term *what* and *why*, not the *how* of
> any given iteration. Concrete iterations live in `docs/specs/` (see
> `docs/specs/README.md`).
>
> When a decision in this document is invalidated by the implementation, update
> this document — it must remain the source of truth for the intent.

## 1. Vision

Replace — or go beyond — Ableton Live's native keyboard shortcut manager with a
programmable, configurable, and **set-independent** system.

The end goal: trigger a wide range of intelligent actions in Live from the
keyboard — track selection, loading devices **by name**, and more generally any
functionality exposed by the Live API (LOM) — through shortcuts that you
configure yourself, in a dedicated interface.

### Why not just use Ableton's native manager

Live's native key mapping is too limited on two axes:

1. **Actions are too poor.** It can't perform "intelligent", parameterized
   actions like *loading a device by its name*. We want rich, configurable
   actions, not just a fixed set of predefined commands.
2. **Shortcuts are tied to the set.** Native shortcuts are attached to a given
   set. We want the opposite: **the same shortcuts everywhere**, whatever
   project is open — exactly like in a code editor where `Ctrl+P` is the same
   regardless of which repo is open.

### Target mental model

```
  [ key pressed ]
        │
        ▼
  key detection  ──►  binding resolution  ──►  action  ──►  Live API (LOM)
   (global hook)      (global config)        (parameterized)
```

- **Key detection**: a global hook captures key combinations whether or not
  Live has focus, depending on the desired scope.
- **Binding resolution**: look up, in a **global configuration**
  (machine/user level, not set level), which action is bound to the captured
  combination.
- **Action**: a named, parameterizable unit (e.g. `load_device(name=…)`,
  `select_track(name=…)`). The catalog of available actions is **exposed** and
  **discoverable** from the configuration frontend.
- **Live API**: the action runs through the Ableton API, on the Live thread.

## 2. Current state (starting point)

The current system routes shortcuts through **AutoHotkey**:

```
  AHK (mappings.ahk)  ──HTTP GET──►  remote script :9000  ──►  Live API
```

`mappings.ahk` binds combinations (`^!e`, `~^+k`, …) to HTTP calls against the
API the remote script already exposes on `127.0.0.1:9000`
(e.g. `GET /device/load?name=EQ Eight`, `GET /track/select?name=kick`).

This existing setup already validates the rightmost end of the chain — *actions
over HTTP already work*. What's missing is:

- **detection** of shortcuts without depending on AHK;
- **configuration** of bindings through a UI, instead of editing
  `mappings.ahk`;

### Reusable building blocks

- **The script's HTTP server** (`src/script/protocol0/application/http/`): stdlib
  router (`@route`), thread-safe bridge to the Live thread via a `queue.Queue`
  drained on every tick (`HttpServer._drain`). This is the foundation for
  exposing new routes (action catalog, config, frontend).
- **The plugin system** (`src/script/protocol0/application/plugin/`):
  `PluginInterface` (`should_start` / `start` / `stop`) auto-discovered by
  `PluginLoader`. A shortcut manager is a natural candidate to be a plugin —
  cleanly startable/stoppable with the script's lifecycle.
- **Device loading** (`DeviceService.load_device`, `BrowserLoaderService`):
  already functional, it's the first target action.

## 3. Architecture decisions

These decisions shape the first iteration. They are made to **test a
hypothesis** (see §4), and are revisable if the hypothesis is invalidated.

### 3.1 Key detection lives in the remote script

The global keyboard hook is installed **by the remote script itself**, inside
Ableton's Python environment — not by AHK nor by an external service.

**Why.** The distribution goal is to be able to **release the script only** if
it proves capable of carrying everything on its own (see §4). Putting detection
in the script is the way to directly test that autonomy.

**Accepted risk.** Live's Python environment is constrained, and a poorly
managed global keyboard hook can disrupt Live (tick latency, key stealing,
interference with native shortcuts). The hook must therefore:

- never block the Live thread (reuse the `submit()` → tick-drain bridge,
  exactly as the HTTP server already does);
- be cleanly installed/uninstalled via a plugin's lifecycle (`start` / `stop`),
  to survive script reloads without leaking a hook;
- stay neutral toward keys it doesn't handle (not consume them).

**AHK becomes legacy.** `mappings.ahk` remains a documented fallback as long as
the native solution isn't proven, but the target is to **drop AHK**.

### 3.2 The configuration frontend is served by the script

The shortcut configuration interface is a **web UI served by the remote
script** on port `9000` (the same one that already serves the HTML index of
routes). It allows the user to:

1. enter a key combination;
2. choose an action from the **list of available actions** (catalog exposed by
   the script);
3. parameterize the action (e.g. the name of the device to load);
4. persist the binding in the global configuration.

**Why the script and not the backend.** Same reason as §3.1: we're testing
whether the script can be the single artifact to distribute. Serving the
frontend from the script keeps everything in a single process for this
evaluation phase.

**Accepted cost.** This adds weight to the Ableton environment (serving web
assets from the script) and will need to be re-evaluated at packaging time.

### 3.3 Binding configuration is global

Shortcut → action bindings are stored in **a single configuration at the
machine/user level**, identical across all sets. Shortcuts are never attached to
a set.

**Why.** This is the core value over the native manager: *the same shortcuts
everywhere*.

### 3.4 Actions form a discoverable catalog

An **action** is a named, parameterizable, self-described unit (name, label,
expected parameters and their types). The frontend reads this catalog to offer
configurable actions; it must not hard-code them.

The existing HTTP routes (`/device/load`, `/track/select`, …) prefigure this
catalog: each action is, or builds on, a functionality exposed by the Live API.

## 4. Hypothesis to validate: "script-only"

The cross-cutting guideline behind all the decisions above is to **test whether
the remote script alone** can carry the whole thing:

> key detection **+** configuration frontend **+** action execution, all in a
> single distributable artifact.

If the hypothesis holds, distribution simplifies radically: **a single binary /
single installer**, with no mandatory AHK or backend.

If the hypothesis is invalidated (unstable keyboard hook in the Live env,
frontend too heavy to serve from the script, blocking thread constraints, …),
the fallback plan is to **move key detection and/or the frontend into a
background service** — either the existing backend (`:9001`, already packaged as
a Scheduled Task), or a dedicated service. The architecture must keep this
switch cheap: detection and execution are already decoupled over HTTP.

## 5. Distribution target

The project must eventually be **packaged as an installable binary** for users
(not merely runnable from sources). Design consequences to keep in mind without
implementing them prematurely:

- the global configuration must live at a stable, documented user location (not
  inside the source tree);
- installation must place the remote script at the right location for Live and,
  if needed (fallback plan §4), register the background service;
- the script's dependencies must remain compatible with Live's constrained
  Python environment (cf. `src/script/pyproject.toml`: stdlib + a minimum of
  lightweight deps).

## 6. Scope of the first iteration (prototype)

> Implementation details will be decided in a dedicated spec (`docs/specs/`).
> What follows only bounds the ambition of the first cut.

First end-to-end action: **load a device by name** through a shortcut configured
in the frontend.

This exercises the whole chain in a minimal version:

- native key detection in the script (§3.1);
- a minimal frontend served by the script (§3.2) to enter "key combination →
  `load_device(name=…)`";
- a persisted global configuration (§3.3);
- execution via the existing `load_device` action (§3.4).

Out of scope for the prototype (but within the vision): the full action catalog,
final binary packaging, fully replacing AHK.

## 7. Guiding principles

- **Never block the Live thread.** Every captured event (keyboard, HTTP)
  crosses the boundary to the Live thread through the tick-drained queue. No
  direct call to the Live API from a daemon thread.
- **Discoverable over hard-coded.** The frontend discovers actions; we don't
  scatter the action list across the UI code.
- **Decoupled capture / execution.** The HTTP boundary between "what detects"
  and "what acts" stays clean, to keep the fallback plan (§4) cheap.
- **The set does not own the shortcuts.** Config is global by default (§3.3).
- **Iterate behind specs.** Every evolution goes through `docs/specs/`; this
  document only describes the durable intent.
