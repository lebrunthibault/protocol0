"""Lecture du fichier d'état runtime publié par le script.

Le script (dans Ableton) écrit %APPDATA%\\Protocol0\\runtime.json avec l'URL effective
de son serveur HTTP (port dynamique), et le supprime à l'arrêt. Côté detector on le lit
pour découvrir le port courant ; l'absence ou la corruption du fichier valent "script
pas actif" (lecture tolérante, jamais d'exception au runtime).
"""
import json
import os
from typing import Optional


def runtime_path() -> str:
    return os.path.join(os.environ["APPDATA"], "Protocol0", "runtime.json")


def read() -> Optional[dict]:
    """Renvoie le payload (script_url, pid, version) ou None si absent/corrompu/invalide."""
    try:
        with open(runtime_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    url = data.get("script_url")
    if not isinstance(url, str) or not url:
        return None
    return data
