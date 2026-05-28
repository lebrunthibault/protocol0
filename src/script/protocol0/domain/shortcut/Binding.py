"""Un binding raccourci → action, côté script.

Miroir de detector.config.Binding (même schéma JSON), mais ici en dataclass
avec (de)sérialisation : le script écrit ce JSON, le détecteur le lit.

Format de combo canonique (partagé détecteur ↔ frontend ↔ config) : minuscules,
modificateurs dans l'ordre fixe ctrl, alt, shift, win, puis la touche, joints
par '+'. Ex. "ctrl+alt+e". Le script ne valide pas le combo (le frontend le
produit déjà au bon format via e.code) ; il le stocke tel quel.
"""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Binding:
    combo: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {"combo": self.combo, "action": self.action, "params": self.params}

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Binding":
        return cls(
            combo=raw["combo"],
            action=raw["action"],
            params=raw.get("params", {}),
        )
