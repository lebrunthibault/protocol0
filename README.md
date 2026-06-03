# Protocol0

Protocol 0 is a companion software for Ableton Live.
It provides a global keyboard shortcut manager that works across all sets, letting you keymap usual parameters as well as custom actions (load a device by name, select a track, or anything else the Live API (LOM) exposes).
Configure it all from a small web UI.
Protocol 0 is free, open-source, and extensible : 
- you can add new actions by [creating a plugin](docs/plugins.md)
- the remote script exposes an HTTP API, so you can call it from your own tools (e.g. a Stream Deck plugin, or a custom frontend).

The project is in early development. Feedback and contributions are very welcome.

> **Platform: Windows.** Protocol0 is developed and run on Windows. The installer,
> the autostart mechanism (a Scheduled Task), and the packaging tooling under
> [`scripts/windows/`](scripts/windows/) are PowerShell and Windows-specific. Dev
> setup (`make bootstrap`) is cross-platform, but the detector itself is
> Windows-only for now; macOS support is on the backlog (see `docs/specs/backlog/`).

See [`CONSTITUTION.md`](CONSTITUTION.md) for the vision and the design decisions
behind it.

## Documentation & installation

Visit the website: <https://www.protocol0.live/>.

## Installation

### End users (installer)

1. Download `Protocol0-Setup-<version>.exe` from the
   [GitHub Releases](https://github.com/lebrunthibault/protocol0/releases).
2. Run it. The installer deploys the **detector**, copies the **remote script**
   into Ableton's MIDI Remote Scripts folder, and registers a Scheduled Task so
   the detector autostarts at logon.
   - Windows SmartScreen warns on first run (the installer is currently unsigned):
     *More info → Run anyway*.
3. Configure shortcuts at <http://127.0.0.1:9000/shortcuts>.

### From source (developers)

Prerequisites (install once): `make`, [`poetry`](https://python-poetry.org/docs/#installation),
and a Python `>=3.11`.

```sh
# First time: set up everything (both Python envs + deploy the remote script)
make bootstrap

# Then run the detector (live logs, Ctrl+C to stop)
make detector
```

`make bootstrap` is cross-platform (Windows + macOS): it finds a Python `>=3.11`,
sets up both poetry envs (remote script + detector), and copies the remote script
into Ableton. Re-run `make install` alone to redeploy just the remote script after
editing it. (On macOS the env setup completes, but the detector itself is still
Windows-only for now — see `docs/specs/backlog/`.)

Config UI: <http://127.0.0.1:9000/shortcuts>. Logs: `%APPDATA%\Protocol0\logs\`.

## Architecture

Two surfaces cooperate over local HTTP:

```
keyboard ─► detector ──HTTP :9000──► remote script (in Ableton) ─► Live API (LOM)
            (local process)          (HTTP API + config frontend)
```

- **Detector** — a separate local process that owns the global keyboard hook and,
  when Ableton is focused, calls the script's API. It can't live inside the script
  (Ableton's embedded Python can't host a keyboard hook).
- **Remote script** — runs inside Ableton, exposes the HTTP API, serves the
  config frontend, and executes actions via the Live API. Stdlib-only.

Bindings are stored globally (`%APPDATA%\Protocol0\shortcuts.json`), shared by the
script and the detector. Full rationale in [`CONSTITUTION.md`](CONSTITUTION.md).

The repo also carries a third, non-runtime surface: the marketing site and user
documentation in [`src/website/`](src/website/) — a static page deployed to
<https://www.protocol0.live/> with no build step.

Cross-platform setup lives in stdlib-only [`scripts/`](scripts/) Python (`make
bootstrap`/`install` dispatch to them); the genuinely Windows-only tooling
(installer, PyInstaller, Scheduled Tasks) sits under
[`scripts/windows/`](scripts/windows/).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
