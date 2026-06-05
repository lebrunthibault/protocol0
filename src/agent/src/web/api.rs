//! Handlers for the agent's web API (under /api) + /status — mirror of agent/web/api.py.
//!
//! Same routes and same JSON payloads as the Python agent (the SPA must not notice the swap):
//!   GET  /status                  -> status::compute()
//!   GET  /api/health              -> { ok, version }
//!   GET  /api/actions             -> action catalog (proxied from the script's /openapi.json)
//!   GET  /api/ableton-shortcuts   -> { doc_url, shortcuts }
//!   GET  /api/shortcuts           -> current bindings
//!   POST /api/shortcuts/add       -> upsert {combo, action, params}
//!   POST /api/shortcuts/delete    -> delete {combo}
//!
//! The blocking reqwest calls (actions, status) run on a blocking thread (see mod.rs) so they
//! never stall the async runtime.

use std::collections::HashMap;

use axum::http::StatusCode;
use axum::response::IntoResponse;
use axum::Json;
use serde::Deserialize;
use serde_json::json;

use crate::settings::WEB_PORT;
use crate::{ableton_shortcuts, action_catalog, runtime_state, shortcut_store, version};
use crate::web::status;

// WEB_PORT is referenced for the bookmarkable URL contract; suppress unused warning when not
// directly read here (it documents the single-port invariant alongside the API).
const _: u16 = WEB_PORT;

pub async fn get_status() -> impl IntoResponse {
    // status::compute() does blocking HTTP (ping) + process enumeration.
    let value = tokio::task::spawn_blocking(status::compute)
        .await
        .unwrap_or_else(|_| json!({ "state": "no_ableton" }));
    Json(value)
}

pub async fn get_health() -> impl IntoResponse {
    Json(json!({ "ok": true, "version": version::version() }))
}

pub async fn get_actions() -> impl IntoResponse {
    // Catalog derived live from the script's /openapi.json. Script unreachable -> [].
    let value = tokio::task::spawn_blocking(|| {
        let rt = runtime_state::read();
        match rt {
            Some(rt) => {
                let client = reqwest::blocking::Client::new();
                let catalog = action_catalog::fetch(&rt.script_url, &client);
                serde_json::to_value(catalog).unwrap_or_else(|_| json!([]))
            }
            None => json!([]),
        }
    })
    .await
    .unwrap_or_else(|_| json!([]));
    Json(value)
}

pub async fn get_ableton_shortcuts() -> impl IntoResponse {
    Json(json!({
        "doc_url": ableton_shortcuts::DOC_URL,
        "shortcuts": ableton_shortcuts::get_all(),
    }))
}

pub async fn get_shortcuts() -> impl IntoResponse {
    Json(shortcut_store::list_bindings())
}

/// Body for /api/shortcuts/add (POST JSON). The SPA posts JSON; params defaults to empty.
#[derive(Deserialize)]
pub struct AddBody {
    combo: Option<String>,
    action: Option<String>,
    #[serde(default)]
    params: HashMap<String, String>,
}

pub async fn post_shortcuts_add(Json(body): Json<AddBody>) -> impl IntoResponse {
    match (body.combo, body.action) {
        (Some(combo), Some(action)) if !combo.is_empty() && !action.is_empty() => {
            Json(shortcut_store::upsert(combo, action, body.params)).into_response()
        }
        _ => error("combo and action are required", StatusCode::BAD_REQUEST),
    }
}

#[derive(Deserialize)]
pub struct DeleteBody {
    combo: Option<String>,
}

pub async fn post_shortcuts_delete(Json(body): Json<DeleteBody>) -> impl IntoResponse {
    match body.combo {
        Some(combo) if !combo.is_empty() => {
            Json(shortcut_store::delete(&combo)).into_response()
        }
        _ => error("combo is required", StatusCode::BAD_REQUEST),
    }
}

/// Unknown /api/* path -> 404 JSON (never fall back to the SPA for an API route).
pub async fn api_not_found() -> impl IntoResponse {
    error("not found", StatusCode::NOT_FOUND)
}

fn error(message: &str, code: StatusCode) -> axum::response::Response {
    (code, Json(json!({ "error": message }))).into_response()
}
