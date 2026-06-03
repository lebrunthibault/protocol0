# Creating a plugin

Protocol0's remote script (the part that runs **inside Ableton**) is extensible
through small **plugins**. A plugin can:

- **react to things happening in Live** — a clip recorded, playback started, a
  track selected… — by declaring event listeners;
- **expose a new action** — an HTTP endpoint that does something via the Live
  API, callable from a keyboard shortcut or any external tool.

You write a plugin by subclassing `PluginInterface` and declaring what it
listens to and what it exposes. The loader wires everything up at startup and
tears it down cleanly on disconnect — you never manage subscriptions by hand.

> The remote script runs under Ableton's **restricted, stdlib-only** embedded
> Python. Plugins must stay stdlib-only too (no third-party packages), and must
> **never block** Live's thread — see [Constraints](#constraints) below.

## Where plugins live

Plugins are Python packages under:

```
src/script/protocol0/plugins/
├── example/          ← copy this to start your own
│   └── ExamplePlugin.py
└── live_set/         ← the author's real-world plugin
```

They are **discovered automatically**: at startup, `PluginLoader` imports the
`plugins` package and instantiates every subclass of `PluginInterface` it finds.
There is no registry to edit — drop a file in, subclass `PluginInterface`, done.

A complete, runnable template lives at
[`src/script/protocol0/plugins/example/ExamplePlugin.py`](../src/script/protocol0/plugins/example/ExamplePlugin.py).
It is disabled by default; copy it or flip `should_start` to try it.

## The interface

```python
class PluginInterface:
    name: str = ""

    def should_start(self) -> bool: ...          # run this plugin? (default: True)
    def start(self) -> None: ...                 # optional one-time setup
    def stop(self) -> None: ...                  # optional teardown
    def register_listeners(self) -> Dict[Type, Callable]: ...   # event -> handler
    def register_actions(self) -> List[Callable]: ...           # @route functions
```

Everything except `name` is optional. A purely declarative plugin only
implements `register_listeners` and/or `register_actions`.

### Lifecycle

```
should_start() ─true─► start() ─► listeners subscribed ─► (plugin lives)
                                                              │
                                  on script disconnect ◄──────┘
                                  listeners unsubscribed ─► stop()
```

- `should_start()` lets a plugin opt out (e.g. only run on a specific set).
  Return `False` and the plugin is skipped entirely.
- `start()` runs once; use it for setup that isn't a listener or an action.
- The loader **subscribes** every listener from `register_listeners()` after
  `start()`, and **unsubscribes** them automatically before `stop()`. You do not
  call `DomainEventBus.subscribe`/`un_subscribe` for them.

## Reacting to events

Return a `{event_type: handler}` map from `register_listeners()`. Each handler
receives the event instance.

```python
from protocol0.domain.lom.clip.ClipRecordedEvent import ClipRecordedEvent
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent

class MyPlugin(PluginInterface):
    name = "my_plugin"

    def register_listeners(self):
        return {
            SongStartedEvent: self._on_play,
            ClipRecordedEvent: self._on_clip_recorded,
        }

    def _on_play(self, _: SongStartedEvent):
        ...

    def _on_clip_recorded(self, event: ClipRecordedEvent):
        clip = event.clip            # events carry their payload as attributes
        ...
```

A few commonly useful events (all under `protocol0/domain/`):

| Event | Fires when | Payload |
|---|---|---|
| `SongStartedEvent` | Playback starts | — |
| `SongStoppedEvent` | Playback stops | — |
| `ClipCreatedEvent` | A clip appears in a slot | `.clip_slot` |
| `ClipRecordedEvent` | A clip finishes recording | `.clip` |
| `SimpleTrackSelectedEvent` | A track is selected | (see the class) |
| `TracksMappedEvent` | The track tree is (re)mapped | — |
| `ScenesMappedEvent` | The scene list is (re)mapped | — |
| `BarChangedEvent` | A new bar starts | — |

The full list is every `*Event.py` under `protocol0/domain/`. Subscribe to the
event type, not to a string name.

## Adding an action

An **action** is a function decorated with `@route` — exactly like the script's
built-in actions (`/device/load`, `/track/select`, …). It becomes an HTTP
endpoint listed on the script index at <http://127.0.0.1:9000/> and callable by
the agent at keypress time (or by any tool — see the
[HTTP API docs](https://www.protocol0.live/docs/http-api.html)).

Declare your routes from `register_actions()` so the loader logs them and the
intent is explicit:

```python
from protocol0.application.http.Router import route

@route("GET", "/my_plugin/do_thing")
def do_thing(name: str) -> None:
    """Short docstring — shown as the action's label on the index."""
    get_container().get(SomeService).do_thing(name)

class MyPlugin(PluginInterface):
    name = "my_plugin"

    def register_actions(self):
        return [do_thing]
```

Notes on routes (handled by `application/http/Router.py`, unchanged by plugins):

- **Query params are coerced** from the function signature: `name: str`,
  `count: int`, `flag: bool`. A parameter without a default is required (→ `400`
  if missing).
- **Return type drives the response.** Return `None` → fire-and-forget `200`.
  Return a `str` → `text/html`. Return a dict/list → `application/json`.
- The handler runs **on Live's thread** via the HTTP bridge — safe to call the
  Live API from inside it.

## Constraints

- **Stdlib-only.** Ableton's embedded Python can't load third-party packages.
- **Never block Live's thread.** Don't sleep or do long work in a listener or
  action; the bridge already hops onto Live's thread for you — keep handlers
  short.
- **One failing plugin won't take the script down.** The loader isolates each
  plugin's startup in a `try/except`, so a broken plugin is logged and skipped.

## Configuration

Per-plugin configuration is **not yet available**. When it lands it will read
from `%APPDATA%\Protocol0\settings.json` — tracked in
[`docs/specs/backlog/2026-06-02-script-settings-json.md`](specs/backlog/2026-06-02-script-settings-json.md).
For now, keep plugin behavior self-contained or driven by the set itself.

## Trying it out

After editing a plugin, redeploy the script into Ableton and reload:

```sh
make install     # copies the remote script into Ableton's Remote Scripts
```

Then check `%APPDATA%\Protocol0\logs\` for `Plugin <name> started`, open
<http://127.0.0.1:9000/> to see your action listed, and trigger your event to
confirm the listener fires.
