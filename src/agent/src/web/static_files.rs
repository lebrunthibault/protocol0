//! Resolve + serve the SPA's static build (src/frontend/dist) — mirror of
//! agent/web/static_files.py.
//!
//! Where the Python agent read the Vite build from _MEIPASS (frozen) or disk (dev), the Rust
//! binary bakes src/frontend/dist straight in via rust-embed at compile time. The dist/ is
//! tiny (~149 KB), so embedding it adds nothing meaningful to the binary.
//!
//! Catch-all SPA: any path that doesn't match a real file serves index.html, so client-side
//! routing (history mode) works on refresh / deep-link.

use rust_embed::RustEmbed;

/// The Vue SPA build, embedded at compile time. The path is relative to this crate's root
/// (src/agent/), so ../frontend/dist reaches src/frontend/dist. The build script
/// (build_agent_exe.ps1) guarantees `npm run build` ran first.
#[derive(RustEmbed)]
#[folder = "../frontend/dist"]
struct Spa;

/// (body, content-type) for a GET request:
///   - real file under dist/        -> that file;
///   - otherwise                    -> index.html (catch-all SPA);
///   - None if the SPA isn't built (no index.html embedded).
pub fn resolve(url_path: &str) -> Option<(Vec<u8>, String)> {
    let rel = url_path.trim_start_matches('/');

    if !rel.is_empty() {
        if let Some(file) = Spa::get(rel) {
            return Some((file.data.into_owned(), content_type(rel)));
        }
    }

    // Catch-all: index.html.
    let index = Spa::get("index.html")?;
    Some((
        index.data.into_owned(),
        "text/html; charset=utf-8".to_string(),
    ))
}

fn content_type(path: &str) -> String {
    let guess = mime_guess::from_path(path).first_or_octet_stream();
    let essence = guess.essence_str();
    if essence.starts_with("text/")
        || essence == "application/javascript"
        || essence == "application/json"
    {
        format!("{essence}; charset=utf-8")
    } else {
        essence.to_string()
    }
}
