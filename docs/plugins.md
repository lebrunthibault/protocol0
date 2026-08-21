# Creating a plugin

A **plugin** extends the remote script: it can register new **actions** (bindable to a
shortcut), **react to events** in Live, and/or **bind control-surface encoders**.

To create a plugin, just drop a `.py` file in `src/remote-script/protocol0/plugins/`, subclass `PluginInterface`, done.

```
src/remote-script/protocol0/plugins/
├── DevicePlugin.py       ← single-file plugin
├── example/              ← copy this to start your own
│   └── ExamplePlugin.py
└── live_set/             ← multi-file plugin (package)
```

## Adding an action

Decorate a method with
[`@action`](../src/remote-script/protocol0/application/plugin/action.py) — no argument. The
**method name** is the action name; its **typed parameters** (`str`/`int`/`float`/
`bool`) become the inputs, shown as typed fields in the keymapper UI and in the
script's Swagger UI at <http://127.0.0.1:9000/docs> (the script's REST API is the
source of truth for the action catalog — the keymapper reads it from there).

```python
from protocol0.application.plugin.action import action

class MyPlugin(PluginInterface):
    name = "my_plugin"

    @action
    def do_thing(self, name: str, count: int) -> None:
        """Short docstring — shown as the action's summary in the Swagger UI."""
        get_container().get(SomeService).do_thing(name, count)
```

The loader generates the route `POST /api/action/<plugin>/<method>` (here
`/api/action/my_plugin/do_thing`); args go in the JSON body. You never write a
route — see
[`Router.py`](../src/remote-script/protocol0/application/http/Router.py) for how it's
dispatched. Real example:
[`DevicePlugin.py`](../src/remote-script/protocol0/plugins/DevicePlugin.py).

### Undo

Every action runs inside a Live **undo step**: whatever it changes, a single
Ctrl-Z in Ableton reverts it. You do not call `Undo` yourself.

If your action finishes **later** than it returns — it delegates to a service
that returns a `Sequence`, or it defers work by a tick — return that `Sequence`
so the undo step is closed once the work actually completes:

```python
    @action
    def do_thing(self) -> Optional[Sequence]:
        """Docstring."""
        return get_container().get(SomeService).do_thing()
```

Annotate the real return type. Over HTTP the action executor **awaits** the
returned `Sequence` and answers from the real outcome (see below) — nothing is
fire-and-forget anymore.

### Response envelope

Every `POST /api/action/...` answers with a uniform JSON envelope:

| Status | Body | Meaning |
|---|---|---|
| `200` | `{"status": "done", "res": ...}` | completed (sync return, or the returned `Sequence` terminated) |
| `500` | `{"status": "error", "error": "..."}` | exception raised, or the `Sequence` errored (the failing step's message) |
| `500` | `{"status": "cancelled"}` | the `Sequence` was cancelled |
| `202` | `{"status": "running"}` | still running after 10 s — the action keeps going in Live |
| `400` | plain text | missing required parameter |

### Targeting grammar

Catalog actions take their targets as **spec strings** resolved by
[`domain/lom/addressing/`](../src/remote-script/protocol0/domain/lom/addressing/__init__.py):

- **track**: `SEL` (selected, the default) · `MST`/`master` · 1-based index
  (`"2"`) · `"name"` (quoted → exact) · bare name (exact, then substring) ·
  `<` / `>` (relative to the selection, clamped)
- **scene**: `SEL` · `LAST` · index · name · `<` / `>`
- **clip**: track spec + clip spec (`SEL` = the track's clip in the selected
  scene, or a scene index, or a name)
- **device**: `SEL` (selected device) · top-level index · dotted rack path
  `2.1.1` (1st device of the 1st chain of the 2nd device — pairs may nest) ·
  name (searched through rack chains)
- **parameter**: 1-based index or name

### Value tiers

Values share one vocabulary (`domain/lom/addressing/values.py`):

- **bool** (`mute`, `solo`, `metronome`…): `ON` / `OFF` / `TGL` (default)
- **continuous** (device parameters, pan, sends): absolute `x` · `x%` of the
  range · `<`/`>` steps (range/64) · `<x`/`>x` · `RND` · `RNDx-y` · `RESET`
- **quasi-continuous** (display units — BPM, dB): absolute · `<`/`>` · `<x`/`>x`
- **adjustable** (enumerated — monitoring, quantizations): option name or
  `<`/`>` cycling

A failed resolution raises `Protocol0Warning` with the candidates, surfaced as
a clean `500 {"status": "error"}`.

## Reacting to events

Return a `{EventType: handler}` map from `register_listeners()`; the loader
subscribes them after `start()` and unsubscribes on disconnect — you never call
`DomainEventBus` yourself. Each handler receives the event instance (payload as
attributes).

```python
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent

class MyPlugin(PluginInterface):
    name = "my_plugin"

    def register_listeners(self):
        return {SongStartedEvent: self._on_play}

    def _on_play(self, _: SongStartedEvent):
        ...
```

Events are the `*Event.py` classes under `protocol0/domain/` — subscribe to the
type, not a name. See
[`PluginInterface.register_listeners`](../src/remote-script/protocol0/application/plugin/PluginInterface.py)
for the contract.

## Binding control-surface encoders

Override `register_encoders()`; the loader calls it right after `start()` with an
[`Encoders`](../src/remote-script/protocol0/application/control_surface/Encoders.py)
binder and disconnects everything automatically on stop. Each `add_encoder` wires
one physical encoder (channel is 1-indexed) to `on_press` / `on_long_press` /
`on_scroll` callbacks; pass `scroll_only=True` for rotation-only knobs (required
for CC 0). Scrolls are relative: the handler receives `go_next: bool`, not an
absolute value.

```python
class MyPlugin(PluginInterface):
    name = "my_plugin"

    def register_encoders(self, encoders: Encoders) -> None:
        encoders.add_encoder(
            channel=3, identifier=0, name="my knob",
            on_scroll=self._on_scroll, scroll_only=True,
        )

    def _on_scroll(self, go_next: bool) -> None:
        ...
```

Real example:
[`live_set/LiveSetPlugin.py`](../src/remote-script/protocol0/plugins/live_set/LiveSetPlugin.py)
maps the 8 EC4 encoders of channel 3 to the macros of the currently selected
device.

## Lifecycle

`should_start()` opts out (return `False` to skip the plugin); `start()` runs once
for setup; `stop()` for teardown. All optional — see the docstrings in
[`PluginInterface.py`](../src/remote-script/protocol0/application/plugin/PluginInterface.py).
