//! Local keystroke injection: turn a canonical combo back into real key events — mirror of
//! agent/key_emitter.py.
//!
//! This is the execution side of a `send_keys` binding: pressing the user's combo
//! (e.g. ctrl+alt+q) makes the agent emit a native Ableton shortcut (e.g. ctrl+n) into the
//! foreground window. Unlike every other action, this does NOT go through the script's HTTP
//! API — most native Live commands have no LOM equivalent, so we replay the keystroke locally
//! via SendInput.
//!
//! Injection order is a chord, not a sequence: press modifiers, tap the main key, release
//! modifiers (in reverse). The agent's own listener ignores these synthesized keys because the
//! low-level hook sees the LLKHF_INJECTED flag on SendInput events, so a binding can't
//! re-trigger itself.
//!
//! Held-modifier neutralisation: the trigger combo's modifiers are usually still physically
//! down when we inject. If we just injected the target chord, the OS would see the user's
//! ctrl+alt PLUS our keys -> wrong shortcut. So we release the user's held modifiers first,
//! inject the clean target chord, then re-press whatever the user still holds.
//!
//! Combo vocabulary is the shared keymap (same tokens the listener captures), so what the UI
//! records is exactly what we replay.

use std::collections::HashSet;

use crate::keymap;

const VK_SHIFT: u16 = 0x10;

/// Canonical modifier token -> Win32 virtual-key code for injection.
fn modifier_vk(token: &str) -> Option<u16> {
    Some(match token {
        "ctrl" => 0x11,  // VK_CONTROL
        "alt" => 0x12,   // VK_MENU
        "shift" => 0x10, // VK_SHIFT
        "win" => 0x5B,   // VK_LWIN
        _ => return None,
    })
}

/// Canonical named (non-character) token -> Win32 virtual-key code.
fn named_vk(token: &str) -> Option<u16> {
    Some(match token {
        "space" => 0x20,
        "tab" => 0x09,
        "enter" => 0x0D,
        "esc" => 0x1B,
        "backspace" => 0x08,
        "delete" => 0x2E,
        "up" => 0x26,
        "down" => 0x28,
        "left" => 0x25,
        "right" => 0x27,
        "home" => 0x24,
        "end" => 0x23,
        "pageup" => 0x21,
        "pagedown" => 0x22,
        _ => return None,
    })
}

/// Canonical main-key token -> (VK to inject, whether Shift is required), or None if unsupported.
///
/// Digits are positional (ASCII '0'..'9' == VK 0x30..0x39), mirroring capture in keymap.rs —
/// they must NOT go through VkKeyScanW. Letters/punctuation DO go through VkKeyScanW so they land
/// correctly regardless of layout (mirrors capture naming them layout-aware via ToUnicodeEx).
/// f1..f12 and named keys map positionally and never need Shift. The `needs_shift` flag matters
/// for glyphs the layout produces only with Shift (e.g. '+' on US is Shift+'='): the canonical
/// namespace names keys by their unshifted glyph, but a future shifted glyph would still inject
/// correctly.
fn resolve_key_vk(token: &str) -> Option<(u16, bool)> {
    let chars: Vec<char> = token.chars().collect();
    // Digits are positional (mirror capture in keymap.rs): ASCII '0'..'9' == VK 0x30..0x39.
    // Must NOT go through VkKeyScanW — on AZERTY the top-row digit needs Shift, which would
    // inject the wrong native shortcut (Ctrl+Alt+Shift+3 instead of Ctrl+Alt+3).
    if chars.len() == 1 && chars[0].is_ascii_digit() {
        return Some((chars[0] as u16, false));
    }
    if chars.len() == 1
        && (chars[0].is_ascii_alphabetic() || keymap::PUNCTUATION.contains(&chars[0]))
    {
        return char_to_vk(chars[0]);
    }
    if chars.len() >= 2 && chars[0] == 'f' {
        if let Ok(n) = token[1..].parse::<u16>() {
            if (1..=12).contains(&n) {
                return Some((0x6F + n, false)); // VK_F1 = 0x70 -> f1 => 0x6F + 1
            }
            return None;
        }
    }
    named_vk(token).map(|vk| (vk, false))
}

