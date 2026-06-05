//! Detect whether an Ableton Live process is running (anywhere, not just foreground) — mirror
//! of agent/process_check.py.
//!
//! Used by /status (web page + systray) to tell "Ableton not running" from "Ableton running
//! but control surface not activated". Windows-specific.
//!
//! Critical match rule: the Ableton exe is `Ableton Live <N> <Edition>.exe` (varies by version
//! AND edition -> never match the full name). We match the prefix "ableton live " WITH the
//! trailing space: that covers every edition/version while excluding `Ableton Index.exe` (the
//! library indexer, which runs in parallel).
//!
//! Unlike the Python agent, which shelled out to `tasklist`, we enumerate processes directly
//! via Toolhelp32Snapshot — no subprocess spawn, no console-flash workaround, lighter.

/// Prefix WITH a trailing space: excludes "Ableton Index.exe" and a hypothetical
/// "Ableton Live.exe" without an edition suffix (never observed, but we stay strict).
const ABLETON_EXE_PREFIX: &str = "ableton live ";

/// True if the image name (basename, e.g. 'Ableton Live 12 Suite.exe') is the DAW.
pub fn matches_ableton(image_name: &str) -> bool {
    image_name
        .trim()
        .to_lowercase()
        .starts_with(ABLETON_EXE_PREFIX)
}

#[cfg(windows)]
pub fn ableton_is_running() -> bool {
    use windows::Win32::Foundation::CloseHandle;
    use windows::Win32::System::Diagnostics::ToolHelp::{
        CreateToolhelp32Snapshot, Process32FirstW, Process32NextW, PROCESSENTRY32W,
        TH32CS_SNAPPROCESS,
    };

    // SAFETY: standard Toolhelp32 snapshot walk. We close the snapshot handle on every exit
    // path. PROCESSENTRY32W requires dwSize set before the first call.
    unsafe {
        let Ok(snapshot) = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0) else {
            tracing::warn!("CreateToolhelp32Snapshot failed");
            return false;
        };

        let mut entry = PROCESSENTRY32W {
            dwSize: std::mem::size_of::<PROCESSENTRY32W>() as u32,
            ..Default::default()
        };

        let mut found = false;
        if Process32FirstW(snapshot, &mut entry).is_ok() {
            loop {
                let name = wide_to_string(&entry.szExeFile);
                if matches_ableton(&name) {
                    found = true;
                    break;
                }
                if Process32NextW(snapshot, &mut entry).is_err() {
                    break;
                }
            }
        }
        let _ = CloseHandle(snapshot);
        found
    }
}

#[cfg(not(windows))]
pub fn ableton_is_running() -> bool {
    false
}

/// Converts a fixed-size, NUL-terminated UTF-16 buffer (szExeFile) to a String.
#[cfg(windows)]
fn wide_to_string(buf: &[u16]) -> String {
    let len = buf.iter().position(|&c| c == 0).unwrap_or(buf.len());
    String::from_utf16_lossy(&buf[..len])
}

#[cfg(test)]
mod tests {
    use super::matches_ableton;

    #[test]
    fn matches_editions_and_versions() {
        assert!(matches_ableton("Ableton Live 12 Suite.exe"));
        assert!(matches_ableton("Ableton Live 12 Intro.exe"));
        assert!(matches_ableton("Ableton Live 13 Standard.exe"));
        // Case/whitespace tolerant.
        assert!(matches_ableton("  ABLETON LIVE 12 Trial.exe  "));
    }

    #[test]
    fn excludes_indexer_and_others() {
        assert!(!matches_ableton("Ableton Index.exe")); // the library indexer
        assert!(!matches_ableton("chrome.exe"));
        assert!(!matches_ableton("")); // no foreground
    }
}
