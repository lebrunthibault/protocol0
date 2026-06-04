# Creating a smart action

A **smart action** is the simplest way to add a new action to Protocol0. It is a
named, parameterizable unit you can bind to a keyboard shortcut — just like the
built-in actions (`load_device`, …) — but with **no plugin to write**.

If you only want to *do something* on a keypress (call the Live API, run a bit of
logic), reach for a smart action. If you also need to **react to events in Live**
(a clip recorded, playback started) or expose a richer HTTP surface, write a full
[plugin](plugins.md) instead.

> Like the rest of the remote script, smart actions run under Ableton's
> **restricted, stdlib-only** embedded Python, and must **never block** Live's
> thread — see [Constraints](#constraints).

> **Not a programmer?** Smart actions are Python, but you don't have to write the
> code by hand. Describe what you want to an AI coding assistant (ChatGPT, Claude,
> Cursor…), point it at the [example](#a-minimal-example), and let it produce the
> file — then drop it in the folder below.

## Smart action vs. plugin

| | Smart action | [Plugin](plugins.md) |
|---|---|---|
| You write | one class, one method | a `PluginInterface` subclass |
| React to Live events | ✗ | ✓ (`register_listeners`) |
| Expose an action / shortcut | ✓ | ✓ (`register_actions`) |
| Discovered automatically | ✓ | ✓ |
| Best for | "do X on this key" | event-driven or multi-action behavior |

A smart action is, in effect, a one-action plugin with the boilerplate removed.
Anything a smart action can do, a plugin can do too — the smart action just
spares you the interface when a single action is all you need.

## The interface

You write a smart action by subclassing `SmartActionInterface`. It is deliberately
tiny: a configurable **name** and a single **`run`** method.

```python
class SmartActionInterface:
    name: str = ""           # the action's name, shown in the shortcut UI

    def run(self) -> None: ...   # what the action does
```

> **Why `run` and not `execute`?** A smart action is meant to read as "this name
> runs this code". `run` is shorter, matches the mental model (you *run* an
> action), and keeps the one-method interface as light as the concept. `execute`
> would carry more ceremony than the abstraction deserves.

That is the whole contract: give it a `name`, implement `run`. The loader
discovers it, registers it in the action catalog (so it shows up in the shortcut
web UI), and lets you bind it to a key.

## Where smart actions live

Smart actions are Python modules under:

```
src/script/protocol0/smart_actions/
├── example/          ← copy this to start your own
│   └── ExampleSmartAction.py
└── ...
```

They are **discovered automatically**: at startup the loader imports the
`smart_actions` package and registers every subclass of `SmartActionInterface` it
finds. There is no registry to edit — drop a file in, subclass
`SmartActionInterface`, done.

If you installed Protocol0 with the installer (rather than running from source),
the same package lives inside Ableton's remote-scripts folder — drop your file
there instead:

```
C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts\Protocol_0\protocol0\smart_actions\
```

Restart Ableton afterward so the new action is picked up.

## A minimal example

```python
from protocol0.application.smart_action.SmartActionInterface import (
    SmartActionInterface,
)
from protocol0.shared.logging.StatusBar import StatusBar


class HelloSmartAction(SmartActionInterface):
    name = "hello"

    def run(self) -> None:
        """Show a greeting in Live's status bar."""
        StatusBar.show_message("Hello from a smart action!")
```

Save that file under `src/script/protocol0/smart_actions/`, redeploy the script,
and `hello` appears in the shortcut catalog at
<http://127.0.0.1:9010/shortcuts> — bind it to any combo.

### Touching the Live API

The action's `run` is invoked on Live's thread, so it's safe to call the Live API
from it. Resolve services through the container, exactly like the core actions and
plugins do:

```python
from protocol0.application.smart_action.SmartActionInterface import (
    SmartActionInterface,
)
from protocol0.shared.Config import get_container


class SelectFirstTrackSmartAction(SmartActionInterface):
    name = "select_first_track"

    def run(self) -> None:
        song = get_container().get(Song)
        song.select_track(song.tracks[0])
```

## Smart action or plugin — once more

- Need to **listen** for something happening in Live? That's a plugin
  (`register_listeners`). A smart action only fires when its shortcut is pressed.
- Need **several related actions**, or shared setup/teardown? A plugin groups them
  and gives you `start`/`stop`. A smart action is intentionally one action with no
  lifecycle.
- Otherwise, prefer the smart action — it's less to write and just as
  discoverable.

See the full plugin guide in [`docs/plugins.md`](plugins.md).

## Constraints

- **Stdlib-only.** Ableton's embedded Python can't load third-party packages.
- **Never block Live's thread.** Don't sleep or do long work in `run`; keep it
  short.
- **One failing smart action won't take the script down.** The loader isolates
  each registration in a `try/except`, so a broken action is logged and skipped.

## Trying it out

After adding a smart action, redeploy the script into Ableton and reload:

```sh
make install     # copies the remote script into Ableton's Remote Scripts
```

Then check `%APPDATA%\Protocol0\logs\` for `Smart action <name> registered`, open
the shortcut UI to bind it, and press your combo (with Ableton in the foreground)
to confirm it fires.
