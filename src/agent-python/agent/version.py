"""Version du projet, lue depuis le fichier `VERSION` à la racine du repo.

Source de vérité unique (bumpée par le skill /commit). Résolution robuste car les
paquets tournent depuis des contextes différents : exe gelé (PyInstaller) -> VERSION
embarqué lu via sys._MEIPASS ; sinon (poetry run / sources) on remonte depuis __file__
jusqu'à trouver VERSION à la racine du repo.
"""
import sys
from pathlib import Path


def _read_version() -> str:
    # 1) exe gelé (PyInstaller) : VERSION embarqué à côté du binaire.
    base = getattr(sys, "_MEIPASS", None)
    if base:
        f = Path(base) / "VERSION"
        if f.exists():
            return f.read_text(encoding="utf-8").strip()
    # 2) depuis les sources : remonte jusqu'à trouver VERSION à la racine du repo.
    for parent in Path(__file__).resolve().parents:
        f = parent / "VERSION"
        if f.exists():
            return f.read_text(encoding="utf-8").strip()
    return "0.0.0"  # dernier recours


__version__ = _read_version()
