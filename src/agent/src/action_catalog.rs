//! Action catalog derived from the script's REST API (its /openapi.json) — mirror of
//! agent/action_catalog.py.
//!
//! No static list: dropping an `@action` plugin into the script makes it appear here
//! automatically. The agent proxies the catalog (the frontend, served on :9010, can't fetch
//! the script on another port — CORS), transforms it into the shape the SPA expects, and
//! serves it on /api/actions:
//!
//!     { name, label, description, params: [{name, type, required}], path, method }
//!
//! - name        : the @action method name (e.g. "load_device").
//! - label       : name in Title Case (e.g. "Load Device").
//! - description : the OpenAPI summary (first line of the method docstring).
//! - params      : from the JSON requestBody (JSON Schema type: string/integer/number/boolean).
//! - path        : "/action/<plugin>/<method>" (without the /api prefix, carried by servers[].url).
//!
//! Script unreachable / network error -> empty list (the keymapper UI is locked anyway when
//! the script isn't "ready").

use std::time::Duration;

use serde::Serialize;
use serde_json::Value;

/// Short timeout: /openapi.json is local and fast; never block the UI.
const TIMEOUT: Duration = Duration::from_secs(2);

#[derive(Serialize)]
pub struct ActionParam {
    pub name: String,
    #[serde(rename = "type")]
    pub ty: String,
    pub required: bool,
}

#[derive(Serialize)]
pub struct ActionDef {
    pub name: String,
    pub label: String,
    pub description: String,
    pub params: Vec<ActionParam>,
    pub path: String,
    pub method: String,
}

/// "load_device" -> "Load Device".
fn title_case(name: &str) -> String {
    name.split('_')
        .map(|word| {
            let mut chars = word.chars();
            match chars.next() {
                Some(first) => first.to_uppercase().chain(chars).collect::<String>(),
                None => String::new(),
            }
        })
        .collect::<Vec<_>>()
        .join(" ")
}

/// Extracts [{name, type, required}] from an operation's JSON requestBody.
fn params_from_request_body(operation: &Value) -> Vec<ActionParam> {
    let schema = operation
        .get("requestBody")
        .and_then(|v| v.get("content"))
        .and_then(|v| v.get("application/json"))
        .and_then(|v| v.get("schema"));
    let Some(schema) = schema else {
        return Vec::new();
    };
    let required: Vec<&str> = schema
        .get("required")
        .and_then(|v| v.as_array())
        .map(|a| a.iter().filter_map(|x| x.as_str()).collect())
        .unwrap_or_default();
    let Some(properties) = schema.get("properties").and_then(|v| v.as_object()) else {
        return Vec::new();
    };
    properties
        .iter()
        .map(|(name, prop)| ActionParam {
            name: name.clone(),
            ty: prop
                .get("type")
                .and_then(|v| v.as_str())
                .unwrap_or("string")
                .to_string(),
            required: required.contains(&name.as_str()),
        })
        .collect()
}

fn to_action_def(path: &str, method: &str, operation: &Value) -> ActionDef {
    let name = path.rsplit('/').next().unwrap_or(path).to_string(); // /action/<plugin>/<method> -> <method>
    ActionDef {
        label: title_case(&name),
        description: operation
            .get("summary")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string(),
        params: params_from_request_body(operation),
        path: path.to_string(),
        method: method.to_uppercase(),
        name,
    }
}

/// Parses an /openapi.json document into the action catalog. Pure (no I/O) so it's unit-
/// testable against a fixture, like the Python version's fetch() body.
///
/// Only reads /action/* routes (the plugin actions); technical routes (/set/get_state…) are
/// not assignable actions for the keymapper.
pub fn parse_catalog(spec: &Value) -> Vec<ActionDef> {
    let Some(paths) = spec.get("paths").and_then(|v| v.as_object()) else {
        return Vec::new();
    };
    let mut catalog = Vec::new();
    for (path, item) in paths {
        if !path.starts_with("/action/") {
            continue;
        }
        if let Some(methods) = item.as_object() {
            for (method, operation) in methods {
                catalog.push(to_action_def(path, method, operation));
            }
        }
    }
    catalog
}

/// Fetches and parses the script's action catalog, or [] if unreachable.
pub fn fetch(script_url: &str, client: &reqwest::blocking::Client) -> Vec<ActionDef> {
    let url = format!("{script_url}/openapi.json");
    let result = client
        .get(&url)
        .timeout(TIMEOUT)
        .send()
        .and_then(|r| r.error_for_status())
        .and_then(|r| r.json::<Value>());
    match result {
        Ok(spec) => parse_catalog(&spec),
        Err(e) => {
            tracing::info!("action catalog unavailable: {e}");
            Vec::new()
        }
    }
}

#[cfg(test)]
mod tests {
    //! The catalog derives from the script's /openapi.json: transform + robustness. Mirror of
    //! test_action_catalog.py. We test parse_catalog (the pure transform) against a fixture;
    //! the network-error path is the `fetch` early-return, trivially [] on any reqwest error.
    use super::*;
    use serde_json::json;

    fn openapi() -> Value {
        json!({
            "paths": {
                "/action/device/load_device": {
                    "post": {
                        "summary": "Load a device onto the selected track by name.",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": { "name": { "type": "string" } },
                                        "required": ["name"]
                                    }
                                }
                            }
                        }
                    }
                },
                // A core route (non /action/*): ignored by the keymapper catalog.
                "/set/get_state": { "get": { "summary": "Get the set state" } }
            }
        })
    }

    #[test]
    fn transforms_action_routes() {
        let catalog = parse_catalog(&openapi());
        assert_eq!(catalog.len(), 1); // /set/get_state ignored
        let a = &catalog[0];
        assert_eq!(a.name, "load_device");
        assert_eq!(a.label, "Load Device"); // method -> Title Case
        assert_eq!(a.description, "Load a device onto the selected track by name.");
        assert_eq!(a.path, "/action/device/load_device");
        assert_eq!(a.method, "POST");
        assert_eq!(a.params.len(), 1);
        assert_eq!(a.params[0].name, "name");
        assert_eq!(a.params[0].ty, "string");
        assert!(a.params[0].required);
    }

    #[test]
    fn empty_on_missing_paths() {
        assert!(parse_catalog(&json!({})).is_empty());
    }

    #[test]
    fn title_case_works() {
        assert_eq!(title_case("load_device"), "Load Device");
        assert_eq!(title_case("hello"), "Hello");
    }
}
