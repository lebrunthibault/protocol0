"""Liste les process detector en cours et les tue (target `make kill-detector`).

Pourquoi : le bug "un raccourci charge plusieurs devices" venait de DEUX detectors tournant
en parallele (cf. docs/debug-double-shortcut.md). Le mutex single-instance couvre la tache
planifiee, mais des lancements manuels en mode source (`poetry run detector` / `make detector`)
laisses en arriere-plan peuvent coexister. Cette cible nettoie tout d'un coup.

Couvre les deux formes du detector :
  1. l'exe gele packagee : `protocol0-detector.exe` ;
  2. le mode source : `python.exe` dont la ligne de commande lance `detector.main`
     (via `poetry run detector` -> console-script -> `import_module('detector.main')`).

Stdlib uniquement, Windows-only (comme process_check.py). On lit les lignes de commande via
PowerShell `Get-CimInstance` (present sur Win10/11 ; `wmic` est deprecie/absent sur Win11
recent) et on tue via `taskkill`. S'exclut lui-meme du massacre (ce script tourne aussi sous
python et contient "detector" dans son chemin).
"""
import json
import os
import subprocess
import sys

# CREATE_NO_WINDOW : pas de flash de console quand on spawn powershell/taskkill.
_CREATE_NO_WINDOW = 0x08000000

_FROZEN_EXE = "protocol0-detector.exe"
# Marqueur de la forme "mode source" : la console-script poetry re-exec dans
# `import_module('detector.main')`. On matche cette signature precise plutot que le simple
# mot "detector" (qui matcherait ce script lui-meme, ou un editeur ouvert sur le repo).
_SOURCE_MARKER = "detector.main"

# Recupere PID/Name/CommandLine en JSON. ConvertTo-Json sort un objet seul (pas un tableau)
# quand il n'y a qu'un resultat -> on force [array] avec @(...) pour un parsing uniforme.
_PS_SCRIPT = (
    "@(Get-CimInstance Win32_Process | "
    "Select-Object ProcessId,Name,CommandLine) | ConvertTo-Json -Compress"
)


def _processes():
    """[(pid, name, commandline)] de tous les process, via PowerShell. [] si echec."""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS_SCRIPT],
            capture_output=True,
            text=True,
            timeout=20,
            creationflags=_CREATE_NO_WINDOW,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    try:
        data = json.loads(out) if out.strip() else []
    except json.JSONDecodeError:
        return []
    rows = []
    for p in data:
        pid = p.get("ProcessId")
        if pid is None:
            continue
        rows.append((int(pid), p.get("Name") or "", p.get("CommandLine") or ""))
    return rows


def _find_detectors():
    """[(pid, label)] des process detector, en excluant ce script."""
    me = os.getpid()
    found = []
    for pid, name, cmd in _processes():
        if pid == me:
            continue
        low_name = name.lower()
        if low_name == _FROZEN_EXE:
            found.append((pid, "%s (frozen exe)" % name))
        elif _SOURCE_MARKER in cmd and "kill_detector" not in cmd:
            found.append((pid, "%s (source: %s)" % (name, _SOURCE_MARKER)))
    return found


def _kill(pid):
    subprocess.run(
        ["taskkill", "/PID", str(pid), "/F"],
        capture_output=True,
        text=True,
        timeout=10,
        creationflags=_CREATE_NO_WINDOW,
    )


def main():
    if sys.platform != "win32":
        print("kill-detector: Windows-only for now (no-op on this platform).")
        return 0
    detectors = _find_detectors()
    if not detectors:
        print("No detector process running.")
        return 0
    print("Found %d detector process(es):" % len(detectors))
    for pid, label in detectors:
        print("  PID %d  %s" % (pid, label))
    print("Killing...")
    for pid, label in detectors:
        _kill(pid)
        print("  killed PID %d" % pid)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
