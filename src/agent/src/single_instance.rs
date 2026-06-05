//! Single-instance lock via a Win32 named mutex — mirror of agent/single_instance.py.
//!
//! Two agents in parallel = two WH_KEYBOARD_LL hooks, so each keystroke is handled twice
//! (shortcut fired twice). This notably happens at install: the [Run] postinstall launches the
//! agent (--open), and a Startup shortcut at logon can overlap a manual launch via the Start
//! Menu shortcut.
//!
//! A named mutex is the idiomatic Windows lock: the OS releases it on process death (no orphan
//! after a crash, unlike a lockfile), and it's more reliable than relying on the web port bind
//! (which retries on failure).

/// The OS error code returned when the named object already exists.
#[cfg(windows)]
const ERROR_ALREADY_EXISTS: u32 = 183;

/// The mutex handle MUST stay alive for the whole process lifetime: if dropped, the mutex is
/// released and a 2nd instance could acquire it. We hold it in a 'static via Box::leak from
/// acquire(), so it lives until the process exits.
#[cfg(windows)]
pub fn acquire() -> bool {
    acquire_named("Protocol0-Detector")
}

/// Tries to take the lock. True if we're the 1st instance, False if another is running.
///
/// The mutex name stays "Protocol0-Detector" (stable internal identity) even after the
/// detector -> agent rename: the installer kills the old exe before installing the new one, so
/// two versions never coexist, and renaming it would gain nothing.
#[cfg(windows)]
fn acquire_named(name: &str) -> bool {
    use windows::core::HSTRING;
    use windows::Win32::Foundation::GetLastError;
    use windows::Win32::System::Threading::CreateMutexW;

    // SAFETY: CreateMutexW with a named mutex. We intentionally leak the returned handle (via
    // Box::leak of the HSTRING is not needed — the HANDLE itself is what must live; we leak it
    // by never closing it and storing it in a leaked Box) so it outlives this function for the
    // whole process.
    unsafe {
        let wide = HSTRING::from(name);
        match CreateMutexW(None, false, &wide) {
            Ok(handle) => {
                // Leak the handle so it's never closed -> mutex held for the process lifetime.
                let boxed = Box::new(handle);
                Box::leak(boxed);
                GetLastError().0 != ERROR_ALREADY_EXISTS
            }
            Err(_) => {
                // If we can't even create the mutex, don't block startup (degrade to "first").
                true
            }
        }
    }
}

#[cfg(not(windows))]
pub fn acquire() -> bool {
    true
}
