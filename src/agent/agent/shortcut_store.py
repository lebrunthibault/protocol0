"""Lecture/écriture de shortcuts.json côté agent (CRUD pour l'API web).

L'agent POSSÈDE désormais l'écriture de la config (avant, c'était le script dans Ableton) :
c'est ce qui permet d'éditer ses raccourcis SANS Ableton. Le listener de l'agent
(agent/config.py) relit le fichier par mtime, donc une écriture ici est prise en compte
au prochain keypress sans plomberie de reload.

Même contrat que l'ex-ShortcutConfigService du script :
    %APPDATA%\\Protocol0\\shortcuts.json
    { "version": 1, "bindings": [ {combo, action, params} ] }

Stdlib only. Tolérant en lecture ([] si absent/corrompu), atomique en écriture
(write tmp + os.replace) pour que le listener ne lise jamais un fichier à moitié écrit.
Clé = combo (un combo ne déclenche qu'une action).
"""
import json
import os
from typing import Dict, List

from agent.config import Binding, config_path

_VERSION = 1


def _load() -> List[Binding]:
    """Bindings courants. [] si fichier absent/vide/corrompu."""
    try:
        with open(config_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    bindings = []
    for raw in data.get("bindings", []):
        combo = raw.get("combo")
        action = raw.get("action")
        if combo and action:
            bindings.append(Binding(combo=combo, action=action, params=raw.get("params", {})))
    return bindings


def _save(bindings: List[Binding]) -> None:
    path = config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "version": _VERSION,
        "bindings": [
            {"combo": b.combo, "action": b.action, "params": b.params} for b in bindings
        ],
    }
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _to_dict(b: Binding) -> Dict[str, object]:
    return {"combo": b.combo, "action": b.action, "params": b.params}


def list_bindings() -> List[Dict[str, object]]:
    return [_to_dict(b) for b in _load()]


def upsert(combo: str, action: str, params: Dict[str, str]) -> List[Dict[str, object]]:
    """Ajoute le binding, ou remplace celui de même combo. Renvoie la liste résultante."""
    bindings = [b for b in _load() if b.combo != combo]
    bindings.append(Binding(combo=combo, action=action, params=params))
    _save(bindings)
    return [_to_dict(b) for b in bindings]


def delete(combo: str) -> List[Dict[str, object]]:
    """Supprime le binding d'une combo (no-op si absent). Renvoie la liste résultante."""
    bindings = [b for b in _load() if b.combo != combo]
    _save(bindings)
    return [_to_dict(b) for b in bindings]
