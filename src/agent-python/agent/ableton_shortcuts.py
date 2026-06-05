"""Curated catalog of native Ableton Live keyboard shortcuts (Live 12, Windows).

A `send_keys` binding lets the user trigger a native Live shortcut from their own
combo (e.g. ctrl+alt+q -> ctrl+n "New Live Set"). This module is the searchable,
named list the UI offers: each entry is a Live command with its native combo.

Hand-curated from the official manual (kept here so the picker works without Ableton
and so the data is versioned/reviewable):
    https://www.ableton.com/en/manual/live-keyboard-shortcuts/

Scope (deliberate, agreed with the user):
  - Windows / Ctrl side only (Mac/Cmd is a later port).
  - General shortcuts only. EXCLUDED: anything needing a mouse click/drag, the
    Editing-detail family, value-adjustment and momentary-latch shortcuts, and bare
    modifier-only entries.
  - Only combos whose main key is inside the shared canonical namespace
    (a-z, 0-9, f1-f12, and the named keys in `keymap`: space, tab, enter, esc,
    backspace, delete, arrows, home, end, pageup, pagedown). Combos on punctuation
    keys ([ ] , ? etc.) are omitted until the namespace covers them.

`keys` is in the canonical combo format (see `keymap`): lowercase, modifiers ordered
ctrl, alt, shift, win, then the key, joined by '+'. That is exactly what the emitter
replays, so what is listed here is what gets injected.
"""
from typing import Any, Dict, List


def _s(name: str, label: str, category: str, keys: str) -> Dict[str, str]:
    return {"name": name, "label": label, "category": category, "keys": keys}


