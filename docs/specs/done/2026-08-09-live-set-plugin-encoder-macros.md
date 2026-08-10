# live_set plugin: EC4 encoders follow the selected device

*2026-08-09*

## Goal

For live performance: the 8 encoders of the EC4 group on MIDI channel 3
(CC 0-7) must always control the 8 macros of the device currently selected in
Live's UI, with no manual remapping.

## Decisions

1. **Extend the plugin system instead of adding another ActionGroup.** Plugins
   could not receive MIDI input (the `ButtonElement` + `component_guard`
   machinery was private to `application/control_surface/`). Rather than a new
   declarative `register_midi_bindings` dict bound to raw `ButtonElement`s, the
   existing `add_encoder` machinery is extracted from `ActionGroupInterface`
   into a reusable `Encoders` binder (`application/control_surface/Encoders.py`)
   so plugins get the full gesture vocabulary (press / long press / scroll)
   without subclassing `ActionGroupInterface`.
2. **New `PluginInterface.register_encoders(encoders)` hook** — called by the
   loader right after `start()`, torn down automatically on stop, symmetric
   with `register_listeners()`. `PluginLoader.load_and_start` now takes the
   control surface's `component_guard` (passed from `Protocol0._initialize`).
3. **Relative scroll, not absolute CC values.** `MultiEncoder`'s scroll only
   understands increments (`go_next = value == 1`), so the EC4 channel-3
   encoders stay in relative mode like the rest of the EC4 setup and macros
   move via `DeviceParameter.scroll(go_next)` (accelerating).
4. **`scroll_only` mode added to `MultiEncoder`** — a rotation-only encoder
   skips the press `ButtonElement`; required for CC 0, whose press note would
   be `identifier - 1 = -1`.
5. **Target = the device selected in the UI** (`Song.selected_device()`), not
   the first device of the selected track. The handler re-reads the selection
   on every tick, so no selection listener is needed (same pattern as
   `ActionGroupLaunchKeyMini`).
6. **Skip "Device On".** Encoder i drives `parameters[i + 1]`: `parameters[0]`
   is "Device On" and a knob on it would toggle the device mid-performance.

## Shipped as

- `application/control_surface/Encoders.py` — extracted binder; channel
  1-indexed,
  duplicate `(channel, cc)` asserted, `disconnect()` tears everything down.
- `application/control_surface/MultiEncoder.py` — `scroll_only` param.
- `application/control_surface/ActionGroupInterface.py` — delegates to
  `Encoders`, public `add_encoder` signature unchanged.
- `application/plugin/PluginInterface.py` / `PluginLoader.py` — the hook and
  its lifecycle wiring.
- `plugins/live_set/LiveSetPlugin.py` — the feature itself (8 encoders,
  channel 3, CC 0-7).
- Docs: `docs/plugins.md` ("Binding control-surface encoders" section),
  `plugins/example/ExamplePlugin.py` (third declarative example).
