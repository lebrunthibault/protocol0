//! Detect whether the user is typing into a text field, to suspend BARE single-key bindings
//! (e.g. `a`, `z`) while they are. Without this, a single-key shortcut would swallow the
//! keystroke and the user could never type those letters into Ableton's browser search or a
//! rename field. Bindings WITH a modifier (`ctrl+a`, `f5`) are never text input and are not gated.
//!
//! How we detect it: UI Automation. Ableton draws its own text fields (custom UI), so they have
//! no standard Win32 caret — `GetGUIThreadInfo().hwndCaret` stays null even while typing
//! (verified empirically). But UIA *does* expose them: the focused element's ControlType is
//! `UIA_EditControlTypeId` (50004) when a search/rename box has focus. That is our signal.
//!
//! Why a background thread + atomic flag, not a call from the hook: `GetFocusedElement` is
//! cross-process COM and can stall for milliseconds. The low-level keyboard hook must never
//! block (Windows silently drops slow hooks). So a dedicated MTA thread polls UIA a few times a
//! second and publishes the result into an `AtomicBool`; the hook just reads the flag — a single
//! relaxed atomic load, effectively free. ~120 ms latency is irrelevant here: a human cannot
//! type within 120 ms of clicking into a field.
//!
//! Windows-specific. macOS port: an equivalent poll of AXFocusedUIElement, checking its role
//! against kAXTextFieldRole / kAXTextAreaRole, would set the same flag (isolated here like
//! `foreground.rs`).

use std::sync::atomic::{AtomicBool, Ordering};

/// Published by the UIA poll thread, read by the keyboard hook. `false` until the service starts
/// and on every failure path, so we degrade toward "shortcut works" rather than "keystroke stolen".
static TEXT_FIELD_FOCUSED: AtomicBool = AtomicBool::new(false);

/// True when a text-edit control currently has UIA focus (user is typing into a field). A plain
/// atomic load — safe and instant to call from inside the keyboard hook.
pub fn text_field_has_focus() -> bool {
    TEXT_FIELD_FOCUSED.load(Ordering::Relaxed)
}

/// UIA_EditControlTypeId — the focused-element ControlType for a single-line/standard text box
/// (Ableton's browser "Search box" and track/clip rename fields report this). We intentionally
/// gate on Edit only: Document/Text controls (50030/50020) are arrangement timeline / labels, not
/// places the user types short text, and treating them as "typing" would wrongly disable shortcuts.
#[cfg(windows)]
const UIA_EDIT_CONTROL_TYPE_ID: i32 = 50004;

/// Starts the background UIA poll. Spawns one detached MTA thread that owns the COM apartment and
/// the IUIAutomation instance for the process lifetime, updating the flag. Idempotent in practice
/// (call once at startup). No-op off Windows.
#[cfg(windows)]
pub fn start_text_focus_service() {
    std::thread::Builder::new()
        .name("uia-text-focus".into())
        .spawn(|| {
            if let Err(e) = run_poll_loop() {
                tracing::warn!("text-focus UIA service stopped: {e} (single-key gating disabled)");
            }
        })
        .ok();
}

#[cfg(windows)]
fn run_poll_loop() -> windows::core::Result<()> {
    use std::time::Duration;
    use windows::Win32::System::Com::{
        CoCreateInstance, CoInitializeEx, CLSCTX_INPROC_SERVER, COINIT_MULTITHREADED,
    };
    use windows::Win32::UI::Accessibility::{CUIAutomation, IUIAutomation};

    // SAFETY: this thread owns its COM apartment for its whole life; we never CoUninitialize
    // because the thread lives until process exit. CoCreateInstance yields the UIA root.
    unsafe {
        let _ = CoInitializeEx(None, COINIT_MULTITHREADED);
        let automation: IUIAutomation =
            CoCreateInstance(&CUIAutomation, None, CLSCTX_INPROC_SERVER)?;

        loop {
            // Best-effort: a failed read just leaves the flag as-is for this tick. GetFocused
            // element + CurrentControlType are the only COM calls; both are cheap on this thread.
            let is_edit = match automation.GetFocusedElement() {
                Ok(el) => match el.CurrentControlType() {
                    Ok(ct) => ct.0 == UIA_EDIT_CONTROL_TYPE_ID,
                    Err(_) => false,
                },
                Err(_) => false,
            };
            TEXT_FIELD_FOCUSED.store(is_edit, Ordering::Relaxed);
            std::thread::sleep(Duration::from_millis(120));
        }
    }
}

#[cfg(not(windows))]
pub fn start_text_focus_service() {}
