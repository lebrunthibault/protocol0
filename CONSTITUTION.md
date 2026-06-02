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

### 3.1 Key detection lives in a local detector process

> **Updated 2026-05-28 — the original decision was invalidated by a spike.**
> The original §3.1 placed the global keyboard hook **inside the remote script**
> (Ableton's Python), to test the "script-only" hypothesis (§4). A prototype
> spike proved this impossible. The original intent — *same shortcuts
> everywhere, configured globally* — is unchanged; only the *where* of detection
> moved. The rest of this section records both the verdict and the new decision.

**Verdict of the spike (NO-GO, in-script detection).** Ableton's embedded Python
cannot host a keyboard hook, for three independent reasons:

1. **No `ctypes`.** Live ships a stripped, statically-linked CPython
   (`win_64_static`): no `ctypes` package, no `_ctypes.pyd`, in fact **no C
   extensions at all** and no `python311.dll`. `import ctypes` →
   `ModuleNotFoundError`. Both candidate implementations (`pynput` and raw
   `ctypes`) depend on it.
2. **Loading a `.pyd` crashes Live.** A stock CPython C-extension links against
   `python311.dll`, which doesn't exist in this static build, so dropping in
   `_ctypes.pyd` doesn't restore it — it crashes the host. No known project has
   ever loaded native code in-process.
3. **No message loop.** Even with `ctypes`, a `WH_KEYBOARD_LL` hook needs the
   installing thread to run a Windows message loop; the remote-script thread is
   tick-driven and has none, so callbacks would never fire.

**New decision.** The global keyboard hook is installed by a **dedicated local
detector process** running under a normal system Python (where `ctypes`/`pynput`
work). It is **separate from the cloud backend** (§5) — detection is intrinsically
local (it runs on the user's machine and watches their keyboard), so it cannot
live in a service meant to run remotely. On a configured combo it resolves the
binding against the global config (§3.3) and calls the script's existing HTTP API
(`:9000`, e.g. `/device/load?name=…`).

**Why a separate process and not the backend.** The backend is a **cloud** service
(§5); the detector must be local. Keeping them as distinct artifacts also means a
crash in one doesn't take down the other.

**Constraints on the detector.**

- stay neutral toward keys it doesn't handle (not consume them);
- only fire when Ableton is the foreground window (a local OS check), so it never
  steals keys from other apps;
- be installable/launchable as a background service so it survives logon;
- keep the capture/execution boundary over HTTP, exactly as today.

**AHK becomes legacy.** `mappings.ahk` remains a documented fallback until the
dedicated detector is proven, but the target is to **drop AHK** in favor of the
configurable detector.

### 3.2 The configuration frontend is served by the script

The shortcut configuration interface is a **web UI served by the remote
script** on port `9000` (the same one that already serves the HTML index of
routes). It allows the user to:

1. enter a key combination;
2. choose an action from the **list of available actions** (catalog exposed by
   the script);
3. parameterize the action (e.g. the name of the device to load);
4. persist the binding in the global configuration.

**Why the script and not the backend.** The backend is a remote cloud service
(§5); the config frontend must be reachable locally and offline, and it reads the
action catalog the script already exposes. Serving it from the script keeps the
configuration experience self-contained, with no dependency on the cloud or on
the local detector being up.

**Accepted cost.** This adds weight to the Ableton environment (serving web
assets from the script) and will need to be re-evaluated at packaging time. Note
that §3.1's in-script detection was invalidated, but §3.2 still holds: serving a
web UI from the script is fine (no `ctypes`/native code needed), unlike a
keyboard hook.

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

## 4. Hypothesis tested: "script-only" — partially invalidated

The original cross-cutting guideline was to **test whether the remote script
alone** could carry the whole thing:

> key detection **+** configuration frontend **+** action execution, all in a
> single distributable artifact.

**Result (2026-05-28).** The hypothesis is **invalidated for key detection**:
Ableton's embedded Python cannot host a keyboard hook (no `ctypes`, `.pyd`
loading crashes Live, no message loop — see §3.1). It **holds for the frontend
and execution**, which the script serves and runs natively without any C
extension.

**Consequence — the fallback (former plan B) is now the plan.** Key detection
moves out of the script into a **dedicated local detector process** (§3.1),
distinct from the cloud backend (§5). The distributable is therefore **two local
artifacts** — the remote script (frontend + execution) and the detector — not
one. The capture/execution boundary stays over HTTP (`:9000`), which is what made
this switch cheap: only the *producer* of key events changed; the script's action
API was untouched.

What remains true: **the same shortcuts everywhere**, configured globally (§3.3),
through a UI that discovers actions (§3.4). Only the autonomy ("script as the
single artifact") was the casualty.

## 5. Distribution target & the role of the backend

The project must eventually be **packaged as an installable binary** for users
(not merely runnable from sources).

**Three tiers, not one process.** The architecture settles into three distinct
pieces, each with a different home:

1. **The remote script** — runs inside Ableton; serves the config frontend (§3.2)
   and executes actions via the Live API (§3.4). Constrained Python (no C ext).
2. **The local detector** — a separate process on the user's machine that owns
   the keyboard hook (§3.1) and calls the script's `:9000` API. Normal system
   Python, so `ctypes`/`pynput` work.
3. **The backend** — *not local and not part of the shortcut hot path*. It is a
   **remote, cloud-hosted service** dedicated to heavy work that is impractical
   on the user's machine: **machine-learning tasks** (e.g. key/audio analysis)
   and similar compute. It is a candidate to sit **behind a paywall**. The current
   local `:9001` FastAPI service (packaged as a Scheduled Task) is a **development
   stand-in** for this future cloud backend, not its final form. Crucially, key
   detection must **never** depend on the backend — a paywalled/remote service
   cannot gate a local keyboard shortcut.

   **Status (2026-05-28): the backend is paused.** While the shortcut manager is
   built, the backend is **not run or maintained locally** — no Scheduled Task,
   no dev process. Nothing in the shortcut path depends on it (guaranteed above),
   so it can stay down. It will be picked back up when ML features are on the
   roadmap, most likely directly as the cloud service rather than the local
   `:9001` stand-in.

Design consequences to keep in mind without implementing them prematurely:

- the global configuration must live at a stable, documented user location (not
  inside the source tree), readable by both the script and the local detector;
- installation must place the remote script at the right location for Live **and**
  install/register the local detector as a background process (§3.1);
- the script's dependencies must remain compatible with Live's constrained
  Python environment (cf. `src/script/pyproject.toml`: stdlib + a minimum of
  lightweight deps); the detector, running under normal Python, has no such limit;
- keep a clean seam between local (script + detector) and remote (backend) so the
  backend can be lifted to the cloud — and metered/paywalled — without touching
  the shortcut path.

### 5.1 Running the pieces in development

- **The detector** runs in dev as `poetry run detector` in a terminal: live logs,
  Ctrl+C to stop, instant restart. This is the everyday dev loop.
- **Docker is not an option for the detector.** It owns a global keyboard hook
  (`pynput`/`SetWindowsHookEx`) and a foreground-window check
  (`GetForegroundWindow`) — both are integration with the *host* Windows session.
  A container (WSL2) is isolated from the host's keyboard and window manager and
  cannot reach them, the same reason the backend can't be containerized while its
  reverse channel uses LoopMIDI. The detector *is* host-level OS integration, so
  it always runs as a native host process.
- **Production packaging** (auto-start at logon via a Scheduled Task) is a later
  milestone, deliberately separate from the dev loop — do not conflate the two.
- **The backend** is paused (see §5, tier 3) and not run in dev for now.

## 6. Scope of the first iteration (prototype)

> Implementation details will be decided in a dedicated spec (`docs/specs/`).
> What follows only bounds the ambition of the first cut.

First end-to-end action: **load a device by name** through a shortcut configured
in the frontend.

This exercises the whole chain in a minimal version:

- key detection in the local detector process (§3.1);
- a minimal frontend served by the script (§3.2) to enter "key combination →
  `load_device(name=…)`";
- a persisted global configuration (§3.3), shared by detector and script;
- execution via the existing `load_device` action (§3.4), reached over the
  script's `:9000` API.

Out of scope for the prototype (but within the vision): the full action catalog,
final binary packaging, fully replacing AHK, and the cloud backend (§5) — the
prototype is local-only.

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
