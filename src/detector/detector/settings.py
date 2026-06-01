"""Réglages runtime du détecteur.

Le détecteur est distribué comme exe autonome (PyInstaller), sans .env à côté :
le port du script a donc un défaut câblé (9000, la valeur dev historique),
surchargeable par la variable d'environnement P0_SCRIPT_PORT pour les cas avancés.
"""
import os

DEFAULT_SCRIPT_PORT = 9000


class Settings:
    def __init__(self) -> None:
        self.p0_script_port = int(os.environ.get("P0_SCRIPT_PORT", DEFAULT_SCRIPT_PORT))

    @property
    def p0_script_url(self) -> str:
        return f"http://127.0.0.1:{self.p0_script_port}"
