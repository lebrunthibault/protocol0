# Loader prod du remote script (déposé tel quel comme __init__.py par l'installeur).
#
# Le remote script est stdlib-only (cf. commit 2d965072) : pas de dépendance tierce à
# vendorer, pas de .venv, pas de réécriture de source. Le paquet protocol0/ est copié
# par l'installeur juste à côté de ce fichier (dans le dossier Protocol_0/).
#
# Ableton charge ce __init__.py mais N'ajoute PAS le dossier Protocol_0/ au sys.path,
# donc `import protocol0` échoue (ModuleNotFoundError) sans l'insert ci-dessous. On
# ajoute donc explicitement le dossier courant au path avant l'import. C'est la version
# prod, minimale, de ce que faisait le __init__.py de dev via __P0_SOURCE_DIR__.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from protocol0.application.main import create_instance  # noqa: E402
