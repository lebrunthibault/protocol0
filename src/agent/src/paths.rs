//! %APPDATA%\Protocol0 file locations, shared by config, store, runtime_state, logging.
//!
//! The Python agent built these from os.environ["APPDATA"] in each module. We centralise
//! them here. dirs::config_dir() returns %APPDATA% (Roaming) on Windows, which is exactly
//! what the Python code used — so the paths are byte-for-byte the same as the Python agent's,
//! and the two agents share the same shortcuts.json / runtime.json (important: the running
//! Ableton script writes runtime.json regardless of which agent reads it).

use std::path::PathBuf;

/// Root data dir: %APPDATA%\Protocol0. Falls back to the current dir only if APPDATA is
/// somehow unset (never the case in a real user session); the Python code would have raised.
pub fn data_dir() -> PathBuf {
    dirs::config_dir()
        .unwrap_or_else(|| PathBuf::from("."))
        .join("Protocol0")
}

/// %APPDATA%\Protocol0\shortcuts.json — the binding config (constitution §3.3, §5).
pub fn config_path() -> PathBuf {
    data_dir().join("shortcuts.json")
}

/// %APPDATA%\Protocol0\runtime.json — the script's published runtime state.
pub fn runtime_path() -> PathBuf {
    data_dir().join("runtime.json")
}

/// %APPDATA%\Protocol0\logs — rotating agent.log lives here.
pub fn log_dir() -> PathBuf {
    data_dir().join("logs")
}
