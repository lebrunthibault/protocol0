//! HTTP client to the remote script's API — mirror of agent/script_client.py.
//!
//! The agent just replaces AHK as an event producer: the action API exposed by the script is
//! unchanged.
//!
//! The base URL is resolved ON EACH CALL, not once: the agent lives from logon to logoff,
//! while Ableton (and its server, on a dynamic port) starts/stops several times in between.
//! So we read the current URL from P0_SCRIPT_PORT (override) or runtime.json on each binding
//! execution; absence = script not active = no-op.

use std::collections::HashMap;

use crate::config::Binding;
use crate::settings::Settings;
use crate::{action_catalog, extension_registry, runtime_state};

pub struct ScriptClient {
    settings: Settings,
    client: reqwest::blocking::Client,
}

impl ScriptClient {
    pub fn new(settings: Settings) -> Self {
        Self {
            settings,
            client: reqwest::blocking::Client::new(),
        }
    }

    fn resolve_base_url(&self) -> Option<String> {
        // 1) manual override (P0_SCRIPT_PORT); 2) discovery via runtime.json; 3) None.
        if let Some(url) = self.settings.override_url() {
            return Some(url);
        }
        runtime_state::read().map(|rt| rt.script_url)
    }

    /// Generic dispatch: resolve the action in the MERGED catalog (the script's /openapi.json plus
    /// every registered third-party extension's) at trigger time, then POST to its OWNER's route.
    /// No action is hardcoded — dropping an `@action` plugin or registering an extension is enough
    /// to make it executable. (`send_keys` never reaches here: it's injected locally upstream, see
    /// main.rs.)
    pub fn execute(&self, binding: &Binding) {
        // The keypress path stays infallible: a failure is logged by `run`, never surfaced.
        let _ = self.run(&binding.action, &binding.params);
    }

    /// Resolve `action` in the merged catalog and POST it to its owner.
    ///
    /// Same dispatch as a keypress, callable without a `Binding` — this is what the SPA's
    /// "run now" button goes through (`POST /api/actions/run`), which is why it reports
    /// failure instead of only logging it.
    pub fn run(&self, action: &str, params: &HashMap<String, String>) -> Result<(), String> {
        // Build the same merged catalog /api/actions exposes, so routing matches exactly what the
        // user bound in the SPA. Each source has a short (2s) per-fetch timeout; the extension
        // registry is small. We read the registry here but do NOT record_pull — a single keypress
        // shouldn't evict a briefly-busy extension; liveness is driven by the SPA's get_actions.
        let mut catalog: Vec<action_catalog::ActionDef> = Vec::new();

        if let Some(base_url) = self.resolve_base_url() {
            let script = action_catalog::fetch(&base_url, &self.client);
            catalog.extend(action_catalog::tag_owner(script, &base_url, "script", true));
        }
        for ext in extension_registry::list() {
            let actions = action_catalog::fetch(&ext.script_url, &self.client);
            catalog.extend(action_catalog::tag_owner(actions, &ext.script_url, &ext.name, false));
        }

        let Some(target) = resolve(&catalog, action, params) else {
            tracing::info!("no owner for action {action} (script/extensions down?)");
            return Err(format!("unknown action '{action}' (is Ableton running?)"));
        };

        self.post(&target.owner_url, &target.path, target.body)
    }

    fn post(&self, base_url: &str, path: &str, body: serde_json::Value) -> Result<(), String> {
        let url = format!("{base_url}{path}");
        let result = self
            .client
            .post(&url)
            .json(&body)
            .timeout(std::time::Duration::from_secs(5))
            .send()
            .and_then(|r| r.error_for_status());
        match result {
            Ok(_) => Ok(()),
            Err(e) => {
                tracing::warn!("script HTTP {path} failed: {e}");
                Err(format!("{path} failed: {e}"))
            }
        }
    }
}

/// Where an action resolves to: the owner base URL, the path to POST, and the JSON body.
#[derive(Debug, PartialEq)]
struct Target {
    owner_url: String,
    path: String,
    body: serde_json::Value,
}

