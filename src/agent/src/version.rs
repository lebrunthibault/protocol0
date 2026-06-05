//! Project version, read from the repo-root `VERSION` file (single source of truth, bumped
//! by /commit) — mirror of agent/version.py.
//!
//! Unlike the Python agent, which resolved VERSION at runtime, a Rust binary has no sources
//! alongside it. build.rs reads repo-root VERSION and injects it as the P0_VERSION compile-time
//! env var (with a rerun-if-changed trigger), so a /commit bump forces a rebuild and the value
//! is never stale. We read it here via env!.

/// The project version, injected by build.rs from repo-root VERSION at compile time.
pub fn version() -> &'static str {
    env!("P0_VERSION")
}
