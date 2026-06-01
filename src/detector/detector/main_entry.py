"""Point d'entrée gelé par PyInstaller.

PyInstaller a besoin d'un vrai script module-level comme cible : le console-script
Poetry (`detector = "detector.main:start"`) ne lui est pas utilisable. Ce module ne
fait que déléguer à detector.main.start.
"""
from detector.main import start

if __name__ == "__main__":
    start()
