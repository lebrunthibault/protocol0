//! Read the global binding config — mirror of agent/config.py.
//!
//! Single file at %APPDATA%\Protocol0\shortcuts.json (constitution §3.3, §5), written by the
//! agent (shortcut_store), read here by the listener. Versioned envelope:
//!     { "version": 1, "bindings": [
//!         { "combo": "ctrl+alt+e", "action": "load_device", "params": {"name": "EQ Eight"} }
//!     ] }
//!
//! Tolerant: an absent/empty/corrupt file yields zero bindings (never an error at runtime).

use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::time::SystemTime;

use serde::Deserialize;

use crate::paths::config_path;

/// One binding: a combo and the action (+ params) it triggers.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Binding {
    pub combo: String,
    pub action: String,
    pub params: HashMap<String, String>,
}

/// Raw on-disk shapes (tolerant deserialization).
#[derive(Deserialize)]
struct RawFile {
    #[serde(default)]
    bindings: Vec<RawBinding>,
}

#[derive(Deserialize)]
struct RawBinding {
    combo: Option<String>,
    action: Option<String>,
    #[serde(default)]
    params: HashMap<String, String>,
}

/// Loads bindings and reloads them when the file changes (by mtime) — exactly like the
/// Python ShortcutConfig the listener polls on every keypress.
pub struct ShortcutConfig {
    path: PathBuf,
    mtime: Option<SystemTime>,
    by_combo: HashMap<String, Binding>,
}

impl ShortcutConfig {
    pub fn new() -> Self {
        let mut c = Self {
            path: config_path(),
            mtime: None,
            by_combo: HashMap::new(),
        };
        c.reload();
        c
    }

    fn current_mtime(&self) -> Option<SystemTime> {
        fs::metadata(&self.path).and_then(|m| m.modified()).ok()
    }

    /// Reloads the file if its mtime changed. Returns true if reloaded.
    pub fn reload_if_changed(&mut self) -> bool {
        if self.current_mtime() != self.mtime {
            self.reload();
            true
        } else {
            false
        }
    }

    pub fn reload(&mut self) {
        self.mtime = self.current_mtime();
        self.by_combo = load(&self.path)
            .into_iter()
            .map(|b| (b.combo.clone(), b))
            .collect();
    }

    pub fn get(&self, combo: &str) -> Option<&Binding> {
        self.by_combo.get(combo)
    }

    /// Builds a config from in-memory bindings, bypassing the file (used by listener tests, the
    /// equivalent of the Python _StubConfig). reload_if_changed() is a no-op here (mtime None).
    #[cfg(test)]
    pub fn from_bindings(bindings: Vec<Binding>) -> Self {
        Self {
            path: PathBuf::new(),
            mtime: None,
            by_combo: bindings.into_iter().map(|b| (b.combo.clone(), b)).collect(),
        }
    }
}

/// Parses the bindings list. Returns an empty vec on any read/parse error (tolerant) — and
/// skips entries missing a combo or action, like the Python loader.
pub fn load(path: &PathBuf) -> Vec<Binding> {
    let Ok(text) = fs::read_to_string(path) else {
        return Vec::new();
    };
    let Ok(file) = serde_json::from_str::<RawFile>(&text) else {
        return Vec::new();
    };
    file.bindings
        .into_iter()
        .filter_map(|raw| {
            let combo = raw.combo.filter(|s| !s.is_empty())?;
            let action = raw.action.filter(|s| !s.is_empty())?;
            Some(Binding {
                combo,
                action,
                params: raw.params,
            })
        })
        .collect()
}
