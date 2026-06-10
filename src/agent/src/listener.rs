//! Keyboard capture via a low-level Windows hook (WH_KEYBOARD_LL) -> combo resolution ->
//! action callback. Mirror of agent/listener.py.
//!
//! Unlike an observe-only listener, this owns the hook and controls its return value per
//! event, so it can SUPPRESS the trigger combo (return 1, skip CallNextHookEx) and stop it
//! from leaking to Ableton. Injection (key_emitter) is done separately; capture is done here
//! so the physical trigger key never reaches the foreground app.
//!
//! Architecture — decide synchronously, defer execution:
//!   - The hook proc runs synchronously inside a message pump on its own thread. Windows drops
//!     hooks whose callback is too slow, so the proc only DECIDES (suppress/pass) using cheap
//!     in-memory state and enqueues the matched binding.
//!   - A worker thread runs the actual action (injection / HTTP), off the hook thread.
//!
//! All decision logic lives in the pure `decide()` method (testable without a real hook); the
//! Win32 proc is a thin marshaller around it.
//!
//! The canonical combo vocabulary (modifier order, key namespace) lives in `keymap`, shared
//! with the emitter so capture and injection stay in lock-step.

use std::collections::HashSet;
use std::sync::mpsc::{Receiver, Sender};
use std::sync::Mutex;

use crate::config::{Binding, ShortcutConfig};
use crate::foreground::ableton_is_foreground;
use crate::keymap;

/// What a fired binding carries to the worker: the binding plus a snapshot of the modifiers
/// physically held at decision time (so the worker doesn't read mutable state late).
pub type FiredBinding = (Binding, HashSet<String>);

/// A "single character" key produces typed text: letters, digits, and the punctuation glyphs —
/// every name from `keymap` that resolves to exactly one char. Named keys (`space`, `enter`,
/// `f5`, `up`) are multi-char and excluded; they are never text input. Used to decide which
/// bindings to suspend while a text field has focus.
fn is_single_char_key(name: &str) -> bool {
    name.chars().count() == 1
}

/// Pure capture state + decision logic, with NO Win32 dependency. Unit-tested directly,
/// exactly like the Python `_decide`.
pub struct DecideState {
    config: ShortcutConfig,
    pressed_modifiers: HashSet<String>,
    /// Non-modifier keys currently held (by vk). Used to act on the rising edge only: Windows
    /// repeats key-down while a key is held (auto-repeat), which would fire the action
    /// multiple times for a single keystroke.
    held_keys: HashSet<u32>,
    /// vks whose key-down we suppressed, so we also suppress the matching key-up (keeps
    /// down/up balanced for Ableton, which never saw the down).
    suppressed_down: HashSet<u32>,
}

impl DecideState {
    pub fn new(config: ShortcutConfig) -> Self {
        Self {
            config,
            pressed_modifiers: HashSet::new(),
            held_keys: HashSet::new(),
            suppressed_down: HashSet::new(),
        }
    }

