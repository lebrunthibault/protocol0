# Constitution — Protocol0 Keyboard Shortcut Manager

> This document describes the **vision** and the **durable architecture choices**
> of a keyboard shortcut manager for Ableton Live, built on top of the Protocol0
> remote script. It describes the long-term *what* and *why*, not the *how* of
> any given iteration — concrete iterations live in `docs/specs/` (see
> `docs/specs/README.md`).
>
> When a decision here is invalidated by the implementation, update this
> document — it must remain the source of truth for the intent.

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
   set. We want the opposite: **the same shortcuts everywhere**, whatever project
   is open — exactly like a code editor where `Ctrl+P` is the same regardless of
   which repo is open.

### Target mental model

```
  [ key pressed ]
        │
        ▼
  key detection  ──►  binding resolution  ──►  action  ──►  Live API (LOM)
   (global hook)      (global config)        (parameterized)
```

- **Key detection** — a global hook captures key combinations whether or not Live
  has focus.
- **Binding resolution** — look up, in a **global configuration** (machine/user
  level, not set level), which action is bound to the captured combination.
- **Action** — a named, parameterizable unit (e.g. `load_device(name=…)`,
  `select_track(name=…)`). The catalog of available actions is **discoverable**
  from the configuration frontend.
- **Live API** — the action runs through the Ableton API, on the Live thread.

## 2. Architecture choices

The important technical decisions, kept deliberately simple. Implementation
details live in `docs/specs/`.

### Hotkey detection runs in a separate local process (the detector)

Key detection lives in a **dedicated local process — the *detector*** — not in
the remote script. It **cannot** be script-only: Ableton's embedded Python is a
restricted runtime that cannot host a global keyboard hook (a prototype spike
confirmed this and it is settled). The detector runs under a normal system
Python, watches the keyboard, and — **only when Ableton is the foreground
window** — resolves the binding and calls the script's HTTP API. It stays neutral
toward keys it doesn't handle and survives logon as a background process.

### The remote script exposes an HTTP API and serves the config frontend

The remote script runs **inside Ableton** and exposes an HTTP API on
`127.0.0.1:9000`. It also **serves the configuration frontend** from there: the
user enters a key combination, picks an action, parameterizes it, and persists
the binding. Serving it from the script keeps configuration reachable **locally
and offline**, with no dependency on the cloud or on the detector being up.

### Bindings are global

Shortcut → action bindings are stored in **a single configuration at the
machine/user level** (`%APPDATA%\Protocol0\shortcuts.json`), shared by the script
(writer) and the detector (reader), identical across all sets — never attached to
a set. This is the core value over the native manager: *the same shortcuts
everywhere*.

### Actions form a discoverable catalog

An **action** is a named, parameterizable, self-described unit (name, label,
expected parameters). The script exposes this catalog; the frontend **reads** it
rather than hard-coding the action list. Existing routes (`/device/load`,
`/track/select`, …) prefigure the catalog — each action builds on a Live-API
capability.

### Windows-first

The project is built and run **on Windows**, and the tooling reflects that. The
detector ships as a Windows executable, autostarts through a **Scheduled Task**,
and is packaged by a Windows installer; the operational scripts in `scripts/` are
**PowerShell**. This is a practical consequence of the environment Protocol0 lives
in — Ableton Live on the author's machine — not a rejection of other platforms.
The architecture itself (HTTP boundary, global config, detector/script split) is
portable; macOS support is tracked in `docs/specs/backlog/` and would replace the
platform-specific packaging and autostart layer, not the core design.

### Two surfaces, not one process

The architecture settles into two distinct pieces, each with a different home:

1. **The remote script** — runs inside Ableton; serves the frontend and executes
   actions via the Live API. Constrained Python: **stdlib-only**.
2. **The local detector** — a separate process on the user's machine that owns the
   keyboard hook and calls the script's `:9000` API. Normal system Python.

### Guiding principles

- **Never block the Live thread.** Captured events cross into the Live thread
  through a tick-drained boundary; no direct Live-API call from a daemon thread.
- **Discoverable over hard-coded.** The frontend discovers actions from the
  catalog.
- **Decoupled capture / execution.** The HTTP boundary between *what detects* and
  *what acts* stays clean — that's what made moving detection out of the script
  cheap.
- **The set does not own the shortcuts.** Config is global by default.
- **Iterate behind specs.** Every evolution goes through `docs/specs/`; this
  document only describes the durable intent.

## 3. Usage

Two ways to install and run Protocol0.

### End users (installer)

1. Download `Protocol0-Setup-<version>.exe` from the project's **GitHub
   Releases**.
2. Run it. The installer deploys the **detector** executable, copies the **remote
   script** into Ableton's MIDI Remote Scripts folder, and registers a **Scheduled
   Task** so the detector autostarts at logon.
   - Windows SmartScreen will warn on first run — the installer is **currently
     unsigned** (code signing is on the backlog). Choose *More info → Run anyway*.
3. Configure shortcuts at **`http://127.0.0.1:9000/shortcuts`**.

### Local / from source (developers)

- Run the detector in a terminal (live logs, Ctrl+C to stop):

  ```sh
  make detector
  ```

- First-time setup (both poetry envs + install the remote script into Ableton):

  ```sh
  make bootstrap   # finds Python >=3.11, sets up envs, deploys Protocol_0 (Win + macOS)
  make install     # redeploy just the remote script after editing it
  ```

- Config UI: `http://127.0.0.1:9000/shortcuts`. Logs: `%APPDATA%\Protocol0\logs\`.

## 4. Roadmap

The roadmap lives in `docs/specs/`. To see what's planned and in flight:

- **`docs/specs/todo/`** — prioritized, ready to be implemented next.
- **`docs/specs/backlog/`** — ideas and future work, not yet prioritized.

`docs/specs/in-progress/` shows what's actively being worked on, and
`docs/specs/done/` keeps the history. See `docs/specs/README.md` for the
lifecycle.
