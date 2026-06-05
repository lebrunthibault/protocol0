//! Curated catalog of native Ableton Live keyboard shortcuts (Live 12, Windows) — mechanical
//! port of agent/ableton_shortcuts.py.
//!
//! A `send_keys` binding lets the user trigger a native Live shortcut from their own combo
//! (e.g. ctrl+alt+q -> ctrl+n "New Live Set"). This module is the searchable, named list the
//! UI offers: each entry is a Live command with its native combo.
//!
//! Hand-curated from the official manual (kept here so the picker works without Ableton and so
//! the data is versioned/reviewable):
//!     https://www.ableton.com/en/manual/live-keyboard-shortcuts/
//!
//! Scope (deliberate, agreed with the user): Windows / Ctrl side only; general shortcuts only;
//! only combos whose main key is inside the shared canonical namespace (see keymap).
//!
//! `keys` is in the canonical combo format (see keymap): lowercase, modifiers ordered
//! ctrl, alt, shift, win, then the key, joined by '+'. That is exactly what the emitter
//! replays, so what is listed here is what gets injected.

use serde::Serialize;

/// Official manual the catalog is curated from (surfaced in the UI as "official doc").
pub const DOC_URL: &str = "https://www.ableton.com/en/manual/live-keyboard-shortcuts/";

#[derive(Serialize)]
pub struct Shortcut {
    pub name: &'static str,
    pub label: &'static str,
    pub category: &'static str,
    pub keys: &'static str,
}

const fn s(
    name: &'static str,
    label: &'static str,
    category: &'static str,
    keys: &'static str,
) -> Shortcut {
    Shortcut {
        name,
        label,
        category,
        keys,
    }
}