    /// Updates capture state and returns Some(fired binding) to enqueue + suppress, or a plain
    /// suppress/pass decision. The return is (suppress, fired): `suppress` is whether to
    /// swallow the event; `fired` is the binding to run (only set on a fresh match).
    ///
    /// Has no I/O except the config lookup (in-memory), the foreground check, and the text-focus
    /// check (both only on matched combos) — both are injected so tests can drive them.
    /// `text_focus` returns true when a text-edit control has focus (user is typing into a field):
    /// a BARE single-key binding is then passed through instead of suppressed, so the keystroke
    /// reaches the field. Combos with a modifier are never gated this way.
    pub fn decide(
        &mut self,
        vk: u32,
        scan: u32,
        is_down: bool,
        injected: bool,
        foreground: impl Fn() -> bool,
        text_focus: impl Fn() -> bool,
    ) -> (bool, Option<FiredBinding>) {
        if injected {
            // Our own synthesized keys: ignore entirely (don't re-trigger, don't track).
            return (false, None);
        }

        if let Some(modifier) = keymap::modifier_token(vk) {
            // Modifiers are tracked but never suppressed: the user's ctrl/alt must keep working
            // for everything else.
            if is_down {
                self.pressed_modifiers.insert(modifier.to_string());
            } else {
                self.pressed_modifiers.remove(modifier);
            }
            return (false, None);
        }

        if !is_down {
            self.held_keys.remove(&vk);
            if self.suppressed_down.remove(&vk) {
                return (true, None); // balance the suppressed down: swallow its up too
            }
            return (false, None);
        }

        // key-down. Auto-repeat: same vk still held -> don't re-dispatch, but keep suppressing
        // if we suppressed the original down.
        if self.held_keys.contains(&vk) {
            return (self.suppressed_down.contains(&vk), None);
        }
        self.held_keys.insert(vk);

        let Some(name) = keymap::key_name_from_vk(vk, scan) else {
            return (false, None);
        };
        let combo = self.build_combo(&name);
        self.config.reload_if_changed();
        let Some(binding) = self.config.get(&combo).cloned() else {
            return (false, None);
        };
        if !foreground() {
            tracing::debug!("combo {combo} ignored (Ableton not foreground)");
            return (false, None);
        }
        // Suspend BARE single-key bindings while the user is typing into a text field (browser
        // search, renaming): let the keystroke reach the field instead of firing/suppressing.
        // Combos with a modifier (ctrl+a, alt+x) are never text input, so they bypass this gate.
        if self.pressed_modifiers.is_empty() && is_single_char_key(&name) && text_focus() {
            tracing::debug!("combo {combo} ignored (text field has focus)");
            return (false, None);
        }
        tracing::info!("combo {combo} -> {} {:?}", binding.action, binding.params);
        self.suppressed_down.insert(vk);
        let snapshot = self.pressed_modifiers.clone();
        (true, Some((binding, snapshot)))
    }

    fn build_combo(&self, key_name: &str) -> String {
        let mut parts: Vec<&str> = keymap::MODIFIER_ORDER
            .iter()
            .copied()
            .filter(|m| self.pressed_modifiers.contains(*m))
            .collect();
        parts.push(key_name);
        parts.join("+")
    }
}

#[cfg(test)]
mod tests {
    //! The listener's decision logic: rising-edge dispatch, per-event suppression, and
    //! self-ignore of injected keys. Drives the pure `decide()` seam directly (the Win32 hook
    //! itself can't run in a unit test). Mirror of test_listener_autorepeat.py.
    //!
    //! VKs are chosen so the positional fallback in keymap::key_name_from_vk yields the letter
    //! deterministically regardless of host keyboard layout: on a non-AZERTY CI host ToUnicodeEx
    //! returns the same letter, and the positional branch (0x41..=0x5A) is the floor. We use
    //! 'u'/'e'/'t' as in the Python tests.

    use super::*;
    use std::collections::HashMap;

    const VK_U: u32 = 0x55; // 'u'
    const VK_E: u32 = 0x45; // 'e'
    const VK_T: u32 = 0x54; // 't'
    const VK_CTRL: u32 = 0x11;

    fn binding(combo: &str, action: &str) -> Binding {
        Binding {
            combo: combo.to_string(),
            action: action.to_string(),
            params: HashMap::new(),
        }
    }

    fn state(bindings: Vec<Binding>) -> DecideState {
        DecideState::new(ShortcutConfig::from_bindings(bindings))
    }

    fn default_state() -> DecideState {
        state(vec![binding("u", "load_device")])
    }

    /// key-down, foreground = true, no text field, unless overridden. Returns (suppress, fired?).
    fn down(s: &mut DecideState, vk: u32) -> (bool, bool) {
        let (sup, fired) = s.decide(vk, 0, true, false, || true, || false);
        (sup, fired.is_some())
    }

    fn down_fg(s: &mut DecideState, vk: u32, fg: bool) -> (bool, bool) {
        let (sup, fired) = s.decide(vk, 0, true, false, || fg, || false);
        (sup, fired.is_some())
    }

