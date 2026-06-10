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
/// Letters/digits/punctuation go through VkKeyScanW so they land correctly regardless of layout
/// (mirrors pynput pressing the character). f1..f12 and named keys map positionally and never
/// need Shift. The `needs_shift` flag matters for glyphs the layout produces only with Shift
/// (e.g. '+' on US is Shift+'='): the canonical namespace names keys by their unshifted glyph,
/// but a future shifted glyph would still inject correctly.
fn resolve_key_vk(token: &str) -> Option<(u16, bool)> {
    let chars: Vec<char> = token.chars().collect();
    if chars.len() == 1
        && (chars[0].is_ascii_alphabetic()
            || chars[0].is_ascii_digit()
            || keymap::PUNCTUATION.contains(&chars[0]))
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
/// listener). They are released before the injection and re-pressed after, so the target chord
/// lands clean regardless of what triggered it.
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

    // Real modifiers to temporarily lift (only ones we know how to press back).
    let held: Vec<u16> = held_modifiers
        .iter()
        .filter_map(|m| modifier_vk(m))
        .collect();

    inject_chord(&mods, main, &held);
}

/// 1) lift the user's held modifiers; 2) inject the clean target chord; 3) restore the held
/// modifiers. Centralizes the SendInput calls.
#[cfg(windows)]
fn inject_chord(mods: &[u16], main: u16, held: &[u16]) {
    // 1) lift the user's held modifiers so they don't pollute the target chord.
    for &m in held {
        key_event(m, true);
    }
    // 2) inject the clean target chord: press mods, tap main, release mods in reverse.
    for &m in mods {
        key_event(m, false);
    }
    key_event(main, false);
    key_event(main, true);
    for &m in mods.iter().rev() {
        key_event(m, true);
    }
    // 3) restore the modifiers the user is still holding.
    for &m in held {
        key_event(m, false);
    }
}

/// Sends one key down/up event via SendInput.
#[cfg(windows)]
fn key_event(vk: u16, up: bool) {
    use windows::Win32::UI::Input::KeyboardAndMouse::{
        SendInput, INPUT, INPUT_0, INPUT_KEYBOARD, KEYBDINPUT, KEYBD_EVENT_FLAGS, KEYEVENTF_KEYUP,
        VIRTUAL_KEY,
    };

    let flags = if up {
        KEYEVENTF_KEYUP
    } else {
        KEYBD_EVENT_FLAGS(0)
    };
    let input = INPUT {
        r#type: INPUT_KEYBOARD,
        Anonymous: INPUT_0 {
            ki: KEYBDINPUT {
                wVk: VIRTUAL_KEY(vk),
                wScan: 0,
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
