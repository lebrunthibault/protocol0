//! Ableton connection diagnostic: 3 states computed by the agent — mirror of agent/web/status.py.
//!
//!   - no_ableton      : Ableton process absent.
//!   - script_inactive : Ableton running but the script's server unreachable (not activated / frozen).
//!   - ready           : script reachable -> its URL is returned (for info; editing doesn't
//!                       depend on it, only action triggering uses it via the listener).
//!
//! The SPA consumes this for its StatusPill; the systray for its status line.

use std::time::Duration;

use serde_json::{json, Value};

use crate::{process_check, runtime_state};

/// Computes the current state as the JSON object the SPA / systray consume.
pub fn compute() -> Value {
    if !process_check::ableton_is_running() {
        return json!({ "state": "no_ableton" });
    }
    if let Some(rt) = runtime_state::read() {
        if ping(&rt.script_url) {
            return json!({ "state": "ready", "script_url": rt.script_url });
        }
    }
    json!({ "state": "script_inactive" })
}

fn ping(script_url: &str) -> bool {
    let url = format!("{script_url}/api/health");
    reqwest::blocking::Client::new()
        .get(&url)
        .timeout(Duration::from_secs(1))
        .send()
        .map(|r| r.status().as_u16() == 200)
        .unwrap_or(false)
}
