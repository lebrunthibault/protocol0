//! Read the runtime-state file published by the script — mirror of agent/runtime_state.py.
//!
//! The script (inside Ableton) writes %APPDATA%\Protocol0\runtime.json with the effective URL
//! of its HTTP server (dynamic port), and removes it on shutdown. The agent reads it to
//! discover the current port; an absent/corrupt file means "script not active" (tolerant
//! read, never an error at runtime).

use std::fs;

use serde::Deserialize;

use crate::paths::runtime_path;

#[derive(Debug, Clone, Deserialize)]
pub struct RuntimeState {
    pub script_url: String,
    // pid / version are present in the file but unused by the agent; we ignore extra fields.
}

/// Returns the runtime state (script_url) or None if the file is absent/corrupt/invalid
/// (missing or empty script_url counts as invalid, matching the Python guard).
pub fn read() -> Option<RuntimeState> {
    let text = fs::read_to_string(runtime_path()).ok()?;
    let state: RuntimeState = serde_json::from_str(&text).ok()?;
    if state.script_url.is_empty() {
        return None;
    }
    Some(state)
}
