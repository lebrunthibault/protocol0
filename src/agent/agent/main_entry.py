"""Point d'entrée gelé par PyInstaller.

PyInstaller a besoin d'un vrai script module-level comme cible : le console-script
Poetry (`agent = "agent.main:start"`) ne lui est pas utilisable. Ce module ne
fait que déléguer à agent.main.start.
"""
from agent.main import start

if __name__ == "__main__":
    start()
