# Protocol0

Protocol 0 is a companion software for Ableton Live.
It provides a global keyboard shortcut manager that works across all sets, letting you keymap usual parameters as well as custom actions (load a device by name, select a track, or anything else the Live API (LOM) exposes).
Configure it all from a small web UI.
Protocol 0 is free, open-source, and extensible : 
- you can add new actions by [creating a plugin](docs/plugins.md)
- the remote script exposes an HTTP API inside Live, so you can call its actions from your own tools (e.g. a Stream Deck plugin, or a custom frontend).

The project is in early development. Feedback and contributions are very welcome.

> **Platform: Windows.** Protocol0 is developed and run on Windows. The installer,
> the autostart mechanism (a Scheduled Task), and the packaging tooling under
> [`scripts/windows/`](scripts/windows/) are PowerShell and Windows-specific. Dev
> setup (`make bootstrap`) is cross-platform, but the agent itself is
> Windows-only for now; macOS support is on the backlog (see `docs/specs/backlog/`).

See [`CONSTITUTION.md`](CONSTITUTION.md) for the vision and the design decisions
behind it.

## Documentation & installation

Visit the website: <https://www.protocol0.live/>.

## Installation

### End users (installer)

1. Download `Protocol0-Setup-<version>.exe` from the
   [GitHub Releases](https://github.com/lebrunthibault/protocol0/releases).
2. Run it. The installer deploys the **agent**, copies the **remote script**
   into Ableton's MIDI Remote Scripts folder, and registers a Scheduled Task so
   the agent autostarts at logon.
   - Windows SmartScreen warns on first run (the installer is currently unsigned):
     *More info → Run anyway*.
3. Configure shortcuts at <http://127.0.0.1:9010/shortcuts> (works even with
   Ableton closed).

### From source (developers)

Prerequisites (install once): `make`, [`poetry`](https://python-poetry.org/docs/#installation),
and a Python `>=3.11`.

```sh
# First time: set up everything (both Python envs + deploy the remote script)
make bootstrap

# Then run the agent (live logs, Ctrl+C to stop)
make agent
```

`make bootstrap` is cross-platform (Windows + macOS): it finds a Python `>=3.11`,
sets up both poetry envs (remote script + agent), and copies the remote script
into Ableton. Re-run `make install` alone to redeploy just the remote script after
editing it. (On macOS the env setup completes, but the agent itself is still
Windows-only for now — see `docs/specs/backlog/`.)

To work on the configuration frontend with live-reload, run `make frontend`
(Vite dev server, proxies `/api` to the agent) alongside `make agent`.

Config UI: <http://127.0.0.1:9010/shortcuts>. Logs: `%APPDATA%\Protocol0\logs\`.

## Architecture

Two surfaces cooperate over local HTTP:

```
keyboard ─► agent ──────────────────► remote script (in Ableton) ─► Live API (LOM)
            (local process,           (action HTTP API,
             :9010 web UI + /api)       dynamic port)
            └─ serves the keymapper web UI + /api (config CRUD)
```

- **Agent** ([`src/agent/`](src/agent/)) — an always-on local process. It owns the
  global keyboard hook and, when Ableton is focused, calls the script's action API.
  It also serves the **keymapper web UI** (a Vue 3 SPA, source in
  [`src/frontend/`](src/frontend/)) and the **`/api`** that reads/writes bindings,
  on a fixed `:9010` — so you can edit shortcuts even with Ableton closed. The hook
  can't live inside the script (Ableton's embedded Python can't host one).
- **Remote script** — runs inside Ableton, exposes the **action API** on a dynamic
  port, and executes actions via the Live API. Stdlib-only.

Bindings are stored globally (`%APPDATA%\Protocol0\shortcuts.json`), owned by the
agent (written from its UI, read by its keyboard listener). Full rationale in
[`CONSTITUTION.md`](CONSTITUTION.md).

The repo also carries a non-runtime surface: the marketing site and user
documentation in [`src/website/`](src/website/) — a static page deployed to
<https://www.protocol0.live/> with no build step.

Cross-platform setup lives in stdlib-only [`scripts/`](scripts/) Python (`make
bootstrap`/`install` dispatch to them); the genuinely Windows-only tooling
(installer, PyInstaller, Scheduled Tasks) sits under
[`scripts/windows/`](scripts/windows/).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