/// Pure resolution step (no I/O) so it's unit-testable without a live script.
///
/// First match by name (script before extensions). Single-extension iteration assumes action
/// names are unique across script + extensions; `owner` is carried so a future (owner, name)
/// binding key is a localized change.
fn resolve(
    catalog: &[action_catalog::ActionDef],
    action: &str,
    params: &HashMap<String, String>,
) -> Option<Target> {
    let found = catalog.iter().find(|a| a.name == action)?;

    // Body = the params the action DECLARES, taken from the caller (missing -> omitted; the
    // owner returns 400 if a required one is absent, which post() logs). Undeclared params
    // supplied by the caller are dropped rather than forwarded.
    let body: serde_json::Map<String, serde_json::Value> = found
        .params
        .iter()
        .filter_map(|p| {
            params
                .get(&p.name)
                .map(|v| (p.name.clone(), serde_json::Value::String(v.clone())))
        })
        .collect();

    // Owner-aware POST: the script serves actions under /api/action/... ; an extension serves
    // them under /action/... (no /api). The openapi `path` is identical for both.
    let path = if found.api_prefix {
        format!("/api{}", found.path)
    } else {
        found.path.clone()
    };

    Some(Target {
        owner_url: found.owner_url.clone(),
        path,
        body: serde_json::Value::Object(body),
    })
}

#[cfg(test)]
mod tests {
    //! The dispatch decision (which owner, which path, which body) is pure — the HTTP call
    //! itself is not covered here.
    use super::*;
    use serde_json::json;

    fn action(name: &str, params: &[&str], api_prefix: bool) -> action_catalog::ActionDef {
        action_catalog::ActionDef {
            name: name.to_string(),
            label: name.to_string(),
            description: String::new(),
            params: params
                .iter()
                .map(|p| action_catalog::ActionParam {
                    name: p.to_string(),
                    ty: "string".to_string(),
                    required: true,
                })
                .collect(),
            path: format!("/action/plugin/{name}"),
            method: "POST".to_string(),
            owner_url: "http://127.0.0.1:9004".to_string(),
            owner_name: "script".to_string(),
            api_prefix,
        }
    }

    fn params(pairs: &[(&str, &str)]) -> HashMap<String, String> {
        pairs.iter().map(|(k, v)| (k.to_string(), v.to_string())).collect()
    }

    #[test]
    fn unknown_action_resolves_to_nothing() {
        assert!(resolve(&[action("load_device", &["name"], true)], "nope", &params(&[])).is_none());
    }

    #[test]
    fn script_action_is_posted_under_the_api_prefix() {
        let catalog = [action("remove_muted_notes", &[], true)];
        let target = resolve(&catalog, "remove_muted_notes", &params(&[])).unwrap();

        assert_eq!(target.path, "/api/action/plugin/remove_muted_notes");
        assert_eq!(target.owner_url, "http://127.0.0.1:9004");
        assert_eq!(target.body, json!({})); // parameterless -> empty body
    }

    #[test]
    fn extension_action_is_posted_without_the_api_prefix() {
        let catalog = [action("do_thing", &[], false)];
        let target = resolve(&catalog, "do_thing", &params(&[])).unwrap();

        assert_eq!(target.path, "/action/plugin/do_thing");
    }

    #[test]
    fn body_carries_the_declared_params_only() {
        let catalog = [action("load_device", &["name"], true)];
        let target =
            resolve(&catalog, "load_device", &params(&[("name", "Reverb"), ("bogus", "x")]))
                .unwrap();

        // `bogus` isn't declared by the action -> dropped, not forwarded.
        assert_eq!(target.body, json!({ "name": "Reverb" }));
    }

    #[test]
    fn missing_param_is_omitted_rather_than_sent_empty() {
        let catalog = [action("load_device", &["name"], true)];
        let target = resolve(&catalog, "load_device", &params(&[])).unwrap();

        assert_eq!(target.body, json!({}));
    }

    #[test]
    fn the_script_wins_over_an_extension_exposing_the_same_name() {
        let mut ext = action("load_device", &[], false);
        ext.owner_name = "my-ext".to_string();
        ext.owner_url = "http://127.0.0.1:9005".to_string();
        let catalog = [action("load_device", &[], true), ext];

        let target = resolve(&catalog, "load_device", &params(&[])).unwrap();

        assert_eq!(target.owner_url, "http://127.0.0.1:9004");
    }
}