#[cfg(windows)]
fn char_to_vk(c: char) -> Option<(u16, bool)> {
    use windows::Win32::UI::Input::KeyboardAndMouse::VkKeyScanW;
    // SAFETY: VkKeyScanW takes a UTF-16 code unit and returns the VK in the low byte and the
    // shift state in the high byte. -1 means no key for this char on the current layout.
    let res = unsafe { VkKeyScanW(c as u16) };
    if res == -1 {
        return None;
    }
    let vk = (res as u16) & 0xFF;
    // High byte bit 0 (value 1) = Shift required to produce this glyph on the current layout.
    let needs_shift = (res >> 8) & 0x01 != 0;
    Some((vk, needs_shift))
}

#[cfg(not(windows))]
fn char_to_vk(c: char) -> Option<(u16, bool)> {
    // Positional ASCII fallback for non-Windows builds (tests only). Punctuation has no stable
    // positional VK off-Windows, so only alphanumerics resolve here; none need shift.
    let up = c.to_ascii_uppercase();
    if up.is_ascii_alphanumeric() {
        Some((up as u16, false))
    } else {
        None
    }
}

/// Injects the canonical combo as a key chord. No-op (with a warning) if the combo can't be
/// parsed into known tokens.
///
/// `held_modifiers` are the canonical modifiers the user currently holds physically (from the
/// listener). The injection is a MINIMAL DIFF against them: held modifiers the target chord
/// also needs are left alone (the user's own keys serve the chord, like a human tapping the
/// main key while still holding ctrl+alt); only extra held modifiers are lifted, and only
/// missing target modifiers are pressed. This avoids releasing/re-pressing a modifier within
/// microseconds, which some apps coalesce or ignore.
pub fn send(combo: &str, held_modifiers: &HashSet<String>) {
    let parts: Vec<&str> = combo.split('+').filter(|p| !p.is_empty()).collect();
    let Some((key_token, mod_tokens)) = parts.split_last() else {
        tracing::warn!("send_keys: empty combo");
        return;
    };

    let mut mods = Vec::new();
    for m in mod_tokens {
        match modifier_vk(m) {
            Some(vk) => mods.push(vk),
            None => {
                tracing::warn!("send_keys: unknown modifier {m:?} in {combo:?}");
                return;
            }
        }
    }

    let Some((main, needs_shift)) = resolve_key_vk(key_token) else {
        tracing::warn!("send_keys: unsupported key {key_token:?} in {combo:?}");
        return;
    };

    // If the glyph is only reachable with Shift on this layout (e.g. '+' = Shift+'='), inject
    // Shift as part of the target chord. Avoid double-pressing if the combo already holds shift.
    if needs_shift && !mods.contains(&VK_SHIFT) {
        mods.push(VK_SHIFT);
    }

    // Real modifiers physically held (only ones we know how to press back).
    let held: Vec<u16> = held_modifiers
        .iter()
        .filter_map(|m| modifier_vk(m))
        .collect();

    let (to_lift, to_press) = chord_plan(&mods, &held);
    tracing::info!(
        "send_keys: injecting {combo:?} (main vk {main:#04x}, press {to_press:02x?}, lift {to_lift:02x?})"
    );
    inject_chord(&to_press, main, &to_lift);
}

/// Minimal diff between the physically held modifiers and the target chord's modifiers:
/// (to_lift, to_press). Held ∩ target stays down untouched — the user's own modifiers serve
/// the chord. Pure, so the parity-critical set logic is unit-testable.
fn chord_plan(target_mods: &[u16], held: &[u16]) -> (Vec<u16>, Vec<u16>) {
    let to_lift = held
        .iter()
        .copied()
        .filter(|m| !target_mods.contains(m))
        .collect();
    let to_press = target_mods
        .iter()
        .copied()
        .filter(|m| !held.contains(m))
        .collect();
    (to_lift, to_press)
}

/// 1) lift the held modifiers the chord must not see; 2) press the missing target modifiers,
/// tap the main key, release them in reverse; 3) restore what was lifted. Modifiers both held
/// and needed never appear here — they stay physically down throughout (see chord_plan).
#[cfg(windows)]
fn inject_chord(to_press: &[u16], main: u16, to_lift: &[u16]) {
    // 1) lift the held modifiers that would pollute the target chord.
    for &m in to_lift {
        key_event(m, true);
    }
    // 2) inject the missing part of the chord: press mods, tap main, release mods in reverse.
    for &m in to_press {
        key_event(m, false);
    }
    key_event(main, false);
    key_event(main, true);
    for &m in to_press.iter().rev() {
        key_event(m, true);
    }
    // 3) restore the modifiers the user is still holding.
    for &m in to_lift {
        key_event(m, false);
    }
}

