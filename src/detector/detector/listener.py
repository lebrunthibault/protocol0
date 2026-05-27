"""Écoute clavier (pynput) → résolution combo → appel HTTP au script.

Tourne sous Python système (pynput dispo, contrairement à l'env Ableton).
Sur une frappe non-modificateur, construit la combo canonique à partir des
modificateurs courants + la touche, la cherche dans la config, et — si Ableton
est au premier plan — appelle l'action via l'API HTTP du script.

Format de combo canonique (partagé avec le frontend et la config) : minuscules,
modificateurs dans l'ordre fixe ctrl, alt, shift, win, puis la touche, joints
par '+'. Ex. "ctrl+alt+e", "ctrl+shift+f5". Namespace proto : a-z, 0-9, f1-f12.
"""
import logging
from typing import Optional, Set

from pynput import keyboard

from detector.config import ShortcutConfig
from detector.foreground import ableton_is_foreground

logger = logging.getLogger("detector")

_MODIFIER_ORDER = ["ctrl", "alt", "shift", "win"]

# pynput Key -> nom de modificateur canonique
_MODIFIER_KEYS = {
    keyboard.Key.ctrl: "ctrl",
    keyboard.Key.ctrl_l: "ctrl",
    keyboard.Key.ctrl_r: "ctrl",
    keyboard.Key.alt: "alt",
    keyboard.Key.alt_l: "alt",
    keyboard.Key.alt_r: "alt",
    keyboard.Key.alt_gr: "alt",
    keyboard.Key.shift: "shift",
    keyboard.Key.shift_l: "shift",
    keyboard.Key.shift_r: "shift",
    keyboard.Key.cmd: "win",
    keyboard.Key.cmd_l: "win",
    keyboard.Key.cmd_r: "win",
}


def _key_name(key: object) -> Optional[str]:
    """Nom canonique d'une touche non-modificateur, ou None si hors namespace.

    On mappe par `vk` (virtual-key code = position physique), pas par `char` :
    sous un modificateur, `char` devient un control char (Ctrl+E -> '\\x05') ou
    un caractère AltGr (Ctrl+Alt+E -> '€' en AZERTY), alors que `vk` reste stable
    (E -> 69) quel que soit le modificateur ou le layout. Cf. plan : nom de touche
    par position physique, des deux côtés (ici vk, côté navigateur e.code).
    """
    vk = getattr(key, "vk", None)
    if vk is not None:
        if 65 <= vk <= 90:  # A-Z
            return chr(vk + 32)  # -> 'a'..'z'
        if 48 <= vk <= 57:  # 0-9 (rangée du haut)
            return chr(vk)
        if 96 <= vk <= 105:  # pavé numérique 0-9
            return chr(vk - 48)
        return None
    # Touches de fonction : pynput livre un Key (ex Key.f5), sans vk utile.
    name = getattr(key, "name", None)
    if name and len(name) >= 2 and name[0] == "f" and name[1:].isdigit():
        n = int(name[1:])
        if 1 <= n <= 12:
            return name
    return None


class ShortcutListener:
    def __init__(self, config: ShortcutConfig, on_action) -> None:
        self._config = config
        self._on_action = on_action
        self._pressed_modifiers: Set[str] = set()
        self._listener: Optional[keyboard.Listener] = None

    def start(self) -> None:
        self._listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self._listener.start()
        logger.info("keyboard listener started")

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def join(self) -> None:
        if self._listener is not None:
            self._listener.join()

    def _on_press(self, key: object) -> None:
        mod = _MODIFIER_KEYS.get(key)
        if mod is not None:
            self._pressed_modifiers.add(mod)
            return
        self._handle_main_key(key)

    def _on_release(self, key: object) -> None:
        mod = _MODIFIER_KEYS.get(key)
        if mod is not None:
            self._pressed_modifiers.discard(mod)

    def _handle_main_key(self, key: object) -> None:
        name = _key_name(key)
        if name is None:
            return
        combo = self._build_combo(name)
        self._config.reload_if_changed()
        binding = self._config.get(combo)
        if binding is None:
            return
        if not ableton_is_foreground():
            logger.info("combo %s ignored (Ableton not foreground)" % combo)
            return
        logger.info("combo %s -> %s %s" % (combo, binding.action, binding.params))
        try:
            self._on_action(binding)
        except Exception as e:
            logger.warning("action %s failed: %s" % (binding.action, e))

    def _build_combo(self, key_name: str) -> str:
        mods = [m for m in _MODIFIER_ORDER if m in self._pressed_modifiers]
        return "+".join(mods + [key_name])
