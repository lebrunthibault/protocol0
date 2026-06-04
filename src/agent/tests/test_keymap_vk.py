"""vk-based vocabulary used by the low-level hook (capture side)."""
import pytest

from agent import keymap


@pytest.mark.parametrize(
    "vk,expected",
    [
        (0x31, "1"),     # '1' top row
        (0x39, "9"),     # '9'
        (0x60, "0"),     # numpad 0
        (0x69, "9"),     # numpad 9
        (0x70, "f1"),    # VK_F1
        (0x7B, "f12"),   # VK_F12
        (0x20, "space"),
        (0x0D, "enter"),
        (0x1B, "esc"),
        (0x25, "left"),
        (0x21, "pageup"),
    ],
)
def test_positional_names(vk, expected):
    # scan is irrelevant for non-letters; ToUnicodeEx returns no letter so we fall back.
    assert keymap.key_name_from_vk(vk, 0) == expected


def test_unknown_vk_is_none():
    assert keymap.key_name_from_vk(0x01, 0) is None  # VK_LBUTTON, outside namespace


def test_letter_layout_aware_via_seam(monkeypatch):
    # Simulate AZERTY: the Q-position vk resolves to 'q' through ToUnicodeEx.
    monkeypatch.setattr(keymap, "_layout_letter", lambda vk, scan: "q")
    assert keymap.key_name_from_vk(0x41, 0) == "q"


def test_letter_positional_fallback_when_layout_unavailable(monkeypatch):
    # ToUnicodeEx unavailable/anomalous -> positional A-Z mapping (vk 0x45 -> 'e').
    monkeypatch.setattr(keymap, "_layout_letter", lambda vk, scan: None)
    assert keymap.key_name_from_vk(0x45, 0) == "e"


def test_modifier_vk_collapses_left_right():
    assert keymap.MODIFIER_VK[0xA2] == "ctrl"   # LCONTROL
    assert keymap.MODIFIER_VK[0xA3] == "ctrl"   # RCONTROL
    assert keymap.MODIFIER_VK[0xA5] == "alt"    # RMENU / AltGr
