"""Lecture/écriture de la config des bindings, côté script.

Le frontend (M3) appelle ce service pour lister et ajouter des bindings ;
le détecteur lit le même fichier (detector.config). Contrat partagé :

  %APPDATA%\\Protocol0\\shortcuts.json
  { "version": 1, "bindings": [
      { "combo": "ctrl+alt+e", "action": "load_device", "params": {"name": "EQ Eight"} }
  ] }

Stdlib only (contrainte env Ableton). Tolérant en lecture (jamais d'exception
au runtime : enveloppe vide si absent/corrompu), atomique en écriture (write
tmp + os.replace) pour que le détecteur ne lise jamais un fichier à moitié écrit.
"""
import json
import os
from typing import List

from protocol0.domain.shortcut.Binding import Binding

_VERSION = 1


def config_path() -> str:
    # Même chemin que detector.config.config_path() — contrat de couplage.
    return os.path.join(os.environ["APPDATA"], "Protocol0", "shortcuts.json")


class ShortcutConfigService(object):
    def __init__(self) -> None:
        self._path = config_path()

    def __repr__(self) -> str:
        return "ShortcutConfigService"

    def list(self) -> List[Binding]:
        """Bindings courants. [] si fichier absent/vide/corrompu."""
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return []
        bindings = []
        for raw in data.get("bindings", []):
            if raw.get("combo") and raw.get("action"):
                bindings.append(Binding.from_dict(raw))
        return bindings

    def upsert(self, binding: Binding) -> List[Binding]:
        """Ajoute le binding, ou remplace celui de même combo. Persiste, renvoie
        la liste résultante. Clé = combo (un combo ne déclenche qu'une action),
        cohérent avec le dédup par combo du détecteur (config._by_combo)."""
        bindings = [b for b in self.list() if b.combo != binding.combo]
        bindings.append(binding)
        self._save(bindings)
        return bindings

    def _save(self, bindings: List[Binding]) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        payload = {"version": _VERSION, "bindings": [b.to_dict() for b in bindings]}
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self._path)
