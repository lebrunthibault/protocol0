//! Detect whether Ableton is the foreground window — mirror of agent/foreground.py.
//!
//! Reproduces the `#IfWinActive ahk_exe Ableton Live 12 Suite.exe` of mappings.ahk: the
//! shortcut only fires when Ableton has focus. Avoids stealing keys from other apps and sorts
//! out cohabitation with the config frontend.
//!
//! Windows-specific (Win32). Isolated here for the future macOS port (equivalent:
//! NSWorkspace.frontmostApplication).

use crate::process_check::matches_ableton;

#[cfg(windows)]
pub fn ableton_is_foreground() -> bool {
    // _foreground_process_name returns a full path (QueryFullProcessImageNameW) -> take the
    // basename before applying the shared match rule.
    let path = foreground_process_path();
    let basename = path
        .rsplit(['\\', '/'])
        .next()
        .unwrap_or(&path)
        .to_string();
    matches_ableton(&basename)
}

#[cfg(windows)]
fn foreground_process_path() -> String {
    use windows::Win32::Foundation::{CloseHandle, HWND, MAX_PATH};
    use windows::Win32::System::Threading::{
        OpenProcess, QueryFullProcessImageNameW, PROCESS_NAME_FORMAT,
        PROCESS_QUERY_LIMITED_INFORMATION,
    };
    use windows::Win32::UI::WindowsAndMessaging::{
        GetForegroundWindow, GetWindowThreadProcessId,
    };

    // SAFETY: standard foreground-window -> pid -> process-handle -> image-name walk. We
    // OpenProcess with the minimal QUERY_LIMITED right and close the handle on every path.
    unsafe {
        let hwnd: HWND = GetForegroundWindow();
        if hwnd.0.is_null() {
            return String::new();
        }
        let mut pid: u32 = 0;
        GetWindowThreadProcessId(hwnd, Some(&mut pid));
        if pid == 0 {
            return String::new();
        }
        let Ok(handle) = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, pid) else {
            return String::new();
        };

        let mut buf = [0u16; MAX_PATH as usize];
        let mut size = buf.len() as u32;
        let ok = QueryFullProcessImageNameW(
            handle,
            PROCESS_NAME_FORMAT(0),
            windows::core::PWSTR(buf.as_mut_ptr()),
            &mut size,
        )
        .is_ok();
        let _ = CloseHandle(handle);

        if ok {
            String::from_utf16_lossy(&buf[..size as usize])
        } else {
            String::new()
        }
    }
}

#[cfg(not(windows))]
pub fn ableton_is_foreground() -> bool {
    false
}
