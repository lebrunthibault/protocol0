"""Lecture de la config globale des bindings.

Fichier unique à %APPDATA%\\Protocol0\\shortcuts.json (constitution §3.3, §5),
écrit par le frontend servi par le script, lu ici par le détecteur. Stdlib only.

Schéma (enveloppe versionnée) :
    { "version": 1, "bindings": [
        { "combo": "ctrl+alt+e", "action": "load_device", "params": {"name": "EQ Eight"} }
    ] }
"""
import json
import os
from typing import Dict, List, NamedTuple, Optional


class Binding(NamedTuple):
    combo: str
    action: str
    params: Dict[str, str]


def config_path() -> str:
    return os.path.join(os.environ["APPDATA"], "Protocol0", "shortcuts.json")


class ShortcutConfig:
    """Charge les bindings et les recharge quand le fichier change (mtime)."""

    def __init__(self) -> None:
        self._path = config_path()
        self._mtime: Optional[float] = None
        self._by_combo: Dict[str, Binding] = {}
        self.reload()

    def _current_mtime(self) -> Optional[float]:
        try:
            return os.path.getmtime(self._path)
        except OSError:
            return None

    def reload_if_changed(self) -> bool:
        """Relit le fichier si son mtime a changé. Retourne True si rechargé."""
        if self._current_mtime() != self._mtime:
            self.reload()
            return True
        return False

    def reload(self) -> None:
        self._mtime = self._current_mtime()
        self._by_combo = {b.combo: b for b in self._load()}

    def get(self, combo: str) -> Optional[Binding]:
        return self._by_combo.get(combo)

    def _load(self) -> List[Binding]:
        # Tolérant : [] si absent/vide/corrompu (jamais d'exception au runtime).
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return []
        bindings = []
        for raw in data.get("bindings", []):
            combo = raw.get("combo")
            action = raw.get("action")
            if not combo or not action:
                continue
            bindings.append(Binding(combo=combo, action=action, params=raw.get("params", {})))
        return bindings
