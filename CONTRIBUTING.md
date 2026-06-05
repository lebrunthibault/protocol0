# Contributing to Protocol0

Thanks for taking the time to look at Protocol0.

## Reporting bugs

The fastest way to help. A good report includes:

- **Your environment** — OS version, Ableton Live version, and the Protocol0
  version (see [`VERSION`](VERSION)).
- **Logs** — Protocol0 writes rotating logs to `%APPDATA%\Protocol0\logs\`
  (e.g. `agent.log`). Attach the relevant files.
- **Steps to reproduce** — what you did, what you expected, what happened
  instead. A precise sequence beats a paragraph of description.

You can open an issue or GitHub or reach me on [Discord](https://discord.gg/p2qYMQeru).

## Running it locally

Protocol0 is a monorepo with two surfaces under `src/`: the **remote
script** (runs inside Ableton, stdlib-only Python) and the **agent** (a Rust
crate, built with Cargo).

Requires the latest stable Rust, Node 18+, and Python 3.11+
([poetry](https://python-poetry.org/docs/#installation) only to lint/test the
remote script, which is otherwise stdlib-only). Then, from the repo root:

- **First-time setup** — `make bootstrap`. Cross-platform (Windows + macOS): it
  finds a Python `>=3.11`, sets up the remote script's poetry env (its lint/test
  tooling), and installs the remote script into Ableton's MIDI Remote Scripts
  folder (wiring up the source dir so edits are picked up live). Re-run `make
  install` alone to redeploy just the remote script after editing it.
- **Agent** — `make agent`.

  After `make bootstrap`, (re)start Ableton Live and select Protocol_0 as a
  Control Surface.

- **Config UI** — once the script is running, the shortcut-configuration page
  is served by the script itself at <http://127.0.0.1:9000/shortcuts>.
- **Logs** — `%APPDATA%\Protocol0\logs\` (also `make logs` to tail them live).

## Commits

Commit messages should follow the [Conventional Commits](https://www.conventionalcommits.org) 
specification and be in lower case.
