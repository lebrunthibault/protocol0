# Protocol0

Protocol 0 is a companion software for Ableton Live.
It provides a global keyboard shortcut manager that works across all sets, letting you keymap usual  custom actions (load a device by name, select a track, or anything else the Live API (LOM) exposes).
Configure it all from a small web UI instead of editing scripts.
Protocol 0 is free, open-source, and extensible : 
- you can add new actions by creating a plugin (doc to come)
- the remote script exposes an HTTP API, so you can call it from your own tools (e.g. a Stream Deck plugin, or a custom frontend).

The project is in early development. Feedback and contributions are very welcome.

See [`CONSTITUTION.md`](CONSTITUTION.md) for the vision and the design decisions
behind it.

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

```sh
# Run the detector (live logs, Ctrl+C to stop)
make detector

# Install the remote script into Ableton
cd src/script && make bootstrap   # first time: pyenv 3.11 + poetry install
make install_script
```

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
