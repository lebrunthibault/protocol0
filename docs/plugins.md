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

Annotate the real return type; over HTTP the action stays fire-and-forget (the
caller gets `200` immediately) whatever it returns.

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
