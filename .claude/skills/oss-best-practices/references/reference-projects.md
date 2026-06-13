# Reference OSS projects for Protocol0

A starting roster of open-source projects to study when researching best practices. Pick the
ones whose traits match the topic; add topic-specific repos via `WebSearch` as needed. Each entry
notes **why it's a match** against Protocol0's traits:

- **D** = daemon / background service
- **W** = serves a self-hosted local web UI
- **X** = plugin/extension of a host app (audio or graphics)
- **A** = music/audio domain
- **P** = cross-platform desktop (Windows+macOS), not server/Linux-only

The closer to `D + W + X + A + P`, the better the reference.

For LLM *pattern* topics (code generation, agents vs workflows, sandboxed execution,
LLM-as-judge, evals, prompting, structured output), also see
[authoritative-sources.md](authoritative-sources.md) — vendor guidance (Anthropic, OpenAI,
Pydantic AI, LangChain, Mistral) and recognized practitioners often outweigh user repos there.

## Tier 1 — closest architectural twins (daemon + local web UI + desktop)

- **Syncthing** — `https://github.com/syncthing/syncthing` — **D W P**.
  The primary inspiration. Background sync daemon that serves its own web UI on a local port,
  config as files, cross-platform desktop, OSS through and through. Best reference for: local web
  UI auth/CSRF on a localhost daemon, autostart per OS, config file format & migrations, GUI/daemon
  split, REST API design, self-update. Not an extension and not audio, but the *shape* is identical.

- **Transmission** — `https://github.com/transmission/transmission` — **D W P**.
  BitTorrent daemon (`transmission-daemon`) with an RPC API consumed by a bundled web UI and native
  clients — directly parallels Protocol0's "background process + HTTP API + web UI + optional native
  front ends". Good for: RPC/HTTP API surface design, daemon lifecycle, multi-frontend story.

- **Tailscale** — `https://github.com/tailscale/tailscale` — **D P**.
  Background service (`tailscaled`) + local API + small local web UI + tray app, polished
  Windows+macOS desktop installers and autostart. Strong reference for desktop service packaging,
  tray UX, and local-daemon ↔ UI IPC on Windows/macOS specifically.

## Tier 2 — strong on one axis (self-hosted web UI / solid service architecture)

- **Grafana** — `https://github.com/grafana/grafana` — **D W**.
  Gold standard for a backend that serves a first-class web UI, plus a real **plugin** architecture
  (`X`-ish: plugins extend Grafana, not a host app). Study for: plugin/extension system design,
  provisioning/config, frontend-backend contract. Server-oriented, so discount its deploy assumptions.

- **Jellyfin** — `https://github.com/jellyfin/jellyfin` — **D W A(media)**.
  Media server: background service + web UI + plugin system, media-adjacent. Good for plugin APIs and
  serving a config/admin UI from a long-running service. Server/Linux-leaning — filter for desktop.

- **Navidrome** — `https://github.com/navidrome/navidrome` — **D W A**.
  Music streaming server: single self-contained binary, low footprint, serves its own web UI, music
  domain. Closest *audio* match for the "self-hosted web UI over a music collection" pattern.

## Tier 3 — extension/plugin patterns and audio companions (the `X`/`A` axes)

- **Mopidy** — `https://github.com/mopidy/mopidy` — **D W A X**.
  Music server with a Python **extension/plugin** ecosystem (e.g. Iris web UI extension). Best
  reference for "core daemon + third-party extensions + web frontends" in the audio domain — very
  close to Protocol0's "add actions via a plugin" goal.

- **Beets** — `https://github.com/beetbox/beets` — **A X (W via `beet web`)**.
  Music library manager with a strong plugin architecture and an optional web interface. Reference for
  Python plugin API ergonomics and an opt-in local web UI bolted onto a tool.

- **Oscleton SDK / LiveOSC family** — search `WebSearch` for current repos — **X A**.
  Ableton Live companion apps built on a MIDI Remote Script bridging Live to external UIs/devices
  (OSC/HTTP). The *only* close domain twins (Live remote-script + external client). Verify the live
  repo before citing — the ecosystem shifts.

- **Ableton Extensions SDK** — `https://github.com/ableton/extensions-sdk` — **X A**.
  Ableton's **official** (2026) JS/TS extension toolkit; extensions run inside Live and can host
  webviews. Not a daemon, but the canonical reference for "what an official Live extension looks
  like" and for in-Live webview UI patterns. Worth watching as it may reshape Protocol0's approach.

## How to choose for a given topic

| Topic | Lean on |
|---|---|
| Local web UI security (CSRF, auth, binding to localhost) | Syncthing, Transmission |
| HTTP/RPC API design for a local daemon | Transmission, Syncthing, Tailscale |
| Autostart / installer / tray on Windows+macOS | Tailscale, Syncthing |
| Self-update of a desktop OSS app | Syncthing, Tailscale |
| Plugin/extension architecture | Mopidy, Beets, Grafana, Ableton Extensions SDK |
| Config file format, schema, migrations | Syncthing, Navidrome |
| Audio/Live-specific integration | Mopidy, Beets, Oscleton/LiveOSC, Ableton Extensions SDK |

Don't treat this list as closed — for any topic, `WebSearch` for the 2-3 projects that solved that
*exact* problem and add them, judging each by the trait letters above.
