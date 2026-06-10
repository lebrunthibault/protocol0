//! HTTP client to the remote script's API — mirror of agent/script_client.py.
//!
//! The agent just replaces AHK as an event producer: the action API exposed by the script is
//! unchanged.
//!
//! The base URL is resolved ON EACH CALL, not once: the agent lives from logon to logoff,
//! while Ableton (and its server, on a dynamic port) starts/stops several times in between.
//! So we read the current URL from P0_SCRIPT_PORT (override) or runtime.json on each binding
//! execution; absence = script not active = no-op.

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

        // First match by name (script before extensions). Single-extension iteration assumes
        // action names are unique across script + extensions; `owner` is carried so a future
        // (owner, name) binding key is a localized change.
        let Some(action) = catalog.iter().find(|a| a.name == binding.action) else {
            tracing::info!("no owner for action {} (script/extensions down?)", binding.action);
            return;
        };

        // Body = the params the action declares, taken from the binding (missing -> omitted;
        // the owner returns 400 if a required one is absent, which post() logs).
        let body: serde_json::Map<String, serde_json::Value> = action
            .params
            .iter()
            .filter_map(|p| {
                binding
                    .params
                    .get(&p.name)
                    .map(|v| (p.name.clone(), serde_json::Value::String(v.clone())))
            })
            .collect();

        // Owner-aware POST: the script serves actions under /api/action/... ; an extension serves
        // them under /action/... (no /api). The openapi `path` is identical for both.
        let path = if action.api_prefix {
            format!("/api{}", action.path)
        } else {
            action.path.clone()
        };
        self.post(&action.owner_url, &path, serde_json::Value::Object(body));
    }

    fn post(&self, base_url: &str, path: &str, body: serde_json::Value) {
        let url = format!("{base_url}{path}");
        let result = self
            .client
            .post(&url)
            .json(&body)
            .timeout(std::time::Duration::from_secs(5))
            .send()
            .and_then(|r| r.error_for_status());
        if let Err(e) = result {
            tracing::warn!("script HTTP {path} failed: {e}");
        }
    }
}
