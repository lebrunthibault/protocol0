//! Read/write shortcuts.json on the agent side (CRUD for the web API) — mirror of
//! agent/shortcut_store.py.
//!
//! The agent OWNS writing the config. The listener (config.rs) re-reads the file by mtime,
//! so a write here is picked up on the next keypress with no reload plumbing.
//!
//! Same contract as the Python store:
//!     %APPDATA%\Protocol0\shortcuts.json
//!     { "version": 1, "bindings": [ {combo, action, params} ] }
//!
//! Tolerant on read (empty on absent/corrupt), atomic on write (write tmp + rename) so the
//! listener never reads a half-written file. Key = combo (one combo triggers one action).

use std::collections::HashMap;
use std::fs;

use serde::Serialize;

use crate::config::{load, Binding};
use crate::paths::config_path;

const VERSION: u32 = 1;

#[derive(Serialize)]
struct OnDisk<'a> {
    version: u32,
    bindings: Vec<BindingDto<'a>>,
}

/// The wire/JSON shape of a binding, used for both the file and the API responses.
#[derive(Serialize)]
pub struct BindingDto<'a> {
    pub combo: &'a str,
    pub action: &'a str,
    pub params: &'a HashMap<String, String>,
}

fn to_dto(b: &Binding) -> BindingDto<'_> {
    BindingDto {
        combo: &b.combo,
        action: &b.action,
        params: &b.params,
    }
}

/// Serializes the current bindings to JSON (the API returns this as the response body).
pub fn list_bindings() -> serde_json::Value {
    let bindings = load(&config_path());
    bindings_to_json(&bindings)
}

/// Adds the binding, or replaces the one with the same combo. Returns the resulting list.
pub fn upsert(combo: String, action: String, params: HashMap<String, String>) -> serde_json::Value {
    let mut bindings: Vec<Binding> = load(&config_path())
        .into_iter()
        .filter(|b| b.combo != combo)
        .collect();
    bindings.push(Binding {
        combo,
        action,
        params,
    });
    save(&bindings);
    bindings_to_json(&bindings)
}

/// Deletes the binding for a combo (no-op if absent). Returns the resulting list.
pub fn delete(combo: &str) -> serde_json::Value {
    let bindings: Vec<Binding> = load(&config_path())
        .into_iter()
        .filter(|b| b.combo != combo)
        .collect();
    save(&bindings);
    bindings_to_json(&bindings)
}

fn bindings_to_json(bindings: &[Binding]) -> serde_json::Value {
    let dtos: Vec<BindingDto> = bindings.iter().map(to_dto).collect();
    serde_json::to_value(dtos).unwrap_or(serde_json::Value::Array(vec![]))
}

fn save(bindings: &[Binding]) {
    let path = config_path();
    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let payload = OnDisk {
        version: VERSION,
        bindings: bindings.iter().map(to_dto).collect(),
    };
    let Ok(json) = serde_json::to_string_pretty(&payload) else {
        return;
    };
    // Atomic write: tmp + rename, so the listener never reads a partial file.
    let tmp = path.with_extension("json.tmp");
    if fs::write(&tmp, json).is_ok() {
        let _ = fs::rename(&tmp, &path);
    }
}
