# Ableton shortcuts catalog — reconciliation (AHK inventory → Protocol0 catalog)

**Status:** validated; catalog patched (`src/agent/src/ableton_shortcuts.rs`, 74 → ~131 entries),
namespace extended to punctuation, conflict UI added. See "Direction" below.

## Direction — key remapping is inherently conflict-prone

Live reuses the same native keystroke across contexts (ctrl+i = insert scene / insert silence /
insert warp marker; ctrl+g = group devices / group notes). A `send_keys` remap injects ONE keystroke,
so it drives whatever Live's current context binds — we can surface the overlap (the conflict UI:
`nativePeers` → modal warning + list badge) but not resolve it, because the ambiguity is Live's.
This is why the longer-term direction is to move a growing share of actions to **API calls handled by
the remote script** (plugin `@action` → `POST /api/action/...`), which are context-explicit and far
less brittle than replaying keystrokes. The keystroke catalog stays as the fallback for the many
native commands with no LOM/API equivalent.

## Why

The third-party AutoHotkey project
[Ableton-custom-shortcuts-manager-windows](https://github.com/nyxandro/Ableton-custom-shortcuts-manager-windows)
ships a list of **127 native Live 12 commands**. Protocol0's own catalog has **74**. We use the
AHK list purely as a **completeness inventory** (only command *names* — facts, not its code; the
repo has no licence). The **official Ableton manual** stays the source of truth for wording and the
native combo.

This document reconciles the two lists so you can validate **what gets added, split, dropped, or
flagged** before any code change. Decisions already taken:
- double-combo AHK entries → **split** into two entries;
- new categories → **added** where the manual structure warrants;
- the canonical namespace has been **extended to punctuation** `, [ ] = -` (chantier A, done), so
  punctuation shortcuts are now mappable and are **kept**, not dropped.

Canonical `keys` format: lowercase; modifiers ordered `ctrl alt shift win`; then the key; joined by
`+`. Punctuation named by its unshifted glyph.

---

## (c) Duplicates of the existing 74 — SKIP (already present)

These AHK entries already exist in the catalog (matched by combo + meaning). Not re-added.

| AHK command | combo | existing `name` |
|---|---|---|
| Export Audio/Video | ctrl+shift+r | `export_audio_video` |
| Export MIDI File | ctrl+shift+e | `export_midi_file` |
| Hide/Show Browser | ctrl+alt+b | `show_browser` |
| Hide/Show Overview | ctrl+alt+0 → see (e) | `show_overview` (combo conflict, see (e)) |
| Hide/Show In/Out | ctrl+alt+i | `show_in_out` |
| Hide/Show Sends | ctrl+alt+s | `show_sends` |
| Hide/Show Mixer | ctrl+alt+m | `show_mixer` |
| Hide/Show Clip View | ctrl+alt+3 | `show_clip_view` |
| Hide/Show Device View | ctrl+alt+4 | `show_device_view` |
| Hide/Show the Groove Pool | ctrl+alt+6 | `show_groove_pool` |
| New Live Set | ctrl+n | `new_live_set` |
| Open Live Set | ctrl+o | `open_live_set` |
| Save Live Set | ctrl+s | `save_live_set` |
| Save Live Set As | ctrl+shift+s | `save_live_set_as` |
| Quit Live | ctrl+q | `quit_live` |
| Group Devices/Tracks | ctrl+g | `group_devices` |
| Ungroup Devices/Tracks | ctrl+shift+g | `ungroup_devices` |
| Show/Hide Plug-In Window | ctrl+alt+p | `show_plugin_window` |
| Select All Notes | ctrl+a | `select_all_clips` (combo conflict — see (e)) |
| Capture MIDI | ctrl+shift+c | `capture_midi` |
| Select Material in Loop | ctrl+shift+l | `select_loop_brace_contents` |
| Insert Warp Marker | ctrl+i | `insert_scene` / `insert_silence` (combo conflict — see (e)) |
| Insert Transient | ctrl+shift+i | `insert_captured_scene` (combo conflict — see (e)) |
| Consolidate Selection into Clip | ctrl+j | `consolidate_selection` |
| Create Fade/Crossfade | ctrl+alt+f | `create_fade` |
| Toggle Loop Brace | ctrl+l | `toggle_loop_brace` |
| Unfold All Tracks | alt+u | `unfold_all_tracks` |
| Preview Selected File | shift+enter | `preview_selected_file` |
| Search in Browser | ctrl+f | `search_in_browser` |
| Insert Audio Track | ctrl+t | `insert_audio_track` |
| Insert MIDI Track | ctrl+shift+t | `insert_midi_track` |
| Insert Return Track | ctrl+alt+t | `insert_return_track` |
| Rename Selected Track | ctrl+r | `rename_track` |
| Freeze/Unfreeze Tracks | ctrl+alt+shift+f | `freeze_tracks` |
| Continue Play from Stop | shift+space | `continue_play` |
| Arm Recording in Arrangement | shift+f9 | `arm_recording_arrangement` |
| Record to Session View | ctrl+shift+f9 | `record_to_session` |
| Turn Audio Engine On/Off | ctrl+alt+shift+e | `toggle_audio_engine` |
| Eighth-Note Quantization | ctrl+7 | `quantize_eighth` |
| Quarter-Note Quantization | ctrl+8 | `quantize_quarter` |
| 1-Bar Quantization | ctrl+9 | `quantize_one_bar` |
| Quantization Off | ctrl+0 | `quantize_off` |

---

## (e) CONFLICTS — RESOLVED (user arbitration, manual-verified)

I do **not** overwrite an existing entry (its `name` may carry a user binding). All decisions below
are final and reflected in the add-tables. Shared-`keys` entries are intentional and handled by the
new conflict UI (chantier C).

| Topic | Existing catalog | Decision |
|---|---|---|
| Device/Clip view toggle | `toggle_device_clip_view` = **f12** | **Keep f12.** Both valid; we keep f12. |
| Hide/Show Overview | `show_overview` = **ctrl+alt+o** | **Keep ctrl+alt+o.** AHK `ctrl+alt+0` confirmed a typo. |
| Learn view | `show_learn_view` = ctrl+alt+7 | **Keep.** Separate from `focus_learn_view` (alt+7) — different combo, both kept. |
| Insert Warp Marker | shares ctrl+i with `insert_scene`/`insert_silence` | **ADD** `insert_warp_marker` = ctrl+i (manual §41.11). Intentional shared combo. |
| Insert Transient | shares ctrl+shift+i with `insert_captured_scene` | **ADD** `insert_transient` = ctrl+shift+i (manual §41.11). |
| Select All Notes | shares ctrl+a with `select_all_clips` | **ADD** `select_all_notes` = ctrl+a (manual §41.12). |
| Group Notes (Play All) | shares ctrl+g with `group_devices` | **ADD** `group_notes` = ctrl+g (manual §41.12, verified). |
| Ungroup Notes | shares ctrl+shift+g with `ungroup_devices` | **ADD** `ungroup_notes` = ctrl+shift+g (manual §41.12, verified). |

---

## (b) Bidirectional manual entries — SPLIT into two

The manual writes these as ONE bidirectional command (e.g. "Halve/Double Loop Length — Ctrl up/down").
A `send_keys` binding emits one combo, so we split each into two entries with one combo each.
Directions are taken **verbatim from the manual** (§ noted). ⚠️ **These labels are therefore
*derived*, not verbatim** — half of a bidirectional manual label. Acceptable (the meaning is exact)
but flagged so we don't claim verbatim where we adapted.

| Manual entry (verbatim) | → entry 1 | → entry 2 |
|---|---|---|
| Halve/Double Loop Length — Ctrl up/down (§41.8) | `loop_halve` "Halve Loop Length" — ctrl+up | `loop_double` "Double Loop Length" — ctrl+down |
| Shorten/Lengthen Loop — Ctrl **right/left** (§41.8) | `loop_shorten` "Shorten Loop" — ctrl+right | `loop_lengthen` "Lengthen Loop" — ctrl+left |
| Move Clip Region with Start Marker — Shift **right/left** (§41.11/12) | `move_clip_region_right` — shift+right | `move_clip_region_left` — shift+left |
| Select Next/Previous Note — Alt up/down (§41.12) | `select_next_note` "Select Next Note" — alt+up | `select_prev_note` "Select Previous Note" — alt+down |
| Select Next/Previous Note in Same Key Track — Alt left/right (§41.12) | `select_next_note_key` — alt+left | `select_prev_note_key` — alt+right |
| Adjust Note Selection Velocity Deviation — Ctrl+Shift up/down (§41.12) | `note_velocity_up` — ctrl+shift+up | `note_velocity_down` — ctrl+shift+down |
| Adjust Note Selection Chance — Ctrl+Alt up/down (§41.12) | `note_chance_up` — ctrl+alt+up | `note_chance_down` — ctrl+alt+down |
| Pan Left/Right of Selection — Ctrl+Alt left/right (§41.9) | `pan_selection_left` — ctrl+alt+left | `pan_selection_right` — ctrl+alt+right |
| Scroll Editor Vertically — Page Up/Down (§41.12) | `scroll_editor_up` — pageup | `scroll_editor_down` — pagedown |
| Scroll Editor Horizontally — Ctrl Page Up/Down (§41.12) | `scroll_editor_left` — ctrl+pageup | `scroll_editor_right` — ctrl+pagedown |
| Adjust Height of Selected Tracks/Clips — Alt+/Alt− (§41.16) | `track_height_increase` — alt+= | `track_height_decrease` — alt+- |

> **Note — split labels are derived.** Verbatim manual wording is on the left; the per-direction
> labels on the right are our adaptation. The `name`s are new and unique.
>
> **Dropped per your call (too specific / arrow-combo collisions):** Move Selected Track Left/Right,
> Move Nonadjacent Scenes, Replace Main Take Clip — all reuse `ctrl+left/right/up/down` already taken
> by the loop-edit entries. Not added.
>
> ⚠️ **`scroll_editor_up`/`down` = bare `pageup`/`pagedown`** (no modifier). A no-modifier trigger
> is unusual for a remap and easy to fire by accident — fine to catalog (it's the native combo) but
> the user would rarely map a plain PageUp. Noted, not dropped.

---

## (d) NEW categories + (a) entries to ADD

New category groups appear at the bottom of the picker (frontend groups by catalog order).

### New category: **MIDI Editing**
All labels verified verbatim against the manual (§41.12 unless noted).
| name | label | keys |
|---|---|---|
| `fit_notes_to_time` | Fit Notes to Time Range | ctrl+alt+j |
| `group_notes` | Group Notes (Play All) | ctrl+g _(shares with `group_devices` — your call, manual-confirmed)_ |
| `ungroup_notes` | Ungroup Notes | ctrl+shift+g _(shares with `ungroup_devices`)_ |
| `select_all_notes` | Select All Notes | ctrl+a _(shares with `select_all_clips`)_ |
| `apply_midi_tool` | Apply Current MIDI Tool Settings | ctrl+enter |
| `invert_note_selection` | Invert Note Selection | ctrl+shift+a |
| `toggle_full_clip_view` | Toggle Full-Size Clip View | ctrl+alt+e |
| `create_follow_action_chain` | Create Follow Action Chain _(§41.15 Session)_ | ctrl+shift+enter |
| + the split note-edit entries from (b): `select_next_note`, `select_prev_note`, `select_next_note_key`, `select_prev_note_key`, `note_velocity_up/down`, `note_chance_up/down` |

### New category: **Grid**
| name | label | keys |
|---|---|---|
| `grid_narrow` | Narrow Grid | ctrl+1 |
| `grid_widen` | Widen Grid | ctrl+2 |
| `grid_triplet` | Triplet Grid | ctrl+3 |
| `grid_snap` | Snap to Grid | ctrl+4 |
| `grid_fixed_adaptive` | Fixed/Zoom-Adaptive Grid | ctrl+5 |

### New category: **Take Lanes** (§41.17 Comping)
| name | label | keys |
|---|---|---|
| `show_take_lanes` | Show Take Lanes | ctrl+alt+u |
| `add_take_lane` | Add Take Lane | shift+alt+t |
| ~~`duplicate_take_lane`~~ | ~~Duplicate Selected Take Lane~~ | **DROPPED** — ctrl+d too generic (your call) |

### New category: **Editing / Time**
| name | label | keys |
|---|---|---|
| `split_clip` | Split Clip at Selection | ctrl+e |
| `crop_clip` | Crop Selected Clips | ctrl+shift+j |
| `duplicate_time` | Duplicate Time | ctrl+shift+d |
| `cut_time` | Cut Time | ctrl+shift+x |
| `paste_time` | Paste Time | ctrl+shift+v |
| `delete_time` | Delete Time | ctrl+shift+delete |
| `quantize` | Quantize | ctrl+u |
| `quantize_settings` | Quantize Settings… | ctrl+shift+u _(manual uses the ellipsis)_ |
| + split loop-edit entries from (b): `loop_halve/double`, `loop_shorten/lengthen`, `move_clip_region_left/right`, `pan_selection_left/right`, `scroll_editor_*` |

### New category: **Focus** (Move Focus to … family — §41.2; labels verbatim, note the "the")
| name | label | keys |
|---|---|---|
| `focus_control_bar` | Move Focus to the Control Bar | alt+0 |
| `focus_session` | Move Focus to the Session View | alt+1 |
| `focus_arrangement` | Move Focus to the Arrangement View | alt+2 |
| `focus_clip_view` | Move Focus to the Clip View | alt+3 |
| `focus_device_view` | Move Focus to the Device View | alt+4 |
| `focus_browser` | Move Focus to the Browser | alt+5 |
| `focus_groove_pool` | Move Focus to the Groove Pool | alt+6 |
| `focus_learn_view` | Move Focus to the Learn View | alt+7 _(manual: Learn, not "Help" — AHK was wrong; combo alt+7 ≠ existing `show_learn_view` ctrl+alt+7, no conflict)_ |
| `focus_selected_clip_panel` | Move Focus to the Selected Clip Panel | alt+8 |
| `focus_clip_panels` | Move Focus to the Clip Panels | alt+shift+p |
| `focus_mixer` | Move Focus to Mixer | alt+shift+m _(§41.16, no "the")_ |

### Add to EXISTING categories
All labels below verified verbatim against the manual. **Corrections vs the AHK wording are flagged.**
| category | name | label | keys |
|---|---|---|---|
| Views | `toggle_second_window` | Toggle Second Window | ctrl+shift+w |
| Views | `open_settings` | Open the Settings | ctrl+, |
| Sets | `bounce_to_new_track` | Bounce to New Track | ctrl+b |
| Browser | `browser_history_back` | Browser History Back | ctrl+[ |
| Browser | `browser_history_forward` | Browser History Forward | ctrl+] |
| ~~Browser~~ | ~~`show_return_tracks`~~ | ~~Show/Hide Return Tracks~~ | **DROPPED — NOT FOUND in manual** (AHK invented it) |
| Devices | `edit_midi_map` | Toggle MIDI Map Mode | ctrl+m _(manual says "Toggle … Mode", not AHK's "Edit MIDI Map")_ |
| Devices | `edit_key_map` | Toggle Key Map Mode | ctrl+k _(manual: "Toggle … Mode")_ |
| Transport | `move_insert_to_playhead` | Move Insert Marker to Playhead Position | ctrl+shift+space _(manual adds "Position")_ |
| Session | `insert_midi_clip` | Insert MIDI Clip | ctrl+shift+m _(manual: "Insert MIDI Clip" §41.15 — NOT "Insert Empty MIDI Clip"; category Session, not Arrangement)_ |
| Arrangement | `delete_fades` | Delete Fades/Crossfades in Selected Clip(s) | ctrl+alt+backspace _(manual full wording)_ |
| Arrangement | `set_start_marker` | Set Start Marker | ctrl+f9 |
| Arrangement | `set_loop_start` | Set Loop Brace Start | ctrl+f10 |
| Arrangement | `set_loop_end` | Set Loop Brace End | ctrl+f11 |
| Arrangement | `set_end_marker` | Set End Marker | ctrl+f12 |

> **Zoom (verified):** manual labels are **"Zoom In Window"** (Ctrl+Plus) and **"Zoom Out Window"**
> (Ctrl+Minus), §41.9. `zoom_out` = `ctrl+-` is clean. "Plus" = Shift+`=` on US → `zoom_in` =
> `ctrl+shift+=`. Add both; verify the zoom-in round-trip in Ableton before shipping the value.
> Categorize under **Views** (or a small **Zoom** group).

---

## DROPPED (final)

- `show_return_tracks` — **not in the manual** (AHK invented). Removed.
- `duplicate_take_lane` (ctrl+d) — too generic (your call). Removed.
- Move Selected Track / Move Nonadjacent Scenes / Replace Main Take Clip — arrow-combo collisions
  with loop-edit (your call). Removed.
- Nothing dropped for namespace reasons: `, [ ] = -` are now supported.

## Label corrections applied (AHK wording → manual verbatim)

- "Edit MIDI Map" → **"Toggle MIDI Map Mode"**; "Edit Key Map" → **"Toggle Key Map Mode"**.
- "Apply Current MIDI Tool" → **"Apply Current MIDI Tool Settings"**.
- "Move Insert Marker To Playhead" → **"Move Insert Marker to Playhead Position"**.
- "Insert Empty MIDI Clip" → **"Insert MIDI Clip"** (category Session, not Arrangement).
- "Delete Fades/Crossfades" → **"Delete Fades/Crossfades in Selected Clip(s)"**.
- "Quantize Settings" → **"Quantize Settings…"** (ellipsis).
- "Move Focus to X" → **"Move Focus to the X"** for the Alt+0–8 family; "Help View" → **"Learn View"**.
- Split-entry labels are *derived* halves of bidirectional manual entries (flagged in (b)).

## Counts (after arbitration)

- Existing: **74**
- New entries to ADD (incl. ~11 split pairs): **~50**
- Dropped: **5** topics
- Shared-`keys` entries (intentional, handled by chantier C): ctrl+i, ctrl+shift+i, ctrl+a,
  ctrl+g, ctrl+shift+g.

→ Catalog grows from 74 to roughly **120**.

**All wording verified against the official manual. Ready for the B.2 catalog patch.**
