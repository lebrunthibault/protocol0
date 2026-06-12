//! Canonical key vocabulary shared by the listener (capture) and the emitter (injection) —
//! mirror of agent/keymap.py.
//!
//! The canonical combo format is the contract between three places that MUST stay in
//! lock-step (proto spec, parity invariant):
//!   - the agent listener (capture), which matches on the physical `vk`;
//!   - the frontend capture (useComboCapture.ts), which matches on event.code;
//!   - the agent emitter (key_emitter.rs), which turns a combo back into key events.
//!
//! Canonical form: lowercase, modifiers in the fixed order ctrl, alt, shift, win, then the
//! main key, joined by '+'. Ex. "ctrl+n", "ctrl+shift+f5", "ctrl+alt+space".
//!
//! Namespace: a-z, 0-9, f1-f12, a set of named non-character keys (space, tab, enter, esc,
//! backspace, delete, arrows, home/end, page up/down), and a small set of punctuation glyphs
//! (see PUNCTUATION) needed by native Live shortcuts like Ctrl+, (Settings) or Ctrl+[ / Ctrl+]
//! (browser history). Punctuation is named layout-aware by its UNSHIFTED glyph, like letters.

/// Fixed modifier order in the canonical combo string.
pub const MODIFIER_ORDER: [&str; 4] = ["ctrl", "alt", "shift", "win"];

/// Punctuation glyphs admitted into the canonical namespace. Kept deliberately small: only the
/// keys some native Live shortcut needs. Named by glyph (layout-aware, like a-z), so a combo
/// stores the character the key produces unshifted on the current layout.
pub const PUNCTUATION: [char; 5] = [',', '[', ']', '=', '-'];

/// Virtual-key code -> canonical modifier token. Generic + left/right variants all collapse
/// to the same token (the canonical form has no left/right distinction).
pub fn modifier_token(vk: u32) -> Option<&'static str> {
    Some(match vk {
        0x11 | 0xA2 | 0xA3 => "ctrl", // VK_CONTROL / L / R
        0x12 | 0xA4 | 0xA5 => "alt",  // VK_MENU / L / R (AltGr -> alt)
        0x10 | 0xA0 | 0xA1 => "shift", // VK_SHIFT / L / R
        0x5B | 0x5C => "win",          // VK_LWIN / VK_RWIN
        _ => return None,
    })
}

/// Virtual-key code -> canonical named-key token. Same namespace as the emitter's named keys,
/// keyed by vk. F1-F12 (0x70-0x7B) are handled in key_name_from_vk.
fn named_token(vk: u32) -> Option<&'static str> {
    Some(match vk {
        0x20 => "space",
        0x09 => "tab",
        0x0D => "enter",
        0x1B => "esc",
        0x08 => "backspace",
        0x2E => "delete",
        0x26 => "up",
        0x28 => "down",
        0x25 => "left",
        0x27 => "right",
        0x24 => "home",
        0x23 => "end",
        0x21 => "pageup",
        0x22 => "pagedown",
        _ => return None,
    })
}

/// Canonical name of a non-modifier key from its virtual-key + scan code.
///
/// Layout-aware for letters (Q -> "q" on AZERTY) via ToUnicodeEx; positional for everything
/// else (digits, numpad, function keys, named keys). Returns None if the key is outside the
/// canonical namespace.
pub fn key_name_from_vk(vk: u32, scan: u32) -> Option<String> {
    if let Some(glyph) = layout_glyph(vk, scan) {
        return Some(glyph.to_string());
    }
    if (0x70..=0x7B).contains(&vk) {
        // VK_F1..VK_F12
        return Some(format!("f{}", vk - 0x6F));
    }
    if (0x30..=0x39).contains(&vk) {
        // '0'..'9' top row
        return char::from_u32(vk).map(|c| c.to_string());
    }
    if (0x60..=0x69).contains(&vk) {
        // numpad 0..9
        return char::from_u32(vk - 0x30).map(|c| c.to_string());
    }
    if let Some(named) = named_token(vk) {
        return Some(named.to_string());
    }
    if (0x41..=0x5A).contains(&vk) {
        // A-Z positional fallback (ToUnicodeEx unavailable)
        return char::from_u32(vk + 0x20).map(|c| c.to_string());
    }
    None
}

