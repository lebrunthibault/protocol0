# Creating a plugin

A **plugin** extends the remote script: it can register new **actions** (bindable to a
shortcut) and/or **reacts to events** in Live.

To create a plugin, just drop a `.py` file in `src/script/protocol0/plugins/`, subclass `PluginInterface`, done.

```
src/script/protocol0/plugins/
├── LoadDevicePlugin.py   ← single-file plugin
├── example/              ← copy this to start your own
│   └── ExamplePlugin.py
└── live_set/             ← multi-file plugin (package)
```

## Adding an action

Decorate a method with
[`@action`](../src/script/protocol0/application/plugin/action.py) — no argument. The
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
[`Router.py`](../src/script/protocol0/application/http/Router.py) for how it's
dispatched. Real example:
[`LoadDevicePlugin.py`](../src/script/protocol0/plugins/LoadDevicePlugin.py).

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
[`PluginInterface.register_listeners`](../src/script/protocol0/application/plugin/PluginInterface.py)
for the contract.

## Lifecycle

`should_start()` opts out (return `False` to skip the plugin); `start()` runs once
for setup; `stop()` for teardown. All optional — see the docstrings in
[`PluginInterface.py`](../src/script/protocol0/application/plugin/PluginInterface.py).