    /// key-down with the text-field gate driven explicitly.
    fn down_text(s: &mut DecideState, vk: u32, text_focus: bool) -> (bool, bool) {
        let (sup, fired) = s.decide(vk, 0, true, false, || true, || text_focus);
        (sup, fired.is_some())
    }

    fn down_injected(s: &mut DecideState, vk: u32) -> (bool, bool) {
        let (sup, fired) = s.decide(vk, 0, true, true, || true, || false);
        (sup, fired.is_some())
    }

    fn up(s: &mut DecideState, vk: u32) -> bool {
        s.decide(vk, 0, false, false, || true, || false).0
    }

    #[test]
    fn autorepeat_fires_once() {
        let mut s = default_state();
        let fires = [down(&mut s, VK_U), down(&mut s, VK_U), down(&mut s, VK_U)];
        assert_eq!(fires.iter().filter(|(_, f)| *f).count(), 1);
    }

    #[test]
    fn press_release_press_fires_twice() {
        let mut s = default_state();
        let a = down(&mut s, VK_U).1;
        up(&mut s, VK_U);
        let b = down(&mut s, VK_U).1;
        assert!(a && b);
    }

    #[test]
    fn injected_events_are_ignored() {
        let mut s = default_state();
        assert_eq!(down_injected(&mut s, VK_U), (false, false));
        // A real keystroke dispatches normally.
        assert!(down(&mut s, VK_U).1);
    }

    #[test]
    fn matched_combo_suppresses() {
        let mut s = default_state();
        assert_eq!(down(&mut s, VK_U), (true, true));
    }

    #[test]
    fn unmatched_combo_passes() {
        let mut s = default_state();
        assert_eq!(down(&mut s, VK_T), (false, false));
    }

    #[test]
    fn matched_but_not_foreground_passes() {
        let mut s = default_state();
        assert_eq!(down_fg(&mut s, VK_U, false), (false, false));
    }

    #[test]
    fn keyup_of_suppressed_down_is_suppressed() {
        let mut s = default_state();
        assert_eq!(down(&mut s, VK_U), (true, true));
        assert!(up(&mut s, VK_U));
        // A subsequent unrelated up is not suppressed.
        assert!(!up(&mut s, VK_T));
    }

    #[test]
    fn keyup_of_passed_down_is_not_suppressed() {
        let mut s = default_state();
        down(&mut s, VK_T); // unbound -> passed
        assert!(!up(&mut s, VK_T));
    }

    #[test]
    fn autorepeat_of_suppressed_key_keeps_suppressing() {
        let mut s = default_state();
        assert_eq!(down(&mut s, VK_U), (true, true));
        assert_eq!(down(&mut s, VK_U).0, true); // repeat: still suppressed
    }

    #[test]
    fn modifier_tracking_builds_combo() {
        let mut s = state(vec![binding("ctrl+e", "send_keys")]);
        assert_eq!(down(&mut s, VK_CTRL), (false, false)); // modifier never suppressed
        // tap 'e' with ctrl held -> fires the ctrl+e binding, with the held snapshot.
        let (sup, fired) = s.decide(VK_E, 0, true, false, || true, || false);
        assert!(sup);
        let (b, mods) = fired.expect("should fire");
        assert_eq!(b.combo, "ctrl+e");
        assert_eq!(mods, HashSet::from(["ctrl".to_string()]));
    }

    #[test]
    fn modifiers_are_never_suppressed() {
        let mut s = default_state();
        assert_eq!(down(&mut s, VK_CTRL), (false, false));
        assert!(!up(&mut s, VK_CTRL));
    }

    #[test]
    fn bare_single_key_passes_when_text_field_focused() {
        // 'u' bound to load_device. While a text field has focus, the keystroke must reach the
        // field: not fired, not suppressed.
        let mut s = default_state();
        assert_eq!(down_text(&mut s, VK_U, true), (false, false));
    }

    #[test]
    fn bare_single_key_fires_when_no_text_field() {
        let mut s = default_state();
        assert_eq!(down_text(&mut s, VK_U, false), (true, true));
    }

