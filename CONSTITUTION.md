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
  `select(name=…)`). The catalog of available actions is **discoverable**
  from the configuration frontend.
- **Live API** — the action runs through the Ableton API, on the Live thread.

Key detection, binding resolution and the configuration frontend all live in the
**agent**; only the final action call crosses into the script inside Live.

### Future direction — a MIDI mapping mode alongside the keymapper

The keyboard is the first input surface, not the only one. The same mental model —
**set-independent bindings → discoverable smart actions → Live API** — extends to
**MIDI**: a second "mapping mode" next to the keymapper, where a MIDI control (a
knob, a button) is bound to an action instead of a key combination.

The triggering use case is letting knobs drive the **first N parameters of the
selected device** (up to 16, to match an Ableton Rack's macros) — the
[*map encoders to the selected device*](https://midiremotescripts.structure-void.com/guides/cookbook/#map-encoders-to-the-selected-device)
pattern. The script already does a fixed version of this (hard-coded encoder
groups); the goal is to make it
**configurable from the web UI**, like the keyboard — and more generally to map any
catalog action to a MIDI control.

Two properties carry over unchanged: bindings are **global** (a JSON under
`%APPDATA%\Protocol0\`, never in the `.als`), and they target the **same
discoverable action catalog**. One difference is deliberate: unlike the keyboard,
**MIDI detection stays inside the script** — MIDI already arrives in Live through
the remote-script framework, and routing "selected device → param n" needs the LOM
live, so there is no reason to re-capture it out of process. The agent still owns
only the configuration UI; the script reads the JSON, builds the actions, and
attaches them to the encoders. *Decoupled capture / execution* holds either way:
where the input is captured differs, but the action and its global config do not.

This is **future work**, tracked in
[`docs/specs/backlog/2026-06-04-midi-mapping-mode.md`](docs/specs/backlog/2026-06-04-midi-mapping-mode.md);
it is recorded here as durable intent, not a committed iteration.

## 2. Architecture choices

The important technical decisions, kept deliberately simple. Implementation
details live in `docs/specs/`.

### A standalone agent owns key detection and the configuration frontend

Everything outside Live lives in a **single standalone process — the *agent***,
a **native Rust binary** that runs outside Ableton and survives logon as a
background process. It owns two things:

1. **Key detection.** The agent hosts the global keyboard hook. This **cannot** be
   script-only: Ableton's embedded Python is a restricted runtime that cannot host
   a global keyboard hook (a prototype spike confirmed this and it is settled). The
   agent watches the keyboard and — **only when Ableton is the foreground
   window** — resolves the binding and calls the script's action API. It stays
   neutral toward keys it doesn't handle.
2. **The configuration frontend.** The agent serves a web app (the
   keymapper UI) and the `/api` that reads and writes the bindings, on a fixed
   `127.0.0.1:9010`. The keymapper is unlocked only when Ableton is running and
   the remote script is active — editing a shortcut for Live should happen with
   Live in front of you. Configuration stays **local and offline**, with no
   dependency on the cloud.

Detection *and* configuration sit in the same process; the agent owns the
bindings file so a saved change is picked up on the next keypress with no reload
plumbing.

### The remote script exposes an action API inside Live

The remote script runs **inside Ableton** and exposes a REST HTTP API under
`/api` — a `/api/health` check, a self-describing `/openapi.json`, a Swagger UI at
`/docs`, and the **action routes** — core routes like `/api/set/get_state` plus
plugin actions under `/api/action/<plugin>/<method>` (e.g.
`/api/action/track/select`) — that drive Live through the
LOM. Reads are `GET`, mutations are `POST`. Its port is
**dynamic** (advertised via `runtime.json`), and it lives and dies with Ableton.
The agent is its main caller: on a matched keypress, the agent looks up the
script's URL and invokes the action.

### Bindings are global

Shortcut → action bindings are stored in **a single configuration at the
machine/user level** (`%APPDATA%\Protocol0\shortcuts.json`), owned by the agent —
written from its frontend, read by its keyboard listener (reloaded on file
change). Identical across all sets, never attached to a set. This is the core
value over the native manager: *the same shortcuts everywhere*.

### Actions form a discoverable catalog

An **action** is a named, parameterizable, self-described unit (name, label,
expected parameters). The script exposes this catalog through its OpenAPI document
(`/openapi.json`, rendered at `/docs`).

### Plugins extend the script

New behavior is added through **plugins** — small units inside the script that
**react to events** in Live and **expose new actions**, without touching the
core. A plugin declares what it listens to and what it offers; the script
discovers it, wires it up, and tears it down cleanly. This keeps the action set
**open and discoverable** (the natural extension of *Discoverable over
hard-coded*): the way to grow Protocol0's vocabulary is to drop in a plugin, not
to edit a central list. The *how* lives in [`docs/plugins.md`](docs/plugins.md).

There is a single mechanism — a plugin — and a plugin exposes an action by
decorating a method with `@action`: the method name is the action, its typed
parameters are the inputs, and the script generates the route. When the goal is
simply to *add one action* — no event listening, no lifecycle — a **smart action**
is just that minimal shape: one class with one `@action` method, discovered the
same way and bindable to a shortcut like any other.

### Windows-first

The project is built and run **on Windows**, and the packaging reflects that. The
agent ships as a Windows executable, autostarts through a **Startup-folder shortcut**
(visible and removable by the user, like AutoHotkey/Espanso), shows a systray icon,
and is packaged by a Windows installer. Because the agent is a global keyboard hook —
the textbook keylogger profile — distribution leans on a **single, stable code-signing
identity** (Azure Trusted Signing): both the installer and the resident agent exe are
Authenticode-signed in release CI so the publisher is verified, and the identity is never
rotated so SmartScreen reputation compounds across releases rather than resetting per build.
Day-to-day developer setup is deliberately kept off that path:
the dev entry points (`make bootstrap`/`install`) dispatch to **stdlib-only,
cross-platform Python**, so a fresh checkout sets up on Windows *or* macOS. The architecture itself
(HTTP boundary, global config, agent/script split) is portable; macOS support
is tracked in `docs/specs/backlog/` and would replace the platform-specific
packaging and autostart layer, not the core design.

### Two surfaces, not one process

The architecture settles into two distinct pieces, each with a different home:

1. **The agent** — an always-on process on the user's machine. It owns the keyboard
   hook, serves the configuration frontend and its `/api` on a fixed `:9010`, and
   calls the script's action API on a matched keypress. A native Rust binary.
2. **The remote script** — runs inside Ableton; exposes the action API and executes
   actions via the Live API on a dynamic port. Constrained Python: **stdlib-only**.

## 3. Roadmap

The roadmap lives in `docs/specs/`. To see what's planned and in flight:

- **`docs/specs/todo/`** — prioritized, ready to be implemented next.
- **`docs/specs/backlog/`** — ideas and future work, not yet prioritized.

`docs/specs/in-progress/` shows what's actively being worked on, and
`docs/specs/done/` keeps the history. See `docs/specs/README.md` for the
lifecycle.
