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
        s("toggle_second_window", "Toggle Second Window", "Views", "ctrl+shift+w"),
        s("open_settings", "Open the Settings", "Views", "ctrl+,"),
        s("zoom_in_window", "Zoom In Window", "Views", "ctrl+shift+="),
        s("zoom_out_window", "Zoom Out Window", "Views", "ctrl+-"),
        // --- Working with Sets and the Program ---
        s("new_live_set", "New Live Set", "Sets", "ctrl+n"),
        s("open_live_set", "Open Live Set", "Sets", "ctrl+o"),
        s("save_live_set", "Save Live Set", "Sets", "ctrl+s"),
        s("save_live_set_as", "Save Live Set As…", "Sets", "ctrl+shift+s"),
        s("quit_live", "Quit Live", "Sets", "ctrl+q"),
        s("export_audio_video", "Export Audio/Video", "Sets", "ctrl+shift+r"),
        s("export_midi_file", "Export MIDI File", "Sets", "ctrl+shift+e"),
        s("bounce_to_new_track", "Bounce to New Track", "Sets", "ctrl+b"),
        // --- Working with Devices and Plug-Ins ---
        s("group_devices", "Group Devices", "Devices", "ctrl+g"),
        s("ungroup_devices", "Ungroup Devices", "Devices", "ctrl+shift+g"),
        s("show_plugin_window", "Show/Hide Plug-In Window", "Devices", "ctrl+alt+p"),
        s("compare_device_ab", "Compare A/B: Switch Device State", "Devices", "p"),
        s("toggle_midi_map_mode", "Toggle MIDI Map Mode", "Devices", "ctrl+m"),
        s("toggle_key_map_mode", "Toggle Key Map Mode", "Devices", "ctrl+k"),
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
        s("move_insert_to_playhead", "Move Insert Marker to Playhead Position", "Transport", "ctrl+shift+space"),
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
        s("insert_midi_clip", "Insert MIDI Clip", "Session", "ctrl+shift+m"),
        s("create_follow_action_chain", "Create Follow Action Chain", "Session", "ctrl+shift+enter"),
        // --- Arrangement View ---
        s("consolidate_selection", "Consolidate Selection into Clip", "Arrangement", "ctrl+j"),
        s("create_fade", "Create Fade/Crossfade", "Arrangement", "ctrl+alt+f"),
        s("toggle_loop_brace", "Toggle Loop Brace", "Arrangement", "ctrl+l"),
        s("select_loop_brace_contents", "Select Loop Brace Contents", "Arrangement", "ctrl+shift+l"),
        s("insert_silence", "Insert Silence", "Arrangement", "ctrl+i"),
        s("fold_unfold_tracks", "Fold/Unfold Selected Tracks", "Arrangement", "u"),
        s("unfold_all_tracks", "Unfold All Tracks", "Arrangement", "alt+u"),
        s("split_clip", "Split Clip at Selection", "Arrangement", "ctrl+e"),
        s("crop_clip", "Crop Selected Clips", "Arrangement", "ctrl+shift+j"),
        s("delete_fades", "Delete Fades/Crossfades in Selected Clip(s)", "Arrangement", "ctrl+alt+backspace"),
        s("set_start_marker", "Set Start Marker", "Arrangement", "ctrl+f9"),
        s("set_loop_start", "Set Loop Brace Start", "Arrangement", "ctrl+f10"),
        s("set_loop_end", "Set Loop Brace End", "Arrangement", "ctrl+f11"),
        s("set_end_marker", "Set End Marker", "Arrangement", "ctrl+f12"),
        s("cut_time", "Cut Time", "Arrangement", "ctrl+shift+x"),
        s("paste_time", "Paste Time", "Arrangement", "ctrl+shift+v"),
        s("duplicate_time", "Duplicate Time", "Arrangement", "ctrl+shift+d"),
        s("delete_time", "Delete Time", "Arrangement", "ctrl+shift+delete"),
        s("track_height_increase", "Adjust Height of Selected Tracks/Clips (Increase)", "Arrangement", "alt+="),
        s("track_height_decrease", "Adjust Height of Selected Tracks/Clips (Decrease)", "Arrangement", "alt+-"),
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
        // --- Browser ---
        s("browser_history_back", "Browser History Back", "Browser", "ctrl+["),
        s("browser_history_forward", "Browser History Forward", "Browser", "ctrl+]"),
        // --- Quantize / Time ---
        s("quantize", "Quantize", "Quantize / Time", "ctrl+u"),
        s("quantize_settings", "Quantize Settings…", "Quantize / Time", "ctrl+shift+u"),
        // --- Grid ---
        s("grid_narrow", "Narrow Grid", "Grid", "ctrl+1"),
        s("grid_widen", "Widen Grid", "Grid", "ctrl+2"),
        s("grid_triplet", "Triplet Grid", "Grid", "ctrl+3"),
        s("grid_snap", "Snap to Grid", "Grid", "ctrl+4"),
        s("grid_fixed_adaptive", "Fixed/Zoom-Adaptive Grid", "Grid", "ctrl+5"),
        // --- MIDI Editing ---
        // ctrl+i / ctrl+shift+i / ctrl+a / ctrl+g / ctrl+shift+g intentionally share their native
        // combo with existing entries (Live reuses them per context). Surfaced by the conflict UI.
        s("select_all_notes", "Select All Notes", "MIDI Editing", "ctrl+a"),
        s("insert_warp_marker", "Insert Warp Marker", "MIDI Editing", "ctrl+i"),
        s("insert_transient", "Insert Transient", "MIDI Editing", "ctrl+shift+i"),
        s("group_notes", "Group Notes (Play All)", "MIDI Editing", "ctrl+g"),
        s("ungroup_notes", "Ungroup Notes", "MIDI Editing", "ctrl+shift+g"),
        s("invert_note_selection", "Invert Note Selection", "MIDI Editing", "ctrl+shift+a"),
        s("fit_notes_to_time", "Fit Notes to Time Range", "MIDI Editing", "ctrl+alt+j"),
        s("apply_midi_tool", "Apply Current MIDI Tool Settings", "MIDI Editing", "ctrl+enter"),
        s("toggle_full_clip_view", "Toggle Full-Size Clip View", "MIDI Editing", "ctrl+alt+e"),
        s("select_next_note", "Select Next Note", "MIDI Editing", "alt+up"),
        s("select_prev_note", "Select Previous Note", "MIDI Editing", "alt+down"),
        s("select_next_note_key", "Select Next Note in Same Key Track", "MIDI Editing", "alt+left"),
        s("select_prev_note_key", "Select Previous Note in Same Key Track", "MIDI Editing", "alt+right"),
        s("note_velocity_up", "Adjust Note Selection Velocity Deviation (Up)", "MIDI Editing", "ctrl+shift+up"),
        s("note_velocity_down", "Adjust Note Selection Velocity Deviation (Down)", "MIDI Editing", "ctrl+shift+down"),
        s("note_chance_up", "Adjust Note Selection Chance (Up)", "MIDI Editing", "ctrl+alt+up"),
        s("note_chance_down", "Adjust Note Selection Chance (Down)", "MIDI Editing", "ctrl+alt+down"),
        s("scroll_editor_left", "Scroll Editor Horizontally (Left)", "MIDI Editing", "ctrl+pageup"),
        s("scroll_editor_right", "Scroll Editor Horizontally (Right)", "MIDI Editing", "ctrl+pagedown"),
        // --- Loop / Selection ---
        s("loop_halve", "Halve Loop Length", "Loop / Selection", "ctrl+up"),
        s("loop_double", "Double Loop Length", "Loop / Selection", "ctrl+down"),
        s("loop_shorten", "Shorten Loop", "Loop / Selection", "ctrl+right"),
        s("loop_lengthen", "Lengthen Loop", "Loop / Selection", "ctrl+left"),
        s("move_clip_region_right", "Move Clip Region with Start Marker (Right)", "Loop / Selection", "shift+right"),
        s("move_clip_region_left", "Move Clip Region with Start Marker (Left)", "Loop / Selection", "shift+left"),
        s("pan_selection_left", "Pan Left of Selection", "Loop / Selection", "ctrl+alt+left"),
        s("pan_selection_right", "Pan Right of Selection", "Loop / Selection", "ctrl+alt+right"),
        // --- Take Lanes ---
        s("show_take_lanes", "Show Take Lanes", "Take Lanes", "ctrl+alt+u"),
        s("add_take_lane", "Add Take Lane", "Take Lanes", "shift+alt+t"),
        // --- Focus ---
        s("focus_control_bar", "Move Focus to the Control Bar", "Focus", "alt+0"),
        s("focus_session", "Move Focus to the Session View", "Focus", "alt+1"),
        s("focus_arrangement", "Move Focus to the Arrangement View", "Focus", "alt+2"),
        s("focus_clip_view", "Move Focus to the Clip View", "Focus", "alt+3"),
        s("focus_device_view", "Move Focus to the Device View", "Focus", "alt+4"),
        s("focus_browser", "Move Focus to the Browser", "Focus", "alt+5"),
        s("focus_groove_pool", "Move Focus to the Groove Pool", "Focus", "alt+6"),
        s("focus_learn_view", "Move Focus to the Learn View", "Focus", "alt+7"),
        s("focus_selected_clip_panel", "Move Focus to the Selected Clip Panel", "Focus", "alt+8"),
        s("focus_clip_panels", "Move Focus to the Clip Panels", "Focus", "alt+shift+p"),
        s("focus_mixer", "Move Focus to Mixer", "Focus", "alt+shift+m"),
    ]
}
