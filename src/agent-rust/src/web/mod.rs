//! Agent web server (fixed port 9010, own thread) — mirror of agent/web/server.py.
//!
//! Serves, in dispatch order:
//!   1. the API routes (/api/* and /status) via web::api;
//!   2. otherwise, the SPA's static build (catch-all -> index.html) via web::static_files.
//!
//! Lifecycle (bind 9010 + background retry if taken): if 9010 is busy, we log and retry — NO
//! random fallback (the shortcut and bookmarks are wired to 9010). The keyboard keeps working
//! even if the server never binds.

pub mod api;
pub mod static_files;
pub mod status;

use std::net::SocketAddr;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use axum::body::Body;
use axum::extract::Request;
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use axum::Router;
use tokio::net::TcpListener;

use crate::settings::WEB_PORT;

const RETRY_INTERVAL: Duration = Duration::from_secs(30);

/// Handle to stop the web server thread.
pub struct WebServer {
    shutdown_tx: Option<tokio::sync::oneshot::Sender<()>>,
    join: Option<thread::JoinHandle<()>>,
}

/// Builds the axum router: API routes first, then a catch-all serving the SPA.
fn router() -> Router {
    // GET mutations are also accepted (query → handled inside) to match the Python contract,
    // but the SPA uses POST, so we wire POST handlers and let GET deep-links fall to the SPA.
    Router::new()
        .route("/status", get(api::get_status))
        .route("/api/health", get(api::get_health))
        .route("/api/actions", get(api::get_actions))
        .route("/api/ableton-shortcuts", get(api::get_ableton_shortcuts))
        .route("/api/shortcuts", get(api::get_shortcuts))
        .route("/api/shortcuts/add", post(api::post_shortcuts_add))
        .route("/api/shortcuts/delete", post(api::post_shortcuts_delete))
        // Everything else: serve the SPA (catch-all -> index.html). Unknown /api/* paths are
        // handled inside serve_spa (404 JSON) rather than via a separate catch-all route, which
        // axum 0.7 rejects when more specific /api/* routes exist alongside it.
        .fallback(serve_spa)
}

/// Catch-all SPA handler: serve a real file under dist/, else index.html. A 500 with an
/// explicit message if the SPA wasn't built (never an empty 404), like the Python server.
async fn serve_spa(req: Request<Body>) -> Response {
    let path = req.uri().path().to_string();
    // Unknown /api/* path -> 404 JSON (never fall back to the SPA for an API route), matching
    // the Python server's contract.
    if path.starts_with("/api/") {
        return api::api_not_found().await.into_response();
    }
    match static_files::resolve(&path) {
        Some((body, ctype)) => ([(axum::http::header::CONTENT_TYPE, ctype)], body).into_response(),
        None => (
            StatusCode::INTERNAL_SERVER_ERROR,
            "frontend not built - run: cd src/frontend && npm ci && npm run build",
        )
            .into_response(),
    }
}

impl WebServer {
    /// Starts the server. If 9010 is taken, retries in the background until it binds or stop().
    pub fn start() -> Self {
        let (shutdown_tx, shutdown_rx) = tokio::sync::oneshot::channel::<()>();
        // Hand the runtime back to the spawning thread only after it's built, so start()
        // returns promptly.
        let (ready_tx, ready_rx) = mpsc::channel::<()>();

        let join = thread::spawn(move || {
            let rt = match tokio::runtime::Builder::new_multi_thread().enable_all().build() {
                Ok(rt) => rt,
                Err(e) => {
                    tracing::error!("web runtime build failed: {e}");
                    let _ = ready_tx.send(());
                    return;
                }
            };
            let _ = ready_tx.send(());
            rt.block_on(serve_with_retry(shutdown_rx));
        });
        // Don't block on readiness beyond a moment; the server binds asynchronously anyway.
        let _ = ready_rx.recv_timeout(Duration::from_secs(2));

        Self {
            shutdown_tx: Some(shutdown_tx),
            join: Some(join),
        }
    }

    pub fn stop(&mut self) {
        if let Some(tx) = self.shutdown_tx.take() {
            let _ = tx.send(());
        }
        if let Some(join) = self.join.take() {
            let _ = join.join();
        }
    }
}

/// Binds 9010, retrying every 30s while busy, then serves until the shutdown signal.
async fn serve_with_retry(mut shutdown_rx: tokio::sync::oneshot::Receiver<()>) {
    let addr = SocketAddr::from(([127, 0, 0, 1], WEB_PORT));
    let listener = loop {
        match TcpListener::bind(addr).await {
            Ok(l) => {
                tracing::info!("web server listening on http://127.0.0.1:{WEB_PORT}");
                break l;
            }
            Err(e) => {
                tracing::warn!("web server could not bind 127.0.0.1:{WEB_PORT} ({e})");
                tokio::select! {
                    _ = tokio::time::sleep(RETRY_INTERVAL) => continue,
                    _ = &mut shutdown_rx => return, // stopped before we ever bound
                }
            }
        }
    };

    let server = axum::serve(listener, router());
    let graceful = server.with_graceful_shutdown(async move {
        let _ = shutdown_rx.await;
    });
    if let Err(e) = graceful.await {
        tracing::warn!("web server error: {e}");
    }
}
