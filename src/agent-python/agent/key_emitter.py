"""Local keystroke injection: turn a canonical combo back into real key events.

This is the execution side of a `send_keys` binding: pressing the user's combo
(e.g. ctrl+alt+q) makes the agent emit a native Ableton shortcut (e.g. ctrl+n) into
the foreground window. Unlike every other action, this does NOT go through the
script's HTTP API — most native Live commands have no LOM equivalent, so we replay
the keystroke locally with pynput's Controller.

Injection order is a chord, not a sequence: press modifiers, tap the main key,
release modifiers (in reverse). The agent's own listener ignores these synthesized
keys because the low-level hook sees the Windows LLKHF_INJECTED flag on SendInput
events, so a binding can't re-trigger itself.

Held-modifier neutralisation: the trigger combo's modifiers are usually still
physically down when we inject (e.g. the user holds ctrl+alt and taps the trigger
key). If we just injected the target chord, the OS would see the user's ctrl+alt
PLUS our keys -> the wrong shortcut. So we release the user's held modifiers first,
inject the clean target chord, then re-press whatever the user still holds.

The trigger's MAIN key needs no such handling: the listener's low-level hook
suppresses the physical trigger event, so the foreground app never sees the trigger
key at all (no leak to compensate for).

Combo vocabulary is the shared `keymap` (same tokens the listener captures), so what
the UI records is exactly what we replay.
"""
import logging

from pynput import keyboard

from agent import keymap

logger = logging.getLogger("agent")

_controller = keyboard.Controller()

# Canonical modifier token -> pynput Key for injection (one Key per token; left/right
# variants collapse to the generic one).
_MODIFIER_TO_PYNPUT = {
    "ctrl": keyboard.Key.ctrl,
    "alt": keyboard.Key.alt,
    "shift": keyboard.Key.shift,
    "win": keyboard.Key.cmd,
}


def _resolve_key(token: str):
    """Canonical main-key token -> a pynput-pressable key (char str or Key), or None."""
    if len(token) == 1 and (token.isalpha() or token.isdigit()):
        return token  # 'a'..'z', '0'..'9' -> press the character
    if len(token) >= 2 and token[0] == "f" and token[1:].isdigit():
        n = int(token[1:])
        if 1 <= n <= 12:
            return getattr(keyboard.Key, "f%d" % n)
        return None
    return keymap.NAMED_TO_PYNPUT.get(token)


def send(combo: str, held_modifiers=()) -> None:
    """Inject the canonical combo as a key chord. No-op (with a warning) if the combo
    can't be parsed into known tokens.

    `held_modifiers` are the canonical modifiers the user currently holds physically
    (from the listener). They are released before the injection and re-pressed after,
    so the target chord lands clean regardless of what triggered it.
    """
    parts = [p for p in combo.split("+") if p]
    if not parts:
        logger.warning("send_keys: empty combo")
        return
    *mod_tokens, key_token = parts

    mods = []
    for m in mod_tokens:
        key = _MODIFIER_TO_PYNPUT.get(m)
        if key is None:
            logger.warning("send_keys: unknown modifier %r in %r" % (m, combo))
            return
        mods.append(key)

    main = _resolve_key(key_token)
    if main is None:
        logger.warning("send_keys: unsupported key %r in %r" % (key_token, combo))
        return

    # Real modifiers to temporarily lift (only ones we know how to press back).
    held = [
        _MODIFIER_TO_PYNPUT[m] for m in held_modifiers if m in _MODIFIER_TO_PYNPUT
    ]

    # 1) lift the user's held modifiers so they don't pollute the target chord.
    for m in held:
        _controller.release(m)
    try:
        # 2) inject the clean target chord.
        for m in mods:
            _controller.press(m)
        try:
            _controller.press(main)
            _controller.release(main)
        finally:
            for m in reversed(mods):
                _controller.release(m)
    finally:
        # 3) restore the modifiers the user is still holding.
        for m in held:
            _controller.press(m)