/// Keys on the extended scan-code page (0xE0 prefix): the navigation cluster + arrows.
/// Without KEYEVENTF_EXTENDEDKEY their MapVirtualKeyW scan code is the numpad-shared one,
/// so apps reading scan codes would see numpad keys instead.
#[cfg(windows)]
fn is_extended(vk: u16) -> bool {
    // pageup, pagedown, end, home, left, up, right, down, delete
    matches!(vk, 0x21..=0x28 | 0x2E)
}

/// Sends one key down/up event via SendInput, carrying the real scan code alongside the VK
/// (a physical keystroke has both; apps that read the scan code ignore wVk-only events).
#[cfg(windows)]
fn key_event(vk: u16, up: bool) {
    use windows::Win32::UI::Input::KeyboardAndMouse::{
        MapVirtualKeyW, SendInput, INPUT, INPUT_0, INPUT_KEYBOARD, KEYBDINPUT, KEYBD_EVENT_FLAGS,
        KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP, MAPVK_VK_TO_VSC, VIRTUAL_KEY,
    };

    // SAFETY: pure table lookup in the current layout.
    let scan = unsafe { MapVirtualKeyW(vk as u32, MAPVK_VK_TO_VSC) } as u16;
    let mut flags = if up {
        KEYEVENTF_KEYUP
    } else {
        KEYBD_EVENT_FLAGS(0)
    };
    if is_extended(vk) {
        flags |= KEYEVENTF_EXTENDEDKEY;
    }
    let input = INPUT {
        r#type: INPUT_KEYBOARD,
        Anonymous: INPUT_0 {
            ki: KEYBDINPUT {
                wVk: VIRTUAL_KEY(vk),
                wScan: scan,
                dwFlags: flags,
                time: 0,
                dwExtraInfo: 0,
            },
        },
    };
    // SAFETY: a single well-formed INPUT struct; SendInput reads exactly one element.
    unsafe {
        SendInput(&[input], std::mem::size_of::<INPUT>() as i32);
    }
}

#[cfg(not(windows))]
fn inject_chord(_mods: &[u16], _main: u16, _held: &[u16]) {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn digits_are_positional_never_shifted() {
        // Mirror of capture (keymap.rs): top-row digit token -> VK 0x30..0x39, no Shift.
        // Guards the AZERTY regression where VkKeyScanW('3') sets needs_shift=true.
        assert_eq!(resolve_key_vk("0"), Some((0x30, false)));
        assert_eq!(resolve_key_vk("3"), Some((0x33, false)));
        assert_eq!(resolve_key_vk("9"), Some((0x39, false)));
    }

    #[test]
    fn named_and_function_keys_unaffected() {
        assert_eq!(resolve_key_vk("space"), Some((0x20, false)));
        assert_eq!(resolve_key_vk("f1"), Some((0x70, false)));
        assert_eq!(resolve_key_vk("f12"), Some((0x7B, false)));
    }

    const CTRL: u16 = 0x11;
    const ALT: u16 = 0x12;
    const SHIFT: u16 = 0x10;

    #[test]
    fn chord_plan_held_equals_target_touches_nothing() {
        // ctrl+alt+q triggering ctrl+alt+3: the user's own ctrl+alt serve the chord — just
        // tap the main key, no modifier flapping.
        assert_eq!(chord_plan(&[CTRL, ALT], &[CTRL, ALT]), (vec![], vec![]));
    }

    #[test]
    fn chord_plan_disjoint_lifts_and_presses() {
        // shift held, target needs ctrl: lift shift, press ctrl.
        assert_eq!(chord_plan(&[CTRL], &[SHIFT]), (vec![SHIFT], vec![CTRL]));
    }

    #[test]
    fn chord_plan_partial_overlap() {
        // ctrl+shift held, target ctrl+alt: ctrl stays down, shift lifted, alt pressed.
        assert_eq!(chord_plan(&[CTRL, ALT], &[CTRL, SHIFT]), (vec![SHIFT], vec![ALT]));
    }

    #[test]
    fn chord_plan_nothing_held_presses_all() {
        assert_eq!(chord_plan(&[CTRL, ALT], &[]), (vec![], vec![CTRL, ALT]));
    }
}
