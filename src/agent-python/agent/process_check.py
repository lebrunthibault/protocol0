"""Détecte si un process Ableton Live tourne (n'importe où, pas seulement au premier plan).

Sert à /status (page web + systray) à distinguer "Ableton pas lancé" de "Ableton lancé mais
control surface pas activée". Spécifique Windows ; stub macOS à venir (équivalent : NSWorkspace
.runningApplications filtré sur le bundle id com.ableton.live).

Règle de match critique : l'exe Ableton est `Ableton Live <N> <Edition>.exe` (varie par
version ET édition -> jamais matcher le nom complet). On matche le préfixe
"ableton live " AVEC l'espace final : ça couvre toutes les éditions/versions tout en
excluant `Ableton Index.exe` (l'indexeur de bibliothèque, qui tourne en parallèle).

Stdlib uniquement (pas de psutil) : l'exe gelé doit rester léger et son profil minimal.
"""
import csv
import logging
import subprocess
from typing import Iterable

logger = logging.getLogger("agent")

# Préfixe AVEC espace final : exclut "Ableton Index.exe" et un éventuel "Ableton Live.exe"
# sans suffixe d'édition (jamais observé, mais on reste strict).
_ABLETON_EXE_PREFIX = "ableton live "

# CREATE_NO_WINDOW : pas de flash de console quand l'exe gelé (no-console) spawn tasklist.
_CREATE_NO_WINDOW = 0x08000000


def matches_ableton(image_name: str) -> bool:
    """Vrai si le nom d'image (basename, ex. 'Ableton Live 12 Suite.exe') est le DAW."""
    return image_name.strip().lower().startswith(_ABLETON_EXE_PREFIX)


def _image_names(tasklist_csv: str) -> Iterable[str]:
    """Extrait la colonne 0 (nom d'image) de la sortie `tasklist /FO CSV /NH`."""
    for row in csv.reader(tasklist_csv.splitlines()):
        if row:
            yield row[0]


def ableton_is_running() -> bool:
    try:
        out = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=_CREATE_NO_WINDOW,
        ).stdout
    except (OSError, subprocess.SubprocessError) as e:
        logger.warning("tasklist failed: %s" % e)
        return False
    return any(matches_ableton(name) for name in _image_names(out))