/// Each entry: name (stable id), label (verbatim from the manual), category, keys.
pub fn get_all() -> Vec<Shortcut> {
    vec![
        // --- Showing and Hiding Views ---
        s("full_screen", "Toggle Full Screen Mode", "Views", "f11"),
        s("toggle_session_arrangement", "Toggle Session/Arrangement View", "Views", "tab"),
        s("toggle_device_clip_view", "Toggle Between Device/Clip View", "Views", "f12"),
        s("hotswap_mode", "Toggle Hot-Swap Mode", "Views", "q"),
        s("show_browser", "Hide/Show Browser", "Views", "ctrl+alt+b"),
        s("show_overview", "Hide/Show Overview", "Views", "ctrl+alt+o"),
        s("show_in_out", "Hide/Show In/Out", "Views", "ctrl+alt+i"),
        s("show_sends", "Hide/Show Sends", "Views", "ctrl+alt+s"),
        s("show_mixer", "Hide/Show Mixer", "Views", "ctrl+alt+m"),
        s("show_clip_view", "Hide/Show Clip View", "Views", "ctrl+alt+3"),
        s("show_device_view", "Hide/Show Device View", "Views", "ctrl+alt+4"),
        s("show_groove_pool", "Hide/Show the Groove Pool", "Views", "ctrl+alt+6"),
        s("show_learn_view", "Hide/Show the Learn View", "Views", "ctrl+alt+7"),
        s("close_window", "Close Window/Dialog", "Views", "esc"),
        // --- Working with Sets and the Program ---
        s("new_live_set", "New Live Set", "Sets", "ctrl+n"),
        s("open_live_set", "Open Live Set", "Sets", "ctrl+o"),
        s("save_live_set", "Save Live Set", "Sets", "ctrl+s"),
        s("save_live_set_as", "Save Live Set As…", "Sets", "ctrl+shift+s"),
        s("quit_live", "Quit Live", "Sets", "ctrl+q"),
        s("export_audio_video", "Export Audio/Video", "Sets", "ctrl+shift+r"),
        s("export_midi_file", "Export MIDI File", "Sets", "ctrl+shift+e"),
        // --- Working with Devices and Plug-Ins ---
        s("group_devices", "Group Devices", "Devices", "ctrl+g"),
        s("ungroup_devices", "Ungroup Devices", "Devices", "ctrl+shift+g"),
        s("show_plugin_window", "Show/Hide Plug-In Window", "Devices", "ctrl+alt+p"),
        s("compare_device_ab", "Compare A/B: Switch Device State", "Devices", "p"),
        // --- Transport ---
        s("play_stop", "Play from Start Marker/Stop", "Transport", "space"),
        s("continue_play", "Continue Play from Stop Point", "Transport", "shift+space"),
        s("stop_at_selection_end", "Stop Playback at End of Selection", "Transport", "ctrl+space"),
        s("insert_marker_to_beginning", "Move Insert Marker to Beginning", "Transport", "home"),
        s("record", "Record", "Transport", "f9"),
        s("arm_recording_arrangement", "Arm Recording in Arrangement View", "Transport", "shift+f9"),
        s("record_to_session", "Record to Session View", "Transport", "ctrl+shift+f9"),
        s("back_to_arrangement", "Back to Arrangement", "Transport", "f10"),
        s("toggle_track_1", "Activate/Deactivate Track 1", "Transport", "f1"),
        s("toggle_track_2", "Activate/Deactivate Track 2", "Transport", "f2"),
        s("toggle_track_3", "Activate/Deactivate Track 3", "Transport", "f3"),
        s("toggle_track_4", "Activate/Deactivate Track 4", "Transport", "f4"),
        s("toggle_track_5", "Activate/Deactivate Track 5", "Transport", "f5"),
        s("toggle_track_6", "Activate/Deactivate Track 6", "Transport", "f6"),
        s("toggle_track_7", "Activate/Deactivate Track 7", "Transport", "f7"),
        s("toggle_track_8", "Activate/Deactivate Track 8", "Transport", "f8"),
        s("toggle_metronome", "Toggle Metronome", "Transport", "o"),
        // --- Global Quantization ---
        s("quantize_sixteenth", "Sixteenth-Note Quantization", "Quantization", "ctrl+6"),
        s("quantize_eighth", "Eighth-Note Quantization", "Quantization", "ctrl+7"),
        s("quantize_quarter", "Quarter-Note Quantization", "Quantization", "ctrl+8"),
        s("quantize_one_bar", "1-Bar Quantization", "Quantization", "ctrl+9"),
        s("quantize_off", "Quantization Off", "Quantization", "ctrl+0"),
        // --- Session View ---
        s("launch_clip_slot", "Launch Selected Clip/Slot", "Session", "enter"),
        s("select_all_clips", "Select All Clips/Slots", "Session", "ctrl+a"),
        s("insert_scene", "Insert Scene", "Session", "ctrl+i"),
        s("insert_captured_scene", "Insert Captured Scene", "Session", "ctrl+shift+i"),
        s("capture_midi", "Capture MIDI", "Session", "ctrl+shift+c"),
        s("jump_first_track_of_scene", "Jump to the First Track of the Current Scene", "Session", "home"),
        s("jump_last_track_of_scene", "Jump to the Last Track of the Current Scene", "Session", "end"),
        // --- Arrangement View ---
        s("consolidate_selection", "Consolidate Selection into Clip", "Arrangement", "ctrl+j"),
        s("create_fade", "Create Fade/Crossfade", "Arrangement", "ctrl+alt+f"),
        s("toggle_loop_brace", "Toggle Loop Brace", "Arrangement", "ctrl+l"),
        s("select_loop_brace_contents", "Select Loop Brace Contents", "Arrangement", "ctrl+shift+l"),
        s("insert_silence", "Insert Silence", "Arrangement", "ctrl+i"),
        s("fold_unfold_tracks", "Fold/Unfold Selected Tracks", "Arrangement", "u"),
        s("unfold_all_tracks", "Unfold All Tracks", "Arrangement", "alt+u"),
        // --- Browser ---
        s("load_selected_browser_item", "Load Selected Item from Browser", "Browser", "enter"),
        s("preview_selected_file", "Preview Selected File", "Browser", "shift+enter"),
        s("search_in_browser", "Search in Browser", "Browser", "ctrl+f"),
        s("similar_files_search", "Show Similar Files Using Similarity Search", "Browser", "ctrl+shift+f"),
        s("show_filter_view", "Hide/Show Filter View", "Browser", "ctrl+alt+g"),
        // --- Commands for Tracks ---
        s("insert_audio_track", "Insert Audio Track", "Tracks", "ctrl+t"),
        s("insert_midi_track", "Insert MIDI Track", "Tracks", "ctrl+shift+t"),
        s("insert_return_track", "Insert Return Track", "Tracks", "ctrl+alt+t"),
        s("rename_track", "Rename Selected Track", "Tracks", "ctrl+r"),
        s("arm_selected_tracks", "Arm Selected Tracks", "Tracks", "c"),
        s("solo_selected_tracks", "Solo Selected Tracks", "Tracks", "s"),
        s("freeze_tracks", "Freeze/Unfreeze Tracks", "Tracks", "ctrl+alt+shift+f"),
        // --- Audio Engine ---
        s("toggle_audio_engine", "Turn Audio Engine On/Off", "Audio Engine", "ctrl+alt+shift+e"),
    ]
}
