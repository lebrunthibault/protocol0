<p align="center">
  <img src="docs/assets/banner.svg" alt="Protocol 0 — the forgotten Ableton key mapper" width="100%">
</p>

Protocol 0 is a third party keyboard shortcut manager for Ableton Live.

It handles classic Ableton [keyboard shortcuts](https://www.ableton.com/en/manual/live-keyboard-shortcuts/) as well as custom actions.

Check out the [docs](https://www.protocol0.live/docs) for more details.

It's built with:
- A Rust agent
- A Javascript web UI
- A Python MIDI Remote Script that exposes an HTTP API from inside Live

It's extensible
- Add your own actions by [writing a plugin](docs/plugins.md)
- Trigger actions with your own tools by calling the script's HTTP API (e.g. AHK, a Stream Deck..)

> **Platform: Windows.** Protocol0 Windows-only for now; macOS support is on the roadmap.

See [`CONSTITUTION.md`](CONSTITUTION.md) for the vision and the design decisions
behind it.

The project is in early development. Feedback and contributions are very welcome.

## Installation

Download the latest release from the [Releases](https://github.com/lebrunthibault/protocol0/releases)
and check out the [docs](http://localhost:8080/docs/installation.html) for more details

### From source

Requires [Rust](https://rustup.rs/), [Node](https://nodejs.org/en), and [Python 3.11+](https://www.python.org/).

```sh
git clone https://github.com/lebrunthibault/protocol0
cd protocol0

make bootstrap  # set up the remote script's tooling + deploy it into Ableton
make agent      # build (cargo) and run the agent, with live logs
make up         # or: run the agent + frontend (live reload) + website
```

- Config UI: <http://127.0.0.1:9010>.
- Logs: `%APPDATA%\Protocol0\logs\`.
- Config file: (`%APPDATA%\Protocol0\shortcuts.json`)

## Architecture

See the [docs](https://www.protocol0.live/docs/architecture.html)


## Contributing

- Join [Discord](https://discord.gg/p2qYMQeru) to chat and get help
- See [CONTRIBUTING.md](CONTRIBUTING.md)

## Roadmap

- Fix any bugs
- Mac version
- More smart actions
- make it easier for users to add plugins (add actions from a chat interface)
- MIDI mapping

for much later (maybe another project)
- Add features for managing your Live sets (take notes, tag)
