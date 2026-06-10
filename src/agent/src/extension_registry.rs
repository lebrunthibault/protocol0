//! In-memory registry of third-party Ableton extensions that announced themselves to the agent.
//!
//! A remote-script plugin runs in the script's own process and is discovered via runtime.json.
//! A third-party extension runs in its own sandboxed Extension Host and can only reach us by an
//! outbound `fetch` (the sandbox forbids the shared-file trick). So it POSTs
//! `/api/extensions/register {name, script_url}` on activate and `/unregister {name}` on shutdown.
//!
//! Registration is SOFT STATE: an extension that dies with Live may never unregister cleanly, so
//! we expire it by liveness — each catalog pull records success/failure, and an entry is pruned
//! after MAX_MISSES consecutive failures (mirrors how the agent tolerates the script being down →
//! empty catalog). Re-registration is idempotent: same `name` replaces the URL and resets liveness.
//!
//! The registry is a process-global singleton: the web handlers (tokio thread) mutate it on
//! register/unregister, and the keypress path (listener thread, via ScriptClient) reads it to route
//! actions. The pure mutation logic lives in free functions over a `&mut HashMap` so it can be unit-
//! tested in isolation; the global is a thin Mutex wrapper over them.

use std::collections::HashMap;
use std::sync::{Mutex, OnceLock};
use std::time::Instant;

/// Consecutive failed pulls before an extension is pruned from the registry.
const MAX_MISSES: u32 = 3;

#[derive(Clone)]
pub struct Extension {
    pub name: String,
    pub script_url: String,
    /// Reset on (re)register and on each successful pull. Reserved for a future TTL sweep; the
    /// active liveness signal today is `misses`.
    pub last_seen: Instant,
    /// Consecutive failed pulls; the entry is dropped once this reaches MAX_MISSES.
    pub misses: u32,
}

fn registry() -> &'static Mutex<HashMap<String, Extension>> {
    static REGISTRY: OnceLock<Mutex<HashMap<String, Extension>>> = OnceLock::new();
    REGISTRY.get_or_init(|| Mutex::new(HashMap::new()))
}

/// Idempotent: same name replaces script_url and resets liveness (last_seen, misses=0).
pub fn register(name: String, script_url: String) {
    register_in(&mut registry().lock().unwrap(), name, script_url, Instant::now());
}

/// Best-effort removal on clean shutdown. No-op if absent.
pub fn unregister(name: &str) {
    registry().lock().unwrap().remove(name);
}

/// Snapshot of the registered extensions for the catalog merge and the keypress path.
pub fn list() -> Vec<Extension> {
    registry().lock().unwrap().values().cloned().collect()
}

/// Record the outcome of a catalog pull. On success, reset liveness; on failure, increment misses
/// and prune at MAX_MISSES. Returns false if the entry was pruned (or was already absent).
pub fn record_pull(name: &str, ok: bool) -> bool {
    record_pull_in(&mut registry().lock().unwrap(), name, ok, Instant::now())
}

// --- pure logic (unit-tested without the global) ---------------------------------------------

fn register_in(map: &mut HashMap<String, Extension>, name: String, script_url: String, now: Instant) {
    map.insert(
        name.clone(),
        Extension { name, script_url, last_seen: now, misses: 0 },
    );
}

fn record_pull_in(map: &mut HashMap<String, Extension>, name: &str, ok: bool, now: Instant) -> bool {
    let Some(ext) = map.get_mut(name) else {
        return false;
    };
    if ok {
        ext.last_seen = now;
        ext.misses = 0;
        true
    } else {
        ext.misses += 1;
        if ext.misses >= MAX_MISSES {
            map.remove(name);
            false
        } else {
            true
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn url_of<'a>(map: &'a HashMap<String, Extension>, name: &str) -> Option<&'a str> {
        map.get(name).map(|e| e.script_url.as_str())
    }

    #[test]
    fn register_then_lookup() {
        let mut map = HashMap::new();
        let now = Instant::now();
        register_in(&mut map, "ext".into(), "http://127.0.0.1:9005".into(), now);
        assert_eq!(url_of(&map, "ext"), Some("http://127.0.0.1:9005"));
    }

    #[test]
    fn re_register_replaces_url_and_resets_misses() {
        let mut map = HashMap::new();
        let now = Instant::now();
        register_in(&mut map, "ext".into(), "http://127.0.0.1:9005".into(), now);
        // Accrue a miss, then re-register: the URL is replaced and misses reset to 0.
        record_pull_in(&mut map, "ext", false, now);
        assert_eq!(map.get("ext").unwrap().misses, 1);
        register_in(&mut map, "ext".into(), "http://127.0.0.1:9999".into(), now);
        assert_eq!(url_of(&map, "ext"), Some("http://127.0.0.1:9999"));
        assert_eq!(map.get("ext").unwrap().misses, 0);
    }

    #[test]
    fn unregister_is_a_noop_when_absent() {
        let mut map: HashMap<String, Extension> = HashMap::new();
        assert!(map.remove("ghost").is_none());
    }

    #[test]
    fn prunes_after_max_misses() {
        let mut map = HashMap::new();
        let now = Instant::now();
        register_in(&mut map, "ext".into(), "http://127.0.0.1:9005".into(), now);
        // First two misses keep the entry; the third prunes it.
        assert!(record_pull_in(&mut map, "ext", false, now));
        assert!(record_pull_in(&mut map, "ext", false, now));
        assert!(!record_pull_in(&mut map, "ext", false, now));
        assert!(!map.contains_key("ext"));
    }

    #[test]
    fn success_resets_misses() {
        let mut map = HashMap::new();
        let now = Instant::now();
        register_in(&mut map, "ext".into(), "http://127.0.0.1:9005".into(), now);
        record_pull_in(&mut map, "ext", false, now);
        record_pull_in(&mut map, "ext", false, now);
        // A successful pull clears the accrued misses, so the next failure doesn't prune.
        record_pull_in(&mut map, "ext", true, now);
        assert_eq!(map.get("ext").unwrap().misses, 0);
        assert!(record_pull_in(&mut map, "ext", false, now));
        assert!(map.contains_key("ext"));
    }

    #[test]
    fn record_pull_on_absent_returns_false() {
        let mut map: HashMap<String, Extension> = HashMap::new();
        assert!(!record_pull_in(&mut map, "ghost", true, Instant::now()));
    }
}