    #[test]
    fn modifier_combo_fires_even_with_text_field_focused() {
        // ctrl+e is never typed text -> the gate must NOT apply when a modifier is held.
        let mut s = state(vec![binding("ctrl+e", "send_keys")]);
        assert_eq!(down(&mut s, VK_CTRL), (false, false));
        let (sup, fired) = s.decide(VK_E, 0, true, false, || true, || true);
        assert!(sup);
        assert!(fired.is_some());
    }

    #[test]
    fn is_single_char_key_classifies_correctly() {
        assert!(is_single_char_key("a"));
        assert!(is_single_char_key("5"));
        assert!(is_single_char_key(","));
        assert!(!is_single_char_key("space"));
        assert!(!is_single_char_key("enter"));
        assert!(!is_single_char_key("f5"));
        assert!(!is_single_char_key("up"));
    }
}

// ---------------------------------------------------------------------------
// Win32 hook plumbing. The proc is a bare extern fn with no user-data slot, so the live
// DecideState is reached via a process-global behind a Mutex (a single listener exists). This
// mirrors how listener.py kept the hook state on a single instance.
// ---------------------------------------------------------------------------

#[cfg(windows)]
mod hook {
    use super::*;
    use std::sync::OnceLock;
    use windows::Win32::Foundation::{LPARAM, LRESULT, WPARAM};
    use windows::Win32::UI::WindowsAndMessaging::{
        CallNextHookEx, KBDLLHOOKSTRUCT, WM_KEYDOWN, WM_SYSKEYDOWN,
    };

    const LLKHF_INJECTED: u32 = 0x10;
    const HC_ACTION: i32 = 0;

    /// The single live decision state, plus a channel to the worker. Set by start().
    static STATE: OnceLock<Mutex<DecideState>> = OnceLock::new();
    static SENDER: OnceLock<Sender<FiredBinding>> = OnceLock::new();

    pub fn install_state(state: DecideState, sender: Sender<FiredBinding>) {
        let _ = STATE.set(Mutex::new(state));
        let _ = SENDER.set(sender);
    }

    /// The low-level keyboard hook proc. Thin marshaller: extract the event, ask decide, never
    /// block. Returns 1 to suppress.
    pub unsafe extern "system" fn proc(code: i32, wparam: WPARAM, lparam: LPARAM) -> LRESULT {
        if code == HC_ACTION {
            let kb = &*(lparam.0 as *const KBDLLHOOKSTRUCT);
            let injected = (kb.flags.0 & LLKHF_INJECTED) != 0;
            let msg = wparam.0 as u32;
            let is_down = msg == WM_KEYDOWN || msg == WM_SYSKEYDOWN;

            if let Some(state) = STATE.get() {
                // Keep the lock as short as possible: decide, then drop before sending.
                let decision = {
                    if let Ok(mut guard) = state.lock() {
                        guard.decide(
                            kb.vkCode,
                            kb.scanCode,
                            is_down,
                            injected,
                            ableton_is_foreground,
                            crate::text_focus::text_field_has_focus,
                        )
                    } else {
                        (false, None)
                    }
                };
                let (suppress, fired) = decision;
                if let Some(fired) = fired {
                    if let Some(sender) = SENDER.get() {
                        let _ = sender.send(fired);
                    }
                }
                if suppress {
                    return LRESULT(1); // suppress: do NOT propagate to the foreground app
                }
            }
        }
        CallNextHookEx(None, code, wparam, lparam)
    }
}

/// The keyboard listener: owns the hook thread + worker thread.
pub struct ShortcutListener {
    hook_thread: Option<std::thread::JoinHandle<()>>,
    worker_thread: Option<std::thread::JoinHandle<()>>,
    hook_tid: std::sync::Arc<Mutex<Option<u32>>>,
}