# Each entry: name (stable id), label (verbatim from the manual), category, keys.
_SHORTCUTS: List[Dict[str, str]] = [
    # --- Showing and Hiding Views ---
    _s("full_screen", "Toggle Full Screen Mode", "Views", "f11"),
    _s("toggle_session_arrangement", "Toggle Session/Arrangement View", "Views", "tab"),
    _s("toggle_device_clip_view", "Toggle Between Device/Clip View", "Views", "f12"),
    _s("hotswap_mode", "Toggle Hot-Swap Mode", "Views", "q"),
    _s("show_browser", "Hide/Show Browser", "Views", "ctrl+alt+b"),
    _s("show_overview", "Hide/Show Overview", "Views", "ctrl+alt+o"),
    _s("show_in_out", "Hide/Show In/Out", "Views", "ctrl+alt+i"),
    _s("show_sends", "Hide/Show Sends", "Views", "ctrl+alt+s"),
    _s("show_mixer", "Hide/Show Mixer", "Views", "ctrl+alt+m"),
    _s("show_clip_view", "Hide/Show Clip View", "Views", "ctrl+alt+3"),
    _s("show_device_view", "Hide/Show Device View", "Views", "ctrl+alt+4"),
    _s("show_groove_pool", "Hide/Show the Groove Pool", "Views", "ctrl+alt+6"),
    _s("show_learn_view", "Hide/Show the Learn View", "Views", "ctrl+alt+7"),
    _s("close_window", "Close Window/Dialog", "Views", "esc"),

    # --- Working with Sets and the Program ---
    _s("new_live_set", "New Live Set", "Sets", "ctrl+n"),
    _s("open_live_set", "Open Live Set", "Sets", "ctrl+o"),
    _s("save_live_set", "Save Live Set", "Sets", "ctrl+s"),
    _s("save_live_set_as", "Save Live Set As…", "Sets", "ctrl+shift+s"),
    _s("quit_live", "Quit Live", "Sets", "ctrl+q"),
    _s("export_audio_video", "Export Audio/Video", "Sets", "ctrl+shift+r"),
    _s("export_midi_file", "Export MIDI File", "Sets", "ctrl+shift+e"),

    # --- Working with Devices and Plug-Ins ---
    _s("group_devices", "Group Devices", "Devices", "ctrl+g"),
    _s("ungroup_devices", "Ungroup Devices", "Devices", "ctrl+shift+g"),
    _s("show_plugin_window", "Show/Hide Plug-In Window", "Devices", "ctrl+alt+p"),
    _s("compare_device_ab", "Compare A/B: Switch Device State", "Devices", "p"),

    # --- Transport ---
    _s("play_stop", "Play from Start Marker/Stop", "Transport", "space"),
    _s("continue_play", "Continue Play from Stop Point", "Transport", "shift+space"),
    _s("stop_at_selection_end", "Stop Playback at End of Selection", "Transport", "ctrl+space"),
    _s("insert_marker_to_beginning", "Move Insert Marker to Beginning", "Transport", "home"),
    _s("record", "Record", "Transport", "f9"),
    _s("arm_recording_arrangement", "Arm Recording in Arrangement View", "Transport", "shift+f9"),
    _s("record_to_session", "Record to Session View", "Transport", "ctrl+shift+f9"),
    _s("back_to_arrangement", "Back to Arrangement", "Transport", "f10"),
    _s("toggle_track_1", "Activate/Deactivate Track 1", "Transport", "f1"),
    _s("toggle_track_2", "Activate/Deactivate Track 2", "Transport", "f2"),
    _s("toggle_track_3", "Activate/Deactivate Track 3", "Transport", "f3"),
    _s("toggle_track_4", "Activate/Deactivate Track 4", "Transport", "f4"),
    _s("toggle_track_5", "Activate/Deactivate Track 5", "Transport", "f5"),
    _s("toggle_track_6", "Activate/Deactivate Track 6", "Transport", "f6"),
    _s("toggle_track_7", "Activate/Deactivate Track 7", "Transport", "f7"),
    _s("toggle_track_8", "Activate/Deactivate Track 8", "Transport", "f8"),
    _s("toggle_metronome", "Toggle Metronome", "Transport", "o"),

    # --- Global Quantization ---
    _s("quantize_sixteenth", "Sixteenth-Note Quantization", "Quantization", "ctrl+6"),
    _s("quantize_eighth", "Eighth-Note Quantization", "Quantization", "ctrl+7"),
    _s("quantize_quarter", "Quarter-Note Quantization", "Quantization", "ctrl+8"),
    _s("quantize_one_bar", "1-Bar Quantization", "Quantization", "ctrl+9"),
    _s("quantize_off", "Quantization Off", "Quantization", "ctrl+0"),

    # --- Session View ---
    _s("launch_clip_slot", "Launch Selected Clip/Slot", "Session", "enter"),
    _s("select_all_clips", "Select All Clips/Slots", "Session", "ctrl+a"),
    _s("insert_scene", "Insert Scene", "Session", "ctrl+i"),
    _s("insert_captured_scene", "Insert Captured Scene", "Session", "ctrl+shift+i"),
    _s("capture_midi", "Capture MIDI", "Session", "ctrl+shift+c"),
    _s("jump_first_track_of_scene", "Jump to the First Track of the Current Scene",
       "Session", "home"),
    _s("jump_last_track_of_scene", "Jump to the Last Track of the Current Scene",
       "Session", "end"),

    # --- Arrangement View ---
    _s("consolidate_selection", "Consolidate Selection into Clip", "Arrangement", "ctrl+j"),
    _s("create_fade", "Create Fade/Crossfade", "Arrangement", "ctrl+alt+f"),
    _s("toggle_loop_brace", "Toggle Loop Brace", "Arrangement", "ctrl+l"),
    _s("select_loop_brace_contents", "Select Loop Brace Contents", "Arrangement", "ctrl+shift+l"),
    _s("insert_silence", "Insert Silence", "Arrangement", "ctrl+i"),
    _s("fold_unfold_tracks", "Fold/Unfold Selected Tracks", "Arrangement", "u"),
    _s("unfold_all_tracks", "Unfold All Tracks", "Arrangement", "alt+u"),

    # --- Browser ---
    _s("load_selected_browser_item", "Load Selected Item from Browser", "Browser", "enter"),
    _s("preview_selected_file", "Preview Selected File", "Browser", "shift+enter"),
    _s("search_in_browser", "Search in Browser", "Browser", "ctrl+f"),
    _s("similar_files_search", "Show Similar Files Using Similarity Search",
       "Browser", "ctrl+shift+f"),
    _s("show_filter_view", "Hide/Show Filter View", "Browser", "ctrl+alt+g"),

    # --- Commands for Tracks ---
    _s("insert_audio_track", "Insert Audio Track", "Tracks", "ctrl+t"),
    _s("insert_midi_track", "Insert MIDI Track", "Tracks", "ctrl+shift+t"),
    _s("insert_return_track", "Insert Return Track", "Tracks", "ctrl+alt+t"),
    _s("rename_track", "Rename Selected Track", "Tracks", "ctrl+r"),
    _s("arm_selected_tracks", "Arm Selected Tracks", "Tracks", "c"),
    _s("solo_selected_tracks", "Solo Selected Tracks", "Tracks", "s"),
    _s("freeze_tracks", "Freeze/Unfreeze Tracks", "Tracks", "ctrl+alt+shift+f"),

    # --- Audio Engine ---
    _s("toggle_audio_engine", "Turn Audio Engine On/Off", "Audio Engine", "ctrl+alt+shift+e"),
]

# Official manual the catalog is curated from (surfaced in the UI as "official doc").
DOC_URL = "https://www.ableton.com/en/manual/live-keyboard-shortcuts/"


def get_all() -> List[Dict[str, Any]]:
    return _SHORTCUTS
