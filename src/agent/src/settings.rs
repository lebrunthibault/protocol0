//! Runtime settings of the agent — mirror of agent/settings.py.
//!
//! The script port is not hardwired: the script picks it dynamically and publishes its
//! effective URL in runtime.json (see runtime_state). We discover the URL at runtime.
//! P0_SCRIPT_PORT remains a manual escape hatch: if set, it forces the URL and bypasses
//! runtime.json (advanced / dev cases).

use std::env;

/// Fixed port of the web server served by the agent (home + keymapper + /api + /status).
/// Hardwired: the agent's --open path (main.rs) and the systray (tray.rs) open
/// http://127.0.0.1:9010/shortcuts. Single source of truth for the port, no dynamic fallback.
/// The URL must stay bookmarkable.
pub const WEB_PORT: u16 = 9010;

/// Settings resolved once at startup.
pub struct Settings {
    override_port: Option<u16>,
}

impl Settings {
    pub fn load() -> Self {
        let override_port = env::var("P0_SCRIPT_PORT")
            .ok()
            .and_then(|s| s.trim().parse::<u16>().ok());
        Self { override_port }
    }

    /// URL forced via P0_SCRIPT_PORT, or None for dynamic discovery (via runtime.json).
    pub fn override_url(&self) -> Option<String> {
        self.override_port.map(|p| format!("http://127.0.0.1:{p}"))
    }
}