impl ShortcutListener {
    /// Starts capture. `on_action` runs each fired binding on the worker thread, off the hook.
    #[cfg(windows)]
    pub fn start(
        config: ShortcutConfig,
        on_action: impl Fn(&Binding, &HashSet<String>) + Send + 'static,
    ) -> Self {
        use std::sync::mpsc::channel;

        let (tx, rx): (Sender<FiredBinding>, Receiver<FiredBinding>) = channel();
        hook::install_state(DecideState::new(config), tx);

        // Worker thread: run actions off the hook thread.
        let worker_thread = std::thread::spawn(move || {
            while let Ok((binding, held)) = rx.recv() {
                on_action(&binding, &held);
            }
        });

        // Hook thread: install the hook and pump messages (the hook only fires while this
        // thread pumps). PostThreadMessage(WM_QUIT) from stop() ends the loop.
        let hook_tid = std::sync::Arc::new(Mutex::new(None));
        let hook_tid_for_thread = hook_tid.clone();
        let hook_thread = std::thread::spawn(move || {
            run_hook(hook_tid_for_thread);
        });

        tracing::info!("keyboard listener started");
        Self {
            hook_thread: Some(hook_thread),
            worker_thread: Some(worker_thread),
            hook_tid,
        }
    }

    #[cfg(not(windows))]
    pub fn start(
        _config: ShortcutConfig,
        _on_action: impl Fn(&Binding, &HashSet<String>) + Send + 'static,
    ) -> Self {
        Self {
            hook_thread: None,
            worker_thread: None,
            hook_tid: std::sync::Arc::new(Mutex::new(None)),
        }
    }

    pub fn stop(&mut self) {
        #[cfg(windows)]
        {
            use windows::Win32::UI::WindowsAndMessaging::{PostThreadMessageW, WM_QUIT};
            if let Some(tid) = *self.hook_tid.lock().unwrap() {
                // SAFETY: posting WM_QUIT to the hook thread's message queue ends its GetMessage
                // loop, which then unhooks. The worker ends when its channel sender is dropped
                // (the hook's static sender lives for the process, so we don't rely on that —
                // joining the hook thread is the signal that capture stopped).
                unsafe {
                    let _ = PostThreadMessageW(tid, WM_QUIT, WPARAM_ZERO, LPARAM_ZERO);
                }
            }
        }
        if let Some(t) = self.hook_thread.take() {
            let _ = t.join();
        }
        // Worker is detached on the static channel; we don't force-join it (the process is
        // shutting down). Drop the handle.
        let _ = self.worker_thread.take();
    }
}

#[cfg(windows)]
use windows::Win32::Foundation::{LPARAM as LPARAM_T, WPARAM as WPARAM_T};
#[cfg(windows)]
const WPARAM_ZERO: WPARAM_T = WPARAM_T(0);
#[cfg(windows)]
const LPARAM_ZERO: LPARAM_T = LPARAM_T(0);

/// Installs the hook on the current thread and pumps messages until WM_QUIT.
#[cfg(windows)]
fn run_hook(hook_tid: std::sync::Arc<Mutex<Option<u32>>>) {
    use windows::Win32::System::Threading::GetCurrentThreadId;
    use windows::Win32::UI::WindowsAndMessaging::{
        DispatchMessageW, GetMessageW, SetWindowsHookExW, TranslateMessage,
        UnhookWindowsHookEx, MSG, WH_KEYBOARD_LL,
    };

    // SAFETY: install a global WH_KEYBOARD_LL hook with our proc; pump messages so it fires;
    // unhook on exit. SetWindowsHookExW with a module of None + thread 0 is the documented way
    // to install a global LL hook from this process.
    unsafe {
        *hook_tid.lock().unwrap() = Some(GetCurrentThreadId());

        let hhook = match SetWindowsHookExW(WH_KEYBOARD_LL, Some(hook::proc), None, 0) {
            Ok(h) => h,
            Err(e) => {
                tracing::error!("SetWindowsHookExW failed: {e}");
                return;
            }
        };

        let mut msg = MSG::default();
        // GetMessageW returns 0 on WM_QUIT (posted by stop()).
        while GetMessageW(&mut msg, None, 0, 0).0 != 0 {
            let _ = TranslateMessage(&msg);
            DispatchMessageW(&msg);
        }
        let _ = UnhookWindowsHookEx(hhook);
    }
}