/// Layout-aware unmodified glyph for a physical key via ToUnicodeEx: a lowercase letter 'a'..'z'
/// or one of the whitelisted PUNCTUATION glyphs, else None.
///
/// Translates against a ZEROED key-state buffer so no held modifier influences the result:
/// Ctrl+E yields 'e' (not '\x05'), Ctrl+, yields ',', and AltGr letters don't turn into
/// punctuation. The zeroed state also means we get the UNSHIFTED glyph (',' not '<', '=' not
/// '+'), which is exactly the canonical name. Anything outside a-z + PUNCTUATION (digits,
/// dead keys, accented results) falls through to positional mapping. Mirror of
/// keymap.py::_layout_letter, widened to the punctuation namespace.
#[cfg(windows)]
fn layout_glyph(vk: u32, scan: u32) -> Option<char> {
    use windows::Win32::UI::Input::KeyboardAndMouse::{GetKeyboardLayout, ToUnicodeEx};

    // SAFETY: GetKeyboardLayout(0) gets the calling thread's layout; ToUnicodeEx writes at
    // most `buf.len()` UTF-16 units into our stack buffer. The key-state array is fully
    // initialized to zero (no modifier active), as the Python code does.
    //
    // wFlags bit 2 (0x4, Win10 1607+) = "do not change keyboard state". CRITICAL: without it,
    // this call — made by the hook for every keypress, BEFORE the foreground app translates
    // it — mutates the kernel's shared dead-key state. Pressing a dead key (e.g. '^' on
    // AZERTY) would leave a pending dead-key from our translation, and the app's own
    // translation of the same keystroke then sees pending '^' + new '^' -> doubled '^^'.
    unsafe {
        let layout = GetKeyboardLayout(0);
        let state = [0u8; 256];
        let mut buf = [0u16; 8];
        let n = ToUnicodeEx(vk, scan, &state, &mut buf, 0x4, layout);
        if n == 1 {
            let ch = char::from_u32(buf[0] as u32)?.to_ascii_lowercase();
            if ch.is_ascii_lowercase() || PUNCTUATION.contains(&ch) {
                return Some(ch);
            }
        }
    }
    None
}

/// Non-Windows stub: no layout translation (positional mapping covers A-Z). Lets the pure
/// logic (and its tests) compile off-Windows; the real agent is Windows-only for now.
#[cfg(not(windows))]
fn layout_glyph(_vk: u32, _scan: u32) -> Option<char> {
    None
}

#[cfg(test)]
mod tests {
    //! vk-based vocabulary used by the low-level hook (capture side). Mirror of test_keymap_vk.py.
    use super::*;

    #[test]
    fn positional_names() {
        // scan is irrelevant for non-letters; layout_glyph returns no glyph so we fall back.
        let cases = [
            (0x31, "1"),   // '1' top row
            (0x39, "9"),   // '9'
            (0x60, "0"),   // numpad 0
            (0x69, "9"),   // numpad 9
            (0x70, "f1"),  // VK_F1
            (0x7B, "f12"), // VK_F12
            (0x20, "space"),
            (0x0D, "enter"),
            (0x1B, "esc"),
            (0x25, "left"),
            (0x21, "pageup"),
        ];
        for (vk, expected) in cases {
            assert_eq!(key_name_from_vk(vk, 0).as_deref(), Some(expected), "vk {vk:#x}");
        }
    }

    #[test]
    fn unknown_vk_is_none() {
        assert_eq!(key_name_from_vk(0x01, 0), None); // VK_LBUTTON, outside namespace
    }

    #[test]
    fn letter_positional_fallback() {
        // On a non-Windows test host layout_glyph is a no-op -> positional A-Z mapping:
        // vk 0x45 -> 'e', vk 0x55 -> 'u'. (On Windows ToUnicodeEx yields the same on QWERTY.)
        #[cfg(not(windows))]
        {
            assert_eq!(key_name_from_vk(0x45, 0).as_deref(), Some("e"));
            assert_eq!(key_name_from_vk(0x55, 0).as_deref(), Some("u"));
        }
    }

    #[test]
    fn punctuation_namespace() {
        // The punctuation glyphs admitted into the namespace. Resolved layout-aware via
        // ToUnicodeEx at capture time (Windows), so the positional fallback can't be exercised
        // off-Windows — assert the whitelist itself, the contract the emitter mirrors.
        assert_eq!(PUNCTUATION, [',', '[', ']', '=', '-']);
    }

    #[test]
    fn modifier_vk_collapses_left_right() {
        assert_eq!(modifier_token(0xA2), Some("ctrl")); // LCONTROL
        assert_eq!(modifier_token(0xA3), Some("ctrl")); // RCONTROL
        assert_eq!(modifier_token(0xA5), Some("alt")); // RMENU / AltGr
        assert_eq!(modifier_token(0x5B), Some("win")); // LWIN
        assert_eq!(modifier_token(0x55), None); // 'u' is not a modifier
    }
}
