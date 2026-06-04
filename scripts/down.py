"""Arrete le stack dev lance par `make up` (target `make down`).

Lit les PID memorises dans %APPDATA%\\Protocol0\\dev-up.json (ecrit par scripts/up.py) et tue
chaque arbre de process avec `taskkill /T` (les services tournent via un shell qui spawn
node/poetry en enfants -> il faut tuer l'arbre, pas juste le shell parent). En filet de
securite on rappelle kill_agent pour les agents qui auraient survecu.

Stdlib uniquement, Windows-only. Idempotent : pas de dev-up.json -> juste le filet de securite.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import kill_agent

_CREATE_NO_WINDOW = 0x08000000
_REPO = Path(__file__).resolve().parent.parent


def _state_file() -> Path:
    return Path(os.environ["APPDATA"]) / "Protocol0" / "dev-up.json"


def _kill_tree(pid: int) -> None:
    # /T : l'arbre entier (enfants node/poetry) ; /F : force.
    subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        capture_output=True,
        text=True,
        timeout=15,
        creationflags=_CREATE_NO_WINDOW,
    )


def main() -> int:
    if sys.platform != "win32":
        print("make down: Windows-only.")
        return 0

    state = _state_file()
    if state.exists():
        try:
            pids = json.loads(state.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pids = {}
        if pids:
            print("Stopping dev stack:")
            for label, pid in pids.items():
                _kill_tree(int(pid))
                print("  %-9s PID %s  killed" % (label, pid))
        state.unlink(missing_ok=True)
    else:
        print("No dev-up.json (nothing recorded). Cleaning up agents anyway.")

    # Filet de securite : tue tout agent qui aurait survecu (exe gele ou mode source) et
    # tout vite/live-server de CE repo qui traine (lancement manuel ou PID hors dev-up.json).
    # On exige le chemin du repo dans la cmdline pour ne jamais tuer un vite d'IDE / autre projet.
    kill_agent.main()
    repo = str(_REPO).lower()
    for pid, _name, cmd in kill_agent._processes():
        low = cmd.lower()
        if ("vite" in low or "live-server" in low) and repo in low:
            _kill_tree(pid)
            print("  stray web PID %d  killed" % pid)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
