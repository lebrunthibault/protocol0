"""Réglages runtime de l'agent.

L'agent est distribué comme exe autonome (PyInstaller), sans .env à côté.

Le port du script n'est plus câblé : le script le choisit dynamiquement et publie son
URL effective dans runtime.json (cf. runtime_state). On découvre donc l'URL à l'exécution.
P0_SCRIPT_PORT reste un escape hatch manuel : s'il est défini, il force l'URL et
court-circuite runtime.json (cas avancés / dev).
"""
import os
from typing import Optional

# Port fixe du serveur "launcher" servi par l'agent (page de diagnostic + redirection
# vers l'UI du script). Câblé en dur car le raccourci Windows (.url) pointe dessus et doit
# rester bookmarkable -> pas de fallback dynamique côté launcher. DOIT correspondre à l'URL
# du raccourci dans installer/protocol0.iss.
LAUNCHER_PORT = 9010


class Settings:
    def __init__(self) -> None:
        self._override_port: Optional[int] = (
            int(os.environ["P0_SCRIPT_PORT"]) if "P0_SCRIPT_PORT" in os.environ else None
        )

    @property
    def override_url(self) -> Optional[str]:
        """URL forcée via P0_SCRIPT_PORT, ou None pour découverte dynamique."""
        if self._override_port is None:
            return None
        return "http://127.0.0.1:%d" % self._override_port
